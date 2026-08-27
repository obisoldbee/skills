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

图片和视频适配器共用以下保存合同：`--execute --output` 在读取凭据、提交前固定输出的绝对父目录，并用 `lstat` 拒绝已有文件、目录、符号链接（含断链）和硬链接。正常父目录符号链接（包括 macOS `/tmp`）可用。下载或解码完成后，先写同目录独占临时文件，再用原子硬链接创建目标；目标被抢占或文件系统不支持硬链接时失败，绝不覆盖或降级为 `rename/replace`。dry-run 不做预检、不写文件、不读凭据、不调用供应商。

提交后的下载、解码或保存失败返回非零，且不重新生成。若同目录可写，错误报告的 `recovery.path` 指向独占创建的 `.agnes-recovery-*.json`（POSIX 权限 `0600`），只保留本次图片 `data[0].url/b64_json` 或视频 ID、状态与 `metadata.url`；不保存鉴权配置或任意调试字段。终端只报告回执路径，避免泄露签名 URL 或媒体内容。该回执是私有恢复材料，不得提交到 Git 或公开分享。

恢复时只读取该回执，向另一个获授权且不存在的目标保存同一结果；视频也可凭同一 ID 继续查询。不要重跑生成命令。若 `recovery.status=unavailable`，表示回执未保存成功；若报告 `partial_path`，该文件也不算完整回执。停止并说明恢复材料缺失，不自动重试生成。回执不保证下载 URL 永久有效，也不保证无效 Base64 可以恢复。
