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
