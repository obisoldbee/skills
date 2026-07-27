# OB Skills

个人自用 AI Skills 合集（**monorepo**）。一个仓库装多个 skill，满足多设备、多 agent 工具共用，一处维护、处处同步。

- GitHub: `https://github.com/obisoldbee/skills`（Private）
- 默认分支: `main`
- 规范: 遵循 [Agent Skills](https://agentskills.io) 开放标准，WorkBuddy / Claude Code / Codex / 40+ agent 通用

## 仓库结构

```
skills/                         ← 仓库根 = 多 skill 容器
├── project-conventions/       ← 每个 skill 一个顶层目录，目录里直接 SKILL.md
│   ├── SKILL.md
│   ├── references/
│   └── README.md
├── <A>/                       ← 未来新增的 skill（同样结构）
├── <B>/
└── scripts/                   ← 跨设备软链脚本（不是 skill）
    ├── link-windows.ps1
    └── link-macos.sh
```

**关键**：目录名即 skill 名；目录内直接放 `SKILL.md`（不套子层）。agent 工具按 `~/.workbuddy/skills/<name>/SKILL.md` 加载。

## 安装到本机（任选一台设备）

```bash
# 1) clone 整个 monorepo 到本地某处（这是你的"项目目录"）
git clone https://github.com/obisoldbee/skills.git ~/proj/skills

# 2) 运行软链脚本，自动把每个 skill 建软链到 agent 的 skills 目录
#    Windows (PowerShell, 无需管理员):
pwsh ~/proj/skills/scripts/link-windows.ps1
#    macOS / Linux (bash):
bash ~/proj/skills/scripts/link-macos.sh
```

脚本会**自动发现**所有含 `SKILL.md` 的子目录，逐个建软链：

- Windows: `mklink /J` 目录联接 → `~/.workbuddy/skills/<name>`（免管理员）
- macOS/Linux: `ln -s` 符号链接 → `~/.workbuddy/skills/<name>`

如需同步到其他 agent（如 Claude Code `~/.claude/skills/`），编辑脚本顶部的 `$targets` / `targets` 数组，取消对应注释即可。

## 多设备同步

```
Windows 家用机改 skill → git commit → git push
                              │
                    （GitHub obisoldbee/skills）
                              │
Mac 公司机 git pull → 内容已最新（软链指向同一 checkout，无需重建链）
                      仅当新增/删除 skill 时，重跑一次 link 脚本
```

> 软链指向的是你本地 checkout 的子目录，不是 GitHub。所以 `git pull` 拿到新内容后，agent 加载的就是最新版——**本机零额外 sync**。改完记得重启对应 agent 让它重新加载。

## 新增一个 skill

1. 在仓库根新建目录，例如 `my-new-skill/`
2. 放入 `SKILL.md`（+ 可选 `references/`）
3. `git add my-new-skill && git commit && git push`
4. 各设备 `git pull` 后，重跑一次 `link-*.ps1/.sh` 脚本（脚本会自动发现新 skill 并建链）

删除 skill 同理：删目录 → commit push → 各设备 pull 后手动删对应软链（或重跑脚本会清理错误指向）。

## 维护约定

- 每个 skill 子目录是**普通文件夹**，monorepo 根才是 git 仓库本身（`src/skills/` 的 `.git`）。
- commit author 必须用 `266514003+obisoldbee@users.noreply.github.com`（否则会被 GitHub 关联到同名第三方账号）。
- 本机若连不上 GitHub，可让 WorkBuddy 沙箱（已登录 `obisoldbee`、有 `repo` 权限）代推。
- 本仓库是**私有自用**；若要分享单个 skill，直接把对应子目录发给对方即可（它本身就是完整 skill 包）。
