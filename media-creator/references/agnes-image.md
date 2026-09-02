# Agnes Image 2.1 Flash

官方文档：<https://agnes-ai.com/zh-Hans/docs/agnes-image-21-flash>

## 能力

- 模型：`agnes-image-2.1-flash`
- 端点：`POST /v1/images/generations`
- 文生图；
- 图生图/转换/重绘/风格化；
- 多图合成；
- URL 或 Base64 输入和输出。

## 请求合同

- 文生图必填：`model`、`prompt`、`size`。
- 推荐 `size`：`1K`、`2K`、`3K`、`4K`，配合 `ratio`。
- 图生图/多图：在 `extra_body.image` 中传入图片 URL 或 Data URI Base64 数组。
- URL/B64 输出：使用 `extra_body.response_format: url|b64_json`；不要把 `response_format` 放在顶层。
- 文生图 Base64 也可用 `return_base64: true`。
- 图生图不需要 `tags: ["img2img"]`。

使用本包适配器先 dry-run：

```bash
python3 -B scripts/agnes_media.py image \
  --prompt "<prompt>" \
  --size 2K \
  --ratio 16:9 \
  --output <output.png>
```

图生图或多图追加重复的 `--image <url-or-data-uri>`。确认预览正确后，只有用户授权真实调用时才加 `--execute`。

## 鉴权与结果

从外部环境或显式 env 文件读取 `AGNES_API_KEY`。不要把 Key 写入命令、日志或包内。成功结果位于 `data[0].url` 或 `data[0].b64_json`。

未执行供应商调用时使用 `configured_not_called`，不能因 env 文件存在而报告生成成功。

## 输出保护与恢复

图片和视频适配器共用以下保存合同：`--execute --output` 在读取凭据、提交前用 `lstat` 拒绝已有文件、目录、符号链接（含断链）和硬链接，核对并持有输出父目录的身份与句柄。正常初始父目录别名（包括 macOS `/tmp`）先解析，再绑定真实目录。必要的新父目录通过已绑定祖先创建；同目录私有探测文件验证独占创建、硬链接发布和清理后即删除。平台缺少目录相对的 no-follow 原语、或文件系统探测失败时，在读取凭据和提交前停止，不降级。dry-run 不做这些预检、不写文件、不读凭据、不调用供应商。

下载或解码完成后，临时文件、原子不替换硬链接、清理及恢复回执都通过同一个父目录句柄操作，不重新跟随绝对路径。父目录被改名或替换时停止，不向替换目录写入。若移动发生在发布的最后时刻，已完成产物只会留在原绑定目录；错误中的 `artifact` 给出文件名和目录设备/inode 身份，`path_verified=false` 表示旧路径已失效，不能按旧路径宣称保存成功。禁止覆盖目标或降级为 `rename/replace`。

提交后的下载、解码或保存失败返回非零，且不重新生成。若绑定目录仍可安全使用，错误报告的 `recovery.path` 指向独占创建的 `.agnes-recovery-*.json`（POSIX 权限 `0600`），只保留本次图片 `data[0].url/b64_json` 或视频 ID、状态与 `metadata.url`；不保存鉴权配置或任意调试字段。所有公共错误只使用安全类别、HTTP 状态码或固定失败状态，不回显 HTTP body、URLError 原文、供应商 `error` 对象、签名 URL 或媒体内容。该回执是私有恢复材料，不得提交到 Git 或公开分享。

恢复时只读取该回执，向另一个获授权且不存在的目标保存同一结果；视频也可凭同一 ID 继续查询。不要重跑生成命令。若 `recovery.status=unavailable`，表示没有已验证的完整回执；`partial_location` 仅说明未清理文件的名称与绑定目录身份，不能当作成功回执，尤其不可沿 `path_verified=false` 的旧路径寻找。停止并说明恢复材料缺失或位置需重新确认，不自动重试生成。回执不保证下载 URL 永久有效，也不保证无效 Base64 可以恢复。
