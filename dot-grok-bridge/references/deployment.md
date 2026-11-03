# 部署与注册

## 参考实现

`../assets/service/bridge.py` 为实装版本原样参考，SHA256 为 `b1885d9f026df0fcb6c4445f4a203fab7615334bcee389d4764750b91488e4e3`。Python 3.11+，标准库及 POSIX `fcntl`。实现 SQLite 状态、OAuth/PKCE、五个消息工具、事件订阅和 Grok Webhook 投递，按单 owner、单服务进程设计。

配套服务代码的隔离检查记录为 130/130 个 unittest 执行项通过，包含继承或导入复用的既有夹具检查。部署时另行记录备份、重启前在途状态、service active、OAuth metadata 与双方实际协作证据；实例运行记录保存在 Skill 树外的已授权交付位置。

先记录运行代码、启动方式、环境字段名、配置权限、原订阅和在途数量。配置及数据库含秘密，检查使用字段白名单。修改前读实际源码及调用方，参考资产不能无条件覆盖更高版本。

新部署先绑定服务器与目录，代码、状态、环境和路由分开保存。`../assets/bridge.env.example`、`../assets/bot-routes.example.json`、`../assets/ob-bridge.service.example`、`../assets/Caddyfile.example` 均为无可用凭据的模板，没有自动安装入口。已有实例沿用其端口和启动方式，新增资源、依赖及系统变更按当前授权处理。

## 凭据方向

| 凭据 | 存放/用途 |
| --- | --- |
| `ADMIN_KEY` | 部署侧私密环境和 OAuth owner 确认，不发给 bot |
| Dot OAuth access/refresh | 由宿主保存，映射为 dot；不提取给调试方冒用 |
| 原 `GROK_KEY` | 原 bot 主动向桥发送，兼容既有路由 |
| 各 bot `send_key` | 该 bot 安全输入卡中的唯一变量，向桥 `/messages` 发消息 |
| `GROK_WEBHOOK_KEY` / 各 bot `webhook_key` | 桥触发对应例程，从其安全配置读取 |
| Dot subscription secret | 订阅握手提供，用于事件签名 |
| `/grok/<scoped-token>` | 指定入站消息的 claim/reply/complete，不赋予主动发起能力 |

各角色、各 bot 使用独立随机秘密，发送密钥与 Webhook 密钥不能互换。生成后直接写私密文件或安全控件，避免经命令行参数、聊天、截图、日志和交接包。

实际 runtime 曾确认跨 bot 同名环境变量覆盖，当前 bot 读取到另一 bot 的发送 key。不按 bot 的聊天或 UUID 假设同名变量隔离。为每个 bot 绑定唯一变量名，例如 `GROK_BRIDGE_KEY_SWE`、`GROK_BRIDGE_KEY_TIBO`；原始黑布丁 bot 同样使用专属 `GROK_BRIDGE_KEY_BLACK_PUDDING`，按其既有 actor 核对 sender。各 helper 固定读取自身变量，缺失或指纹不符即停，不回退到通用 `GROK_BRIDGE_KEY`。持久规则只允许读取本 bot 的 secret，不枚举或读取其他 bot 的变量。变量名区分解决引用歧义，真实系统隔离仍需另外验证。

持有已核对的原正确 key 时，可以把原值改存到本 bot 的唯一变量，无需重生成，各 bot 继续使用独立 key。实例采用的命名方式是取私密 `send-keys.json` 的 bot 名称，去掉 `grok-` 前缀，将剩余名称大写并把连字符改为下划线，作为 `GROK_BRIDGE_KEY_` 的后缀；保存前核对生成名称逐 bot 唯一。在获授权的部署记录中绑定 slug、UUID、变量名和预期 SHA256；首次运行及变量改存后，先按 [消息协议](protocol.md) 在实际 runtime 只做指纹比对，再发送并核对响应 sender。服务端原 `GROK_KEY` 的兼容用途保持原合同，它不是云电脑 helper 的通用回退变量。

