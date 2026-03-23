# 📊 统一交易系统看板

Polymarket + A 股 统一 Web 控制面板

## 🚀 快速启动

```bash
# 启动看板
./manage.sh start

# 查看状态
./manage.sh status

# 停止看板
./manage.sh stop

# 重启看板
./manage.sh restart
```

## 📍 访问地址

- **本地：** http://localhost:5002
- **局域网：** http://192.168.3.85:5002

## ⚙️ 开机自启动

已配置 launchd 服务，开机自动启动。

```bash
# 启用自启动（默认已启用）
./manage.sh enable-auto

# 禁用自启动
./manage.sh disable-auto
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `web_server.py` | Flask Web 服务器 |
| `manage.sh` | 管理脚本（启动/停止/状态） |
| `start_dashboard.sh` | 启动脚本 |
| `templates/unified_dashboard.html` | 看板页面 |
| `web_server.pid` | 进程 ID 文件 |
| `web_server.log` | 日志文件 |

## 🔧 故障排查

**看板无法启动？**
```bash
# 查看日志
cat web_server.log

# 检查端口占用
lsof -i :5002

# 强制重启
./manage.sh stop
./manage.sh start
```

**开机未自启动？**
```bash
# 检查 launchd 服务状态
launchctl list | grep trading-dashboard

# 重新加载服务
launchctl unload ~/Library/LaunchAgents/com.openclaw.trading-dashboard.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.trading-dashboard.plist
```

---

**配置日期：** 2026-03-20
