---
name: minimax-agent-daily-checkin
description: "使用 ego-browser 查询 MiniMax Agent 签到和积分，或执行每日签到并核验积分增量。固定执行器负责空间、回执和已授权的条件飞书通知。"
---

# MiniMax Agent Daily Check-in

## 执行入口

每次触发重新读取本文件。将 `skill_dir` 绑定为本次读取的 SKILL.md 所在目录，读取当前可用的 ego-browser SKILL.md，然后只调用下面一个入口。固定执行器包含完整浏览器流程；不要另写浏览器脚本、创建空间或制作报告输入 JSON。

| 用户意图 | 命令 |
|---|---|
| 只查询 | `python3 -B <skill_dir>/scripts/run_checkin.py --mode query-only` |
| 明确要求手动签到 | `python3 -B <skill_dir>/scripts/run_checkin.py --mode manual` |
| 定时签到，已授权 bot 通知 | `python3 -B <skill_dir>/scripts/run_checkin.py --mode scheduled --chat-id <caller_lark_chat_id>` |

定时模式先读 [scheduled-wrapper.md](references/scheduled-wrapper.md)。prompt 中的 scheduled、通知目标和 bot 通知授权即为执行授权，无需再次确认；缺少目标或授权返回 `needs_configuration`，不降级执行。含糊请求先澄清。查询不提交登录、不领取、不通知。

运行命令后等待原进程结束；终端返回后台 session 时继续等待该 session。不要再次启动命令、用新空间补读积分，或单独调用 `finish_round.py`、`service_health.py`、lark-cli。命令失败也不修改脚本、回执或 JSON 来补造成功；依据原输出报告阻塞。

## 固定执行器的合同

执行器使用系统 Asia/Shanghai 日期，不采用历史会话的“今天”。一轮最多创建一个 TaskSpace，立即持久化真实数字 ID；在同一页面完成以下流程：

1. 打开 `https://agent.minimaxi.com/`，等待加载并观察当前登录状态。账号和登录入口均未出现时，继续在原页有界等待约 30 秒；只有出现账号、签到控件、明确登录入口或维护提示后才判定状态。等待结束仍无入口时记录页面未就绪并保留原空间。对明确的产品公告、版本更新、促销或新手引导弹窗，按当前可见语义寻找该弹窗内唯一的“关闭／稍后／跳过”，自动关闭后复查消失，继续原页面流程；整轮最多关闭三个，不点击“立即体验”、购买或升级入口。未知弹窗、表单、验证码、协议或权限确认不归类为广告。全部网站操作使用已批准的 ego-browser，不使用隐藏 API、直接 HTTP 或另一浏览器。
2. 查询遇到未登录则交接原空间。执行模式在提交登录前再次核对状态，已自动恢复登录就直接继续签到；确需登录时仅尝试一次已有密码的普通登录，不读写或输出凭据，不走微信/验证码路线。登录或验证未成功才保留原空间并报告，初始未登录本身不提前发送通知。
3. 从当前“每日签到”卡片读取状态，从账号菜单“用量”的可见“积分”读取本轮余额。领取前必须有本轮基线；昨天余额、旧报告、余额减奖励均不可作基线。菜单和卡片都在原页面切换，不另建空间。
4. 已显示“今日已签到”则不点击；只有明确的“签到得 N”允许一次领取。先把“已尝试”落盘再点击；点击结果不明也不能再试。新签到需明确完成状态及积分增量等于 N；读数不符只重读一次，仍不符交接原空间。
5. 正常完成或确认维护后只调用一次 `finish({keep:[]})`，再短暂轮询原 ID 是否从空间列表消失。只有关闭回执和空间消失同时成立才报告“已关闭”。异常按 [task-space-cleanup.md](references/task-space-cleanup.md) 交接，用户接管后不重新认领。
6. 最后由执行器处理 [维护状态](references/service-maintenance.md)、必要通知和 [短报告](references/result-report.md)。签到正常完成时静默；单独的空间 ID/收尾问题只保留本地记录，不作为需要用户协助的飞书告警。异常正文只有 `MiniMax 签到异常。`，维护状态变化也只发一句，不附诊断字段。通知尝试及 message_id 持久化；重复调用返回原回执，不能把“已发送”改成“未触发”。

运行依赖 macOS、已批准的 Ego Lite/ego-browser、站点网络及已有认证。可安全关闭的公告不直接判失败或提前通知；只有关闭入口不明确、关闭后仍遮挡、反复弹出超过限额、未知页面、验证挑战或运行环境不可用时，保存实际失败结果和原空间，不安装、不改网络或安全配置、不收集凭据。执行器通过当前可用的 CLI 连接 Ego。不要硬编码 Ego Lite 版本路径。

## 回执与重入

包在运行时只读。执行器仅在外部状态目录 `$XDG_STATE_HOME/skill-automations/minimax-agent-daily-checkin/`（默认 `~/.local/state/skill-automations/minimax-agent-daily-checkin/`）保存脱敏动作、空间 ID、积分证据、通知回执和最终报告。

scheduled 使用当日锁和固定记录，保证同日重复调用不再次打开浏览器、签到或发信。命令中断时保留“结果待核查”，不自动补跑；人工修复需先核对原空间和动作。manual/query-only 各自建立独立记录，不读取历史成功来冒充本轮查询。记录不是重试调度器；不创建提醒、不更改主任务时间、不清空旧账本。

## 最终回复

只把执行器生成的中文 stdout 原样放在一个 text 代码块中，块外不附过程、表格或建议。正常报告五行：日期、结果、剩余积分、页面、飞书。新获得积分并入结果行，没有独立“领取”字段；失败增加简短原因和原空间 ID。账号、电话、UID、密码、Cookie、Token、原始账号快照不得进入报告或回执。

维护入口：`scripts/test_browser_round.mjs`、`scripts/test_run_checkin.py` 验证执行器；旧 `check_contract_scenarios.py` 检查合成合同场景。历史自提醒合同仅在维护旧部署时查阅 [minimaxcode-retry.md](references/minimaxcode-retry.md)。