helper 与原例程发送常规完整请求时，显式设置 `end_of_turn=true`；只有本方确实还有后续片段时才设为 false。原始 bot 与新增 bot 使用同一规则，保存后回读变量引用、默认轮末标记及实际请求载荷。

## 首次接入顺序

1. 授权服务器准备私密目录、环境、TLS 反代与服务。后台 HTTP 仅监听 loopback。反代保留 OAuth、MCP 和回调路径/正文，不记录带秘密的路径与请求体。
2. Grok Bot 建立或找到 Webhook 例程，保存固定 URL/密钥并绑定正确 bot。桥通过 Bearer Webhook 密钥触发；例程接受实际载荷，执行 claim、处理、reply、complete。
3. ChatGPT 连接 `BRIDGE_BASE_URL/mcp`，按实际宿主执行 OAuth owner 连接。本实现使用 owner key、PKCE 和宿主回调域名白名单。
4. 原始 Dot 建立 `message.created`、recipient=dot 的持久 Webhook 订阅和接收任务。`CALLBACK_HOSTS` 绑定宿主实际返回的事件接收域名，核对握手挑战、签名和有效期。
5. 保存双方协作规则及每个 bot 的持久主动 helper、README 和 DM/群聊发现规则，核对实际注入的工具/事件源，逐个运行真实验收。主动入口要求见 [消息协议](protocol.md)。

协议版本和 `events/*` 为附带实现及当时宿主合同，换宿主或升级时核对其实时能力。缓存处理见 `ui-and-cache.md`。

## 多 bot 注册

`BOT_ROUTES_FILE` 指向 version=1 的 JSON。每个独立 bot 使用稳定 slug、canonical 平台 UUID、独立目的 URL 和两种独立凭据。群房间不登记为执行身份，显示名只用于人工回读。

```json
{"version":1,"bots":[{"id":"grok-artist","bot_uuid":"11111111-1111-4111-8111-111111111111","enabled":false}]}
```

启用前补 `webhook_url`、`webhook_key`，以及 `send_key` 或 lowercase SHA256 `send_key_hash` 之一。发送密钥原值仅安全保存到对应 bot。示例 UUID 必须换成实际平台 ID。

在本次部署记录中另记该 bot 的主动 helper、README、持久发现规则位置及各自验证状态。仅保存两种密钥和 Webhook 时，主动协作仍待验证；不能沿用另一 bot 的验收结果。

启动校验要求私密 regular file，owner=root 或实际服务 uid，无 group/world bits，拒绝 symlink，使用 0600 或 0400。slug 匹配 `[a-z][a-z0-9._-]{0,63}`，排除 dot/grok/admin；UUID 唯一。凭据长度 40..512，无空白，不能跨角色/路由复用。

目标要求 HTTPS 443，无 userinfo、fragment 或控制字符，不能与其他路由及原路由重复，包括等价默认端口写法。投递另做 DNS 公网地址 pinning 并禁止重定向。已落库的 slug↔UUID 不可换人；route fingerprint 绑定待投递消息及回调，禁用/换密钥/改目的会使旧操作失效。

缺失或空注册配置只保留原 dot/grok。未知、禁用或变化的路由拒绝投递，不回落给 Dot/原 bot。注册仅在进程启动加载。新接入默认 disabled，先启用一个并真实验收，再逐个放开其余目标。

## 部署更新

先进入资产 `service/`，运行 `python3 -B run_offline_tests.py`。测试用假凭据、假上游和临时 SQLite，包含短时本机 loopback HTTP，不访问外部服务。

确认用户无活跃桥接工作，检查所有尚未处理或结果未知的消息。包括 queued/dispatching、已投递未领取的 routine_accepted/event_accepted、agent_processing，以及 delivery_unknown/processing_unknown。结合会话、原始聊天和上游运行记录判定是否收口；停止会话也不能证明外部执行已结束。旧历史记录按实际状态归档判断，不仅凭三个计数为零宣称无在途工作。

