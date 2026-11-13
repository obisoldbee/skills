# Career Discovery 职业深度访谈

用一份空白或不完整的简历开始，每轮追问一件具体的事，弄清你当时做了什么、谁作了决定、结果有什么证据。材料充分后，再整理为职业时间线、面试故事或针对某个岗位的简历。插件版本为 0.2.0。

## 使用

支持 Agent Skills 的客户端可以单独加载 [career-discovery](skills/career-discovery/SKILL.md)。在 Codex 项目中使用时，把整个 `skills/career-discovery/` 放入该项目的 `.agents/skills/`。支持 Agent Plugins 1.0.0 的客户端可以读取包根的 [plugin.json](plugin.json)。访谈使用包内文档和模板，无需安装其他仓库或启动服务。

可以这样开始。

> 我的简历几乎是空白的。请从我最近的一份工作问起，每轮只问一个问题。等事实和个人贡献核实后，再帮我写简历。

续访时可以说“从上次未解决的问题继续”。准备投递时，提供目标岗位说明，要求把每项关键要求对应到已核实的项目证据。给出估计值时保留“大约”等限定。团队的成绩和你个人作过的决定分别记录。

## 职业材料

对话可以直接进行。要保存进度时，指定自己的工作目录，并说明可以在那里创建 `career-assets/`。会话记录整理已确认的事实、待核实的矛盾和下次的首个问题。涉及客户、同事或内部项目时，可先用代称。公开插件目录只存技能和空白模板。

## 方法与来源

| 来源 | 在本包中的用途 |
|---|---|
| [obra/superpowers · brainstorming](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/brainstorming/SKILL.md) | 先读材料，一次解决一个疑点，再决定下一步问什么。 |
| [Q00/Symposium · wonder](https://github.com/Q00/Symposium/blob/60037854824e369b004703de30877a6c88530f60/skills/wonder/SKILL.md) | 借鉴苏格拉底式追问，让新线索改变访谈方向。 |
| 数字生命卡兹克的 [leader](https://github.com/KKKKhazix/khazix-skills/blob/71cd50ffe1f1f4d400b54be967dc6b59379aff8f/leader/SKILL.md) 与 [hv-analysis](https://github.com/KKKKhazix/khazix-skills/blob/71cd50ffe1f1f4d400b54be967dc6b59379aff8f/hv-analysis/SKILL.md) | 将目标七问用于界定访谈目的、完成条件和待核实事项。沿时间线追踪职责变化，再与同一时期的项目或目标岗位对照，形成待本人核实的定位。 |
| [FrancyJGLisboa/agent-skills-platform · structured interview](https://github.com/FrancyJGLisboa/agent-skills-platform/blob/0c6900a0597622791d1daaafc1c19b2fead0e8d4/references/structured-interview.md) | 借鉴结构化访谈与质量检查，将事实、冲突和待确认事项记录到职业材料中。 |
| [Agent Plugins 1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/44a0ff84bfdfebccfc649dce9aea9ccc45cbfbf9/spec/1.0.0.md) | 确定包根清单和内嵌 Skill 的发现位置。`plugin.json` 引用该版本的 Schema。 |

职业资产库设计阶段还调研了两个项目，一个把职业经历整理成证据和岗位材料，另一个将访谈组织成可持续维护的职业资料库。[rubickguo/career-asset-interviewer](https://github.com/rubickguo/career-asset-interviewer/tree/a575b093eeb7b1cbb3b0ee9cd3e35bc08d7cfbcc) · [DSNeville/career-repo-builder-skill](https://github.com/DSNeville/career-repo-builder-skill/tree/92f423e8102d817d90676fa4dfe1c099759f19a4)

本插件沿用原包声明的 [MIT 许可证](LICENSE)。四个方法项目的版权声明见 [第三方说明](THIRD_PARTY_NOTICES.md)。Agent Plugins 的规范文档采用 CC BY 4.0，Schema 和软件采用 Apache-2.0。[规范仓库许可说明](https://github.com/agentplugins/agent-plugins-spec/blob/44a0ff84bfdfebccfc649dce9aea9ccc45cbfbf9/LICENSE.md)

## 检查

在包目录执行 `shasum -a 256 -c SHA256SUMS.txt` 可核对本仓库版本的文件。行为用例与评分方法见 [评估指南](skills/career-discovery/evals/README.md)。真实求职者的完整访谈效果仍待实测。
