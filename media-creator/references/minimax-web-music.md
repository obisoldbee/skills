# MiniMax Web Music

## 路由边界

通用音乐请求默认走 <https://www.minimaxi.com/audio/music>，只承诺原创歌曲和纯音乐 BGM。它是需要登录态的网页执行路线，不是 MMX API 的包装，也不是 voice cloning、reference-audio editing 或 cover 路线。

主任务先按 [browser-handoff-envelope.md](browser-handoff-envelope.md) 冻结最终 payload；ego-browser worker 只把这些字段映射到页面，不改变创意内容。若 live `project-handoff` visible-task surface 可用，使用 `luna-max` visible thread（`gpt-5.6-luna`、`max`）；没有该 surface 但当前 Harness 已验证等价浏览器执行能力时，才按同一 envelope 本地执行，ego-browser 仍是首选。显式 Luna 请求不能因 thread 创建失败而降级。

## 预检与表单

在同一个 task space 打开 `https://www.minimaxi.com/audio/music`，用页面实时状态确认已经进入音乐创作页，而不是登录页、活动页或错误页，并读回当前模型、余额、数量和主提交按钮费用。遇到登录、验证码或人工确认，按 ego-browser handoff 暂停，不读取凭据、不绕过验证。

最终 payload 的最小字段是：

- `title`：短且可识别的歌曲名称；
- `mode`：`instrumental` 或 `vocal`；
- `style_prompt`：可执行的曲风、用途、情绪、速度、乐器、结构和排除项描述；
- `lyrics`：人声歌曲需要时提供，纯音乐保持为空；
- `count`：正整数，未指定时固定为 `1`，即使页面默认显示批量数量也先调为 1；
- `output_path`：调用方授权的绝对最终 MP3 路径；其父目录必须可写，已有文件默认不覆盖。

纯音乐打开页面的“纯音乐”开关并保持歌词为空。人声歌曲关闭开关，并填入主任务提供的歌词与风格。网页模型可能漂移（历史指南中的 `Music-2.5+` 不构成当前选择），只选择实时页面仍显示且支持目标模式的模型；不要自行替换 model 作为创意决策。

提交前再次确认最新页面中的模型、数量、余额和费用。费用为非零、费用不明确、余额不足或需要未经授权的付费/订阅时暂停。只点击表单内与数量相邻的主提交按钮一次；页面顶部活动按钮不是等价提交入口。

## 完成、下载与验证

提交后先确认作品区出现本次标题/批次对应的新生成状态，再持续观察同一作品。必须等待全曲完成；试听片段、作品卡出现或 toast 不代表完成。生成失败、状态不明或页面被用户接管时停止，不重复生成。

全曲完成后，只在目标作品卡内选择下载，导出格式按当前页面选择 MP3。把浏览器下载行为和最终格式点击放在同一个 ego-browser 执行上下文，等待临时后缀消失，再从文件系统读回 `output_path`：必须是普通文件、大小大于 0、可识别为 MP3，并记录 SHA-256。下载失败只处理同一作品的再次下载，不重新提交。

交付状态只有“网页生成完成 + MP3 下载完成 + 本地文件读回通过”才是 `verified_artifact`。输出不宣称特定时长、voice cloning、reference-audio editing、cover 或商用许可；商用权利以账号套餐和适用协议为准。
