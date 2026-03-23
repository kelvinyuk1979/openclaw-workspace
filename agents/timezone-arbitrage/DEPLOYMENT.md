# 🚀 时区套利 Agent - 部署指南

---

## 📋 部署方式

### 方式 1：本地开发（推荐新手）

适合：测试、调试、学习

```bash
# 1. 克隆/复制项目
cd /Users/kelvin/.openclaw/workspace/agents/timezone-arbitrage

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实 API keys

# 5. 测试运行
python src/main.py --dev

# 6. 生产运行
python src/main.py
```

---

### 方式 2：Docker 部署（推荐生产）

适合：24/7 运行、隔离环境

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填入真实 API keys

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f agent

# 4. 停止服务
docker-compose down
```

**服务包含：**
- Agent 主程序
- PostgreSQL 数据库
- Redis 缓存

---

### 方式 3：云服务器部署

适合：低延迟、高可用

#### AWS EC2

```bash
# 1. 创建 EC2 实例（t3.medium, Ubuntu 22.04）

# 2. 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 部署项目
git clone <repo> timezone-arbitrage
cd timezone-arbitrage
cp .env.example .env
# 编辑 .env

# 5. 启动
docker-compose up -d

# 6. 设置开机自启
sudo systemctl enable docker
```

#### 成本估算

| 服务 | 规格 | 月成本 |
|------|------|--------|
| EC2 | t3.medium | ~$30 |
| RDS (可选) | db.t3.micro | ~$15 |
| 总计 | | ~$45/月 |

---

## ⚙️ 配置说明

### 环境变量（.env）

```bash
# Telegram（必需）
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890

# Polymarket（必需）
POLYMARKET_API_KEY=your_api_key
POLYMARKET_API_SECRET=your_api_secret

# 数据库（Docker 自动配置）
DB_USER=timezone_agent
DB_PASSWORD=secure_password_here

# Redis（Docker 自动配置）
REDIS_PASSWORD=secure_redis_password
```

### 获取 Telegram Bot Token

1. 打开 Telegram，搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示设置 bot 名称
4. 获得 Token（格式：`1234567890:ABCdef...`）

### 获取 Chat ID

1. 把你的 bot 拉到群里（或私聊）
2. 发送一条消息
3. 访问：`https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. 找到 `"chat":{"id":-1001234567890}`

---

## 🔍 监控与日志

### 查看实时日志

```bash
# Docker
docker-compose logs -f agent

# 本地
tail -f logs/agent.log
```

### 关键日志指标

| 日志内容 | 含义 |
|---------|------|
| `发现 X 个套利机会` | 找到可交易机会 |
| `用户未批准，取消交易` | 等待用户确认超时 |
| `订单已全部提交` | 交易执行成功 |
| `全部结算完成` | 利润已到账 |
| `ERROR` | 需要检查错误原因 |

### 设置告警

编辑 `config/config.yaml`：

```yaml
notifications:
  telegram:
    enabled: true
  triggers:
    - event: "error"
      require_approval: false  # 错误立即通知
```

---

## 📊 数据库管理

### 连接数据库

```bash
# Docker
docker-compose exec postgres psql -U timezone_agent -d timezone_arbitrage

# 本地
psql -h localhost -U timezone_agent -d timezone_arbitrage
```

### 常用查询

```sql
-- 查看所有交易
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

-- 查看今日统计
SELECT * FROM performance_stats WHERE date = CURRENT_DATE;

-- 查看胜率
SELECT 
    COUNT(*) as total_trades,
    COUNT(CASE WHEN actual_return > position_size THEN 1 END) as winning_trades,
    COUNT(CASE WHEN actual_return > position_size THEN 1 END) * 100.0 / COUNT(*) as win_rate
FROM trades 
WHERE status = 'settled';
```

### 备份数据库

```bash
# 导出
docker-compose exec postgres pg_dump -U timezone_agent timezone_arbitrage > backup_$(date +%Y%m%d).sql

# 导入
docker-compose exec -T postgres psql -U timezone_agent -d timezone_arbitrage < backup_20260314.sql
```

---

## 🔧 故障排查

### 问题 1：无法连接 Polymarket

**症状：** `ERROR: 下单失败：401 Unauthorized`

**解决：**
```bash
# 检查 API keys
echo $POLYMARKET_API_KEY
echo $POLYMARKET_API_SECRET

# 重启服务
docker-compose restart agent
```

### 问题 2：Telegram 通知不发送

**症状：** 发现机会但没有通知

**解决：**
```bash
# 测试 Bot Token
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# 检查 Chat ID
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
```

### 问题 3：数据库连接失败

**症状：** `ERROR: could not connect to database`

**解决：**
```bash
# 检查 PostgreSQL 是否运行
docker-compose ps

# 重启数据库
docker-compose restart postgres

# 查看数据库日志
docker-compose logs postgres
```

### 问题 4：内存占用过高

**症状：** Agent 占用>500MB 内存

**解决：**
```bash
# 限制 Docker 内存
# 编辑 docker-compose.yml，添加：
services:
  agent:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## 📈 性能优化

### 1. 调整检查频率

编辑 `config/config.yaml`：

```yaml
sources:
  japan_boj:
    check_interval_sec: 60  # 降低频率节省资源
```

### 2. 启用 Redis 缓存

```yaml
redis:
  enabled: true
  cache_ttl: 300  # 5 分钟缓存
```

### 3. 数据库索引优化

```sql
CREATE INDEX CONCURRENTLY idx_trades_created_at ON trades(created_at);
CREATE INDEX CONCURRENTLY idx_signals_processed ON signals(processed);
```

---

## 🔐 安全建议

### 1. 使用 Secrets 管理

不要用 `.env` 文件，改用 Docker Secrets：

```bash
echo "your_secret" | docker secret create polymarket_api_key -
```

### 2. 限制网络访问

```yaml
services:
  postgres:
    ports: []  # 不暴露到外部
  redis:
    ports: []  # 不暴露到外部
```

### 3. 定期更新依赖

```bash
# 每月检查更新
pip list --outdated
pip install --upgrade -r requirements.txt
```

### 4. 审计日志

```yaml
logging:
  audit:
    enabled: true
    retention_days: 90  # 保留 90 天
```

---

## 📞 获取帮助

- **文档：** `README.md`
- **配置示例：** `config/config.yaml`
- **交易日志：** `logs/agent.log`
- **首笔交易记录：** `FIRST_TRADE.md`

---

**最后更新：** 2026-03-14  
**版本：** 1.0.0
