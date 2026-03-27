# 📦 Polymarket 自动交易 - 部署检查清单

## ✅ 任务 1：完整脚本文件（已完成）

已生成以下文件到：`~/.openclaw/workspace/skills/polymarket-auto-trader/deploy/`

| 文件 | 用途 | 大小 |
|------|------|------|
| `setup_vps.sh` | VPS 环境安装脚本 | 1.4KB |
| `run_trade.py` | 主交易脚本 | 13KB |
| `pnl_tracker.py` | P&L 查询工具 | 5.6KB |
| `approve_contracts.py` | 合约授权脚本 | 4.4KB |
| `health_check.py` | 健康检查脚本 | 4.3KB |
| `monitor.sh` | 监控面板脚本 | 1.7KB |
| `.env.example` | 配置模板 | 507B |
| `.gitignore` | Git 忽略规则 | 107B |
| `DEPLOYMENT_GUIDE.md` | 完整部署指南 | 4.5KB |

**复制到 VPS 命令**：
```bash
cd ~/.openclaw/workspace/skills/polymarket-auto-trader/deploy
scp -r * root@your-vps-ip:/opt/polymarket-trader/
```

---

## ⚠️ 任务 2：API Key 配置检查

**Anthropic API Key**：未找到配置文件

**你需要**：
1. 访问 https://console.anthropic.com
2. 注册/登录账号
3. 创建 API Key
4. 复制密钥（格式：`sk-ant-xxxxxxxx`）

**部署时填入**：
```bash
# 在 VPS 上编辑.env 文件
nano /opt/polymarket-trader/.env

# 填入：
LLM_API_KEY=sk-ant-你的密钥
PRIVATE_KEY=你的 Polygon 钱包私钥
```

---

## 💰 任务 3：获取 USDC.e 到 Polygon

### 方法 A：交易所直接提现（推荐，便宜）

1. **在交易所购买 USDC**
   - OKX/Binance/Coinbase 都可以
   - 购买至少$100 等值 USDC

2. **提现到 Polygon 网络**
   - 地址：你的 MetaMask Polygon 地址
   - 网络：**Polygon**（不是 Ethereum！）
   - 币种：确认是 **USDC.e** 或 **USDC (Polygon)**
   
3. **验证到账**
   - 访问 https://polygonscan.com
   - 输入你的地址查看余额

### 方法 B：从 Ethereum 桥接（贵，慢）

1. 访问 https://wallet.polygon.technology/bridge
2. 连接钱包
3. 桥接 USDC 到 Polygon
4. Gas 费约$10-30

### 方法 C：跨链桥（中等成本）

- https://app.synapseprotocol.com
- https://hop.exchange
- 支持从 Arbitrum、Optimism 等链桥接

---

## 📊 任务 4：监控脚本（已完成）

### 监控脚本功能

**monitor.sh** - 快速状态面板：
```bash
./monitor.sh
```

显示：
- ✅ 运行状态
- 📅 Cron 计划任务
- 📜 最近 5 笔交易
- 💰 P&L 汇总
- 📝 最新日志
- 💾 磁盘使用

**health_check.py** - 健康检查：
```bash
/opt/trader/bin/python3 health_check.py
```

检查：
- API 连接状态
- 钱包余额
- 最近交易活动
- 告警通知

**pnl_tracker.py** - P&L 详情：
```bash
/opt/trader/bin/python3 pnl_tracker.py
```

显示：
- USDC.e 余额
- 当前持仓
- 未实现盈亏
- 交易历史

---

## 🚀 快速部署流程

### 1. 准备阶段（30 分钟）
- [ ] 购买 VPS（DigitalOcean/Hetzner）
- [ ] 创建 MetaMask 钱包
- [ ] 购买并桥接 USDC.e（至少$100）
- [ ] 申请 Anthropic API Key

### 2. 部署阶段（15 分钟）
```bash
# 本地执行
cd ~/.openclaw/workspace/skills/polymarket-auto-trader/deploy
scp -r * root@your-vps-ip:/opt/polymarket-trader/

# VPS 执行
ssh root@your-vps-ip
cd /opt/polymarket-trader
chmod +x setup_vps.sh
./setup_vps.sh

# 配置密钥
cp .env.example .env
nano .env  # 填入密钥
chmod 600 .env

# 合约授权
/opt/trader/bin/python3 approve_contracts.py

# 测试运行
/opt/trader/bin/python3 run_trade.py
```

### 3. 自动化（5 分钟）
```bash
crontab -e
# 添加：
*/10 * * * * cd /opt/polymarket-trader && /opt/trader/bin/python3 run_trade.py >> logs/cron.log 2>&1
0 * * * * cd /opt/polymarket-trader && /opt/trader/bin/python3 health_check.py >> logs/health.log 2>&1
```

### 4. 监控
```bash
# 随时查看状态
./monitor.sh

# 实时日志
tail -f logs/cron.log

# P&L 查询
/opt/trader/bin/python3 pnl_tracker.py
```

---

## 📋 成本预算

| 项目 | 金额 |
|------|------|
| VPS（月） | $6 |
| USDC.e（起始） | $100-500 |
| MATIC（Gas） | $5 |
| Anthropic API（月） | $15-30 |
| **总计启动** | **约$130-550** |

**建议**：先用$100 测试，确认系统正常后再增加资金

---

## ⚠️ 风险提示

1. **交易风险**：量化策略可能亏损
2. **技术风险**：代码 bug、API 变更
3. **安全风险**：私钥泄露、VPS 被黑
4. **监管风险**：Polymarket 政策变化

**建议**：
- 只用能承受损失的资金
- 定期备份私钥
- 使用专用钱包（不放其他资产）
- 每周审查交易记录

---

## 🎯 下一步行动

**立即执行**：
1. [ ] 购买 VPS
2. [ ] 创建钱包并桥接 USDC.e
3. [ ] 申请 Anthropic API Key
4. [ ] 上传脚本到 VPS
5. [ ] 测试运行

**完成后**：
- 运行 `./monitor.sh` 查看状态
- 设置 Telegram/Discord 告警（可选）
- 根据表现调整参数

---

**需要帮助？**

查看完整指南：`DEPLOYMENT_GUIDE.md`

或问我：
- "如何配置 VPS？"
- "USDC.e 怎么桥接？"
- "参数如何优化？"
