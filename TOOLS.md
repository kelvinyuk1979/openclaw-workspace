# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## API Keys

配置位置：`api-keys.json`

切换命令：
```bash
./switch-api-key.sh primary    # 切换到主密钥
./switch-api-key.sh backup     # 切换到备用密钥
./switch-api-key.sh set-backup # 设置新的备用密钥
./switch-api-key.sh status     # 查看当前状态
```

## 模型切换 (OpenClaw)

切换命令：
```bash
./switch-model.sh gemini   # 切换主模型为 Gemini
./switch-model.sh qwen     # 切换主模型为 Qwen (DashScope)
./switch-model.sh status   # 查看当前主模型
```
*注意：每次执行 `switch-model.sh` 切换之后，必须运行 `openclaw gateway restart` 使其生效。*
