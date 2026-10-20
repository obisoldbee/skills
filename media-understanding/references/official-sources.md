# Official Provider Contracts

MiniMax and Agnes reviewed: 2026-10-20. Volcengine and MiMo retain their earlier review scope; they were not revalidated in this update. These links describe public contracts, not local credentials, entitlement, balance, successful calls, or permanent model availability. Recheck before an external call when the contract is material.

## Agnes

Agnes section reviewed 2026-10-20. Model `agnes-3.0-flash`: 512K context,
65,536 maximum output; Chat Completions, Responses and Anthropic-compatible Messages.
Official input modalities are text and image URL, not native video. Chat fields include
`temperature`, `top_p`, `max_tokens`, `stream`, `tools`, `tool_choice`, and
`chat_template_kwargs.enable_thinking`; Messages supports `thinking.type` and
`thinking.budget_tokens`. These fields are endpoint-specific, not a universal payload.
Kimi local-image and sampled-frame compatibility is a separate runtime test; never add
`video_in` merely because a model alias or API Key exists. See [Kimi branch](kimi-readmedia.md).

- [Agnes 3.0 Flash](https://agnes-ai.com/zh-Hans/docs/agnes-30-flash): model id `agnes-3.0-flash`.
- [Quickstart](https://agnes-ai.com/zh-Hans/docs/quickstart) and [overview](https://agnes-ai.com/zh-Hans/docs/overview): OpenAI-compatible `POST https://apihub.agnes-ai.com/v1/chat/completions` with Bearer authentication.
- The current image example proves a public `image_url`. It does not prove local upload, data URL, or Base64 support. Keep those transports disabled until separately documented or authorized and tested.
- [Token Plan](https://agnes-ai.com/zh-Hans/docs/tokenplan) distinguishes free, enterprise and Token Plan Key pools. Use the selected key profile; a subscription alone does not identify the current generic key pool. No new key is selected by this package.
- Official client integration pages exist; a standalone Agnes Code CLI media command could not be verified from a live install source in this review. The package keeps its owned Chat adapter rather than adding an unverified CLI.

## MiniMax

- [Anthropic API](https://platform.minimax.cn/docs/api-reference/text-anthropic-api) documents exact `MiniMax-M3.1-Flash` and `MiniMax-M3` IDs, their distinct thinking/effort behavior and ignored sampling fields. [Text guide](https://platform.minimax.cn/docs/guides/text-generation) recommends Anthropic compatibility. The current domestic base is `https://api.minimax.cn/anthropic`; the package preserves explicit old profile bindings without claiming this research tested old API hosts.
- [Messages API](https://platform.minimax.cn/docs/api-reference/text-chat-anthropic) and its [OpenAPI schema](https://platform.minimax.cn/docs/api-reference/text/api/openapi-chat-anthropic.json) define URL/Base64 image and video blocks. Base64 uses `source.type=base64` with `media_type` and `data`; image <=10 MB, video <=50 MB, request <=64 MB. [Files](https://platform.minimax.cn/docs/api-reference/file-management-upload) supports larger videos <=512 MB with `purpose=video_understanding` and `mm_file://file_id`.
- [ASR guide](https://platform.minimax.cn/docs/guides/speech-to-text) and [ASR API](https://platform.minimax.cn/docs/api-reference/speech-to-text) document `asr-1.0`, multipart `/v1/speech_to_text`, 500 seconds/50 MB, timestamps, speakers and subtitles. This is separate from M3 Messages; native M3 audio blocks remain unconfirmed.
- [AI SDK](https://platform.minimax.cn/docs/api-reference/text-ai-sdk) claims PDF support, while Messages OpenAPI does not specify a document/file block. The exact direct-PDF contract remains unresolved; continue local parse/OCR rather than inventing a payload.
- [CLI](https://platform.minimax.cn/docs/token-plan/minimax-cli) and [v1.0.28 source](https://github.com/MiniMax-AI/cli/tree/v1.0.28) were checked against local help. Image VLM does not expose a model; ASR was added in 1.0.26. Auth, endpoint and region selection need explicit binding. See [CLI contract](minimax-cli.md) for commands and source locations.

## Volcengine Ark

| Official page | Proven contract | Routing consequence |
|---|---|---|
| [Image understanding](https://www.volcengine.com/docs/82379/1362931?lang=zh) | Responses/Chat; Files/path, URL, Base64; description, grounding, GUI | Prefer regular Platform Responses/Files for production |
| [Video understanding](https://www.volcengine.com/docs/82379/1895586?lang=zh) | Responses/Chat; Files, URL, Base64; temporal/video QA and model-dependent audio | Verify exact model and input contract |
| [Audio understanding](https://www.volcengine.com/docs/82379/2377589?lang=zh) | ASR, alignment, speakers, translation, meeting-minutes prompt recipes | Treat subtitles/minutes as prompt recipes, not typed specialist APIs |
| [Document understanding](https://www.volcengine.com/docs/82379/1902647?lang=zh) | PDF via Responses; Files or URL/Base64; pages become visual inputs | Only PDF is proven; preserve page evidence |
| [Ark CLI guide](https://www.volcengine.com/docs/82379/2536875?lang=zh) | `+understand` exposes 12 recipes over one Responses engine | CLI convenience is not a second PDF engine or proof of Plan/model compatibility |

The PDF choice is operational: use Files + Responses for large/reused documents and production lifecycle control; use URL/Base64 for one-off PDF under the documented limit; use `arkcli +understand doc-extract` for an interactive fixed recipe after checking its resolved model.

[Agent Plan](https://www.volcengine.com/docs/82379/2366394?lang=zh) and [Coding Plan](https://www.volcengine.com/docs/82379/1925114?lang=zh) quotas are limited to supported AI/coding tools. They are not ordinary custom-API entitlement. Keep ordinary Platform, Agent Plan, Coding Plan, and Ark CLI profiles isolated. The [current model list](https://www.volcengine.com/docs/82379/1330310?lang=zh) must be checked before claiming a modality is supported.

## Xiaomi MiMo

The reviewed public contract uses model `mimo-v2.5` and OpenAI-compatible `POST https://api.xiaomimimo.com/v1/chat/completions`. Token Plan and pay-as-you-go profiles have separate Base URLs/keys and must not be mixed. The API key only authenticates the request; image bytes come from a public URL or Base64 data embedded in the JSON request body.

| Media | Official page | Proven input and limit summary |
|---|---|---|
| Image | [Image understanding](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/multimodal-understanding/image-understanding) | 支持公网 URL，或将本地图片在客户端转成 Base64 后内联传入；不支持直接传本地路径/文件对象。URL 文件≤50MB，Base64 编码字符串≤50MB。 |
| Audio | [Audio understanding](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/multimodal-understanding/audio-understanding) | `input_audio.data`, public URL or data URL; URL up to 100MB, encoded Base64 string up to 50MB; no documented hard duration limit |
| Video | [Video understanding](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/multimodal-understanding/video-understanding) | `video_url.url`, URL or data URL; URL up to 300MB, encoded Base64 string up to 50MB; `fps` 0.1–10; no documented hard duration limit |

For a local image, the client reads the file and encodes it before the request. OpenAI format uses `image_url.url = data:{MIME_TYPE};base64,...`; Anthropic format uses `source.type = base64` with `media_type` and `data`. The API does not accept a local path, `file://`, a file object, or a separate upload reference as the image content.

The pages being readable does not prove local readiness. Keep each route disabled until its own adapter, credential binding, and authorized media/transport smoke test pass. Error categories must remain distinct; see [MiMo error codes](https://mimo.mi.com/docs/zh-CN/api/guidance/error-codes).
