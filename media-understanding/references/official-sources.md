# Official Provider Contracts

Last reviewed: 2026-08-11. These links describe public contracts, not local credentials, entitlement, balance, successful calls, or permanent model availability. Recheck before an external call when the contract is material.

## Agnes

- [Agnes 2.5 Flash](https://agnes-ai.com/zh-Hans/docs/agnes-25-flash): model id `agnes-2.5-flash`.
- [Quickstart](https://agnes-ai.com/zh-Hans/docs/quickstart) and [overview](https://agnes-ai.com/zh-Hans/docs/overview): OpenAI-compatible `POST https://apihub.agnes-ai.com/v1/chat/completions` with Bearer authentication.
- The current image example proves a public `image_url`. It does not prove local upload, data URL, or Base64 support. Keep those transports disabled until separately documented or authorized and tested.

## MiniMax

- [Text generation guide](https://platform.minimaxi.com/docs/guides/text-generation) marks Anthropic compatibility as recommended and the default path. Use base URL `https://api.minimaxi.com/anthropic` and `POST https://api.minimaxi.com/anthropic/v1/messages` for `MiniMax-M3` image/video understanding; see the [Anthropic API contract](https://platform.minimaxi.com/docs/api-reference/text-anthropic-api).
- [OpenAI-compatible M3](https://platform.minimaxi.com/docs/api-reference/text-openai-api) at `POST https://api.minimaxi.com/v1/chat/completions` remains officially supported, but it is only a compatibility fallback for a project already bound to the OpenAI SDK. It is not the default recommendation.
- [Files upload](https://platform.minimaxi.com/docs/api-reference/file-management-upload): large video can use `purpose=video_understanding` and `mm_file://file_id`; direct URL/Base64 video is the smaller-file path.
- [MiniMax API overview](https://platform.minimax.io/docs/api-reference/api-overview) and [MiniMax CLI](https://platform.minimax.io/docs/token-plan/minimax-cli) define different profiles. The locally installed `mmx vision describe` does not expose its underlying model id.
- [MCP guide](https://platform.minimaxi.com/docs/guides/mcp-guide): ordinary MCP availability is not evidence of a general-purpose understanding tool. Do not prefer MCP unless the exact current tool is discovered and matches the requested media contract.
- Standalone M3 audio and native PDF/document inputs were not documented in the reviewed contracts. Use ASR/transcript for audio semantics and local parse/OCR for documents.

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
