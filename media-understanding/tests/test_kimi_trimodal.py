"""Exercise real offline media export and exact mixed-input evidence boundaries."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PROVIDERS = Path(__file__).resolve().parents[1] / 'scripts/providers'
def module(name):
    spec=importlib.util.spec_from_file_location(name, PROVIDERS/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
trimodal=module('kimi_trimodal')
kimi=module('kimi_readmedia')

class TrimodalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requires local ffmpeg')
    def test_real_2fps_export_timestamps_no_audio_and_no_overwrite(self):
        source=self.root/'a b.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=size=320x240:rate=10',
                        '-t','2','-c:v','libx264',str(source)],check=True)
        out=trimodal.destination(source)
        before=trimodal.sha(source)
        meta=trimodal.prepare(source,out,self.root/'missing-asr.pt','missing-whisper')
        frames=json.loads((out/'frames.json').read_text())
        self.assertEqual(out.name,'frames_a b')
        self.assertEqual(meta['frame_count'],4)
        self.assertEqual([f['timestamp_seconds'] for f in frames],[0,0.5,1,1.5])
        self.assertEqual(meta['audio_state'],'no_audio_stream')
        self.assertEqual(before,trimodal.sha(source))
        self.assertEqual(len(kimi.inputs(out/'manifest.json',['image_in'])),5)
        with self.assertRaises(FileExistsError):
            trimodal.prepare(source,out,self.root/'missing-asr.pt','missing-whisper')

    def test_text_does_not_require_media_capability_and_hash_is_enforced(self):
        text=self.root/'asr.json';text.write_text('{"segments":[]}')
        manifest=self.root/'manifest.json'
        item={'kind':'text','path':str(text),'sha256':kimi.sha(text)}
        manifest.write_text(json.dumps([item]))
        self.assertEqual(kimi.inputs(manifest,[]),[item])
        text.write_text('changed')
        with self.assertRaisesRegex(ValueError,'hash_mismatch'):kimi.inputs(manifest,[])

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requires local ffmpeg')
    def test_digital_silence_needs_no_asr_and_preserves_audio(self):
        source=self.root/'silent.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=size=320x240:rate=10',
                        '-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-t','1',
                        '-c:v','libx264','-c:a','aac',str(source)],check=True)
        out=trimodal.destination(source)
        meta=trimodal.prepare(source,out,self.root/'missing-asr.pt','missing-whisper')
        info=json.loads((out/'audio-info.json').read_text())
        self.assertEqual(meta['audio_state'],'digital_silence')
        self.assertEqual((info['sample_rate'],info['channels'],info['peak_pcm16']),(44100,2,0))
        self.assertEqual((out/'transcript/audio.srt').read_text(),'')
        manifest=kimi.inputs(out/'manifest.json',['image_in','video_in'])
        self.assertEqual([x['kind'] for x in manifest],['image','image','video','text'])

    def test_peer_read_or_missing_transcript_cannot_pass(self):
        text=self.root/'asr.json';text.write_text('{}')
        item={'kind':'text','path':str(text),'sha256':kimi.sha(text)}
        home=self.root/'home';out=self.root/'out';out.mkdir()
        wire=home/'sessions/s/agents/main/wire.jsonl';wire.parent.mkdir(parents=True)
        rows=[{'type':'llm.request','model':'MiniMax-M3'},
              {'type':'context.append_loop_event','event':{'type':'tool.call','name':'Read','args':{'path':str(self.root/'peer.md')},'toolCallId':'r'}},
              {'type':'context.append_loop_event','event':{'type':'tool.result','toolCallId':'r','result':{}}},
              {'type':'context.append_loop_event','event':{'type':'content.part','part':{'type':'text','text':'done'}}},
              {'type':'context.append_loop_event','event':{'type':'step.end','finishReason':'end_turn'}}]
        wire.write_text('\n'.join(map(json.dumps,rows)))
        result=kimi.evidence(home,out,'MiniMax-M3',[item],'single',3,lambda s:s)
        self.assertFalse(result['checks']['exact_transcript_reads'])
        self.assertFalse(result['checks']['no_peer_tools'])
        self.assertFalse(result['passed'])

if __name__=='__main__':unittest.main()
