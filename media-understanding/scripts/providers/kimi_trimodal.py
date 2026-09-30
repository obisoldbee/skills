#!/usr/bin/env python3
"""Prepare dense frames + audio + local timestamped ASR, then Kimi M3 AgentSwarm."""
from __future__ import annotations
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import wave

HERE = Path(__file__).resolve().parent


def sha(f):
    h = hashlib.sha256()
    with f.open("rb") as s:
        for b in iter(lambda:s.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def destination(source, explicit=None):
    return Path(explicit).resolve() if explicit else source.parent / ("frames_" + source.stem)


def run(cmd, log=None):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if log: log.write_text(r.stdout + r.stderr)
    if r.returncode: raise RuntimeError("local preparation failed: " + str(cmd[0]))
    return r.stdout


def prepare(source, out, asr_model, whisper, fps=2.0):
    if not math.isfinite(fps) or fps <= 0: raise ValueError("invalid_fps")
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool): raise ValueError("missing_dependency: " + tool)
    source_hash = sha(source)
    probe = json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(source)]))
    if not any(x.get("codec_type")=="video" for x in probe["streams"]): raise ValueError("no_video_stream")
    duration = float(probe["format"]["duration"])
    has_audio = any(x.get("codec_type")=="audio" for x in probe["streams"])
    out.mkdir(parents=True,exist_ok=False)
    images=out/"images";images.mkdir()
    metadata={"source":str(source),"source_sha256":source_hash,"duration":duration,"fps":fps,
              "provider_calls":False,"state":"preparing","audio_stream_present":has_audio,
              "asr_model_path":str(asr_model),"asr_model_sha256":sha(asr_model) if has_audio and asr_model.is_file() else None}
    (out/"preparation.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
    run(["ffmpeg","-v","error","-nostdin","-n","-i",str(source),"-vf",f"fps={fps}:start_time=0","-q:v","2",str(images/"frame_%06d.jpg")],out/"frames-export.log")
    frames=sorted(images.glob("frame_*.jpg"))
    expected=duration*fps
    if not frames or abs(len(frames)-expected)>1: raise ValueError("frame_count_duration_mismatch")
    manifest=[{"path":str(f),"kind":"image","sha256":sha(f),"frame_id":f"F{i+1:06d}","timestamp_seconds":round(i/fps,6)} for i,f in enumerate(frames)]
    (out/"frames.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    transcript_dir=out/"transcript";transcript_dir.mkdir()
    text={"language":None,"text":"","segments":[],"audio_state":"no_audio_stream"}
    if has_audio:
        audio=out/"audio.wav"
        run(["ffmpeg","-v","error","-nostdin","-n","-i",str(source),"-map","0:a:0","-vn","-c:a","pcm_s16le",str(audio)],out/"audio-export.log")
        peak=0
        with wave.open(str(audio),"rb") as w:
            audio_info={"channels":w.getnchannels(),"sample_rate":w.getframerate(),"frames":w.getnframes()}
            while True:
                chunk=w.readframes(65536)
                if not chunk: break
                samples=array.array('h',chunk)
                if sys.byteorder!='little':samples.byteswap()
                peak=max(peak,max(map(abs,samples),default=0))
        audio_info.update(peak_pcm16=peak,sha256=sha(audio))
        (out/"audio-info.json").write_text(json.dumps(audio_info,indent=2))
        carrier=out/"audio-carrier.mp4"
        run(["ffmpeg","-v","error","-nostdin","-n","-f","lavfi","-i","color=c=black:s=640x320:r=3","-i",str(audio),"-shortest","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","64k",str(carrier)],out/"audio-carrier.log")
        manifest.append({"path":str(carrier),"kind":"video","sha256":sha(carrier),"evidence_layer":"audio_carrier_experimental","original_start":0,"original_end":duration,"note":"Black image is artificial. Audio understanding must be distinguished from reading transcript."})
        if peak==0:
            text.update(audio_state="digital_silence",text="",segments=[])
            (transcript_dir/"audio.srt").write_text("")
        else:
            if not asr_model.is_file() or not shutil.which(whisper):
                raise ValueError("missing_local_asr: explicit installed Whisper and cached model required; no automatic download")
            run([whisper,str(audio),"--model",str(asr_model.resolve()),"--device","cpu","--fp16","False","--word_timestamps","True","--output_format","all","--output_dir",str(transcript_dir),"--verbose","False"],out/"asr.log")
            text=json.loads((transcript_dir/"audio.json").read_text())
            text["audio_state"]="asr_candidate_unverified"
    if not has_audio:
        (transcript_dir/"audio.srt").write_text("")
    text.update(source_audio_sha256=sha(out/"audio.wav") if has_audio else None,
                provenance="local Whisper word timestamps; exact digital silence bypasses ASR", acoustic_understanding="not_proven_by_transcript")
    context=out/"timestamped-transcript.json";context.write_text(json.dumps(text,ensure_ascii=False,indent=2))
    manifest.append({"path":str(context),"kind":"text","sha256":sha(context),"evidence_layer":"timestamped_asr"})
    if sha(source)!=source_hash: raise ValueError("source_changed_during_preparation")
    metadata.update(state="prepared",frame_count=len(frames),audio_state=text['audio_state'])
    (out/"preparation.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return metadata


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,help="Default: frames_<video stem> beside the video; must be new")
    p.add_argument("--fps",type=float,default=2.0)
    p.add_argument("--asr-model",type=Path,default=Path.home()/".cache/whisper/base.pt")
    p.add_argument("--whisper",default="whisper")
    p.add_argument("--observers",type=int,default=3)
    p.add_argument("--prompt-file",type=Path)
    p.add_argument("--config",type=Path,default=Path.home()/".kimi-code/config.toml")
    p.add_argument("--execute",action="store_true",help="After local preparation, call MiniMax-M3 through Kimi AgentSwarm")
    a=p.parse_args()
    if not 2<=a.observers<=128:p.error("observers must be 2..128")
    source=a.input.resolve(strict=True);out=destination(source,a.output_dir)
    try:
        meta=prepare(source,out,a.asr_model,a.whisper,a.fps)
        question=a.prompt_file.read_text() if a.prompt_file else "完整分析视频的交互和内容。每位观察者各自读取全部帧、音频载体与时间戳转写。按时间轴关联画面、声音和文字，给出有帧ID和时间依据的观察、冲突及未知；只有明确期望与实际结果不符才报告问题。每人注明实际读帧数/总帧数；不得跳帧、只读缩略图或从转写冒充听到了声音。"
        (out/"question.txt").write_text(question)
        print(json.dumps(meta,ensure_ascii=False,indent=2),flush=True)
        if a.execute:
            subprocess.run([sys.executable,"-B",str(HERE/"kimi_readmedia.py"),"--config",str(a.config),"--model","MiniMax-M3","--mode","swarm","--observers",str(a.observers),"--manifest",str(out/"manifest.json"),"--prompt-file",str(out/"question.txt"),"--output-dir",str(out/"analysis"),"--execute"],check=True)
    except (ValueError,RuntimeError,FileExistsError,subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc))


if __name__=="__main__":main()