存在在途或未知任务时先协调并查明结果，不强停用户工作。停服务后用 SQLite backup API 制作一致副本，同时私密备份代码、环境和路由；不能只复制活跃 WAL 数据库主文件。

以实际服务 uid 验证 registry 和暂存代码，覆盖服务账户的读权限。本实现使用追加迁移，保留 tokens、订阅和 binding。启动后回读代码哈希、service active、认证健康、原订阅及新身份数量。

文件后缀导致 module loader 不识别、运行账户读权限失败和服务启动错误应分别定位；不要重建 OAuth 或清空数据库解决配置问题。回滚读 `acceptance-and-recovery.md`。

## 静态 IP 或公共入口迁移

静态 IP 已由其他人类授权任务更换时，先核对实际新入口、同一 owner/Dot 及本次桥迁移范围。逐项同步或回读 `PUBLIC_BASE_URL`、TLS、OAuth MCP 连接、接收 source/trigger、各 bot helper、原 routine 主机校验及自动审核规则。示例继续使用通用域名和占位身份，实例地址及 UUID 留在获授权的部署记录。

1. 停止新派活，按上文检查所有在途和结果未知消息，并核对双方外部执行。只有确认无在途、无未知结果后进入迁移；否则保留 CID/MID 和实际状态，先协调收口。记录原 Dot、原接收 task、OAuth client、旧 source/trigger/SID 与迁移目标。
2. 停服务后用 SQLite backup API 制作数据库一致备份，并私密备份相关配置与代码。保留数据、身份、OAuth client 和恢复入口，按本次授权准备单次迁移。
3. 同步服务的 `PUBLIC_BASE_URL`、TLS 证书/反代和 OAuth/MCP 对外元数据，受控启动服务后回读 HTTPS443 与当前实际运行配置，继续保持新派活暂停。旧消息的 callback 不自动改域名；保持其原作用域，按实际状态安排恢复。
4. 旧 ChatGPT 插件 URL 在实装时的当前 UI 无法编辑。准备指向新 `/mcp` 的连接并复用原 OAuth client；保留原 Dot 和原接收 task。连接、字段及宿主能力按 [界面与缓存](ui-and-cache.md) 的实际回读处理。
5. 先停用旧 source，确认旧 trigger 不再触发接收；同一接收 task 切换 source，不新增并行 receiver。默认保留 binding。只有本次已明确授权同一 owner/Dot 的迁移、无在途或未知消息且已有一致备份，确需变更 binding 时才按当前实现执行受控单次迁移，并记录前后绑定。清空 binding 不是常规修复步骤。
6. 替换原接收 task 的 trigger 时，不把旧 source 的 `trigger.id` 或 SID 填入新 source；更新请求省略这些旧标识，由宿主为新 source 生成。成功响应后用宿主 list 回读原 task 的新 source、trigger 及新 SID，再查服务端持久订阅记录，确认新 SID 绑定同一 owner/Dot。两处不符时先定位，不重复创建 receiver。
7. 同步各 bot helper 的当前桥入口、README 与发现规则，回读原 routine 的主机校验及自动审核允许的主动 `/messages` 与作用域回调主机。保持路径、身份和用户任务范围限制，不扩大为任意 URL。确认旧 source 已停用、仅原接收 task 接收，再由原双方按 [验收与恢复](acceptance-and-recovery.md) 逐 bot 验证真实协作。

迁移中断时保留当前阶段及新旧绑定状态，先定位具体失败，不自动再次迁移或清空 binding。配置保存、连接成功、list 回读、服务端新 SID 与真实往返分别记录，未覆盖的 bot、渠道或行为明确标为待验证。具体运行结果与证据保留在 Skill 树外，通用正文保留可复用的操作条件。
