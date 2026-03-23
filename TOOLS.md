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

---

## 🧩 精选技能清单 (2026-03-20)

_折腾半个月、试用 200+ 技能后真正留下来的精华_

| 技能 | 安装命令 | 用途 | 状态 |
|------|----------|------|------|
| **agent-browser** | `npx skills add vercel-labs/agent-browser@agent-browser` | 网页爬取自动化，龙虾自己操作浏览器 | ✅ 已安装 |
| **bb-browser** | `npx skills add epiral/bb-browser@bb-browser` | 免登录神器，复用本地浏览器登录态 | ❌ 已禁用 (高风险) |
| **opencli** | `npx skills add joeseesun/opencli-skill@opencli` | 18 平台命令行化 (B 站/某乎/小红书/X/Reddit/GitHub 等) | ✅ 已安装 |
| **skill-vetter** | `npx skills add useai-pro/openclaw-skills-security@skill-vetter` | 安装前安全扫描 (网络外发/敏感变量/可疑代码) | ✅ 已安装 |
| **self-improving-agent** | `npx skills add charon-fan/agent-playbook@self-improving-agent` | 自动复盘，把纠正变知识卡片 | ✅ 已有 (workspace) |
| **lossless-claw** | `npx skills add Martian-Engineering/lossless-claw` | 长记忆 + 树状摘要，控制 Token 消耗 | ❌ 无效 SKILL.md |
| **control-center** | `npx skills add aradotso/trending-skills@openclaw-control-center` | 多实例监控仪表盘 (Token 消耗/健康状态/记忆管理) | ✅ 已安装 |
| **openclaw-backup** | `npx skills add theagentservice/skills@openclaw-backup` | 配置/记忆/对话一键备份回档 | ✅ 已安装 |

**安装位置：** `~/.agents/skills/`

## 模型切换 (OpenClaw)

切换命令：
```bash
./switch-model.sh gemini   # 切换主模型为 Gemini
./switch-model.sh qwen     # 切换主模型为 Qwen (DashScope)
./switch-model.sh status   # 查看当前主模型
```
*注意：每次执行 `switch-model.sh` 切换之后，必须运行 `openclaw gateway restart` 使其生效。*

---

## 💹 交易技能

### Day Trading Investor Pro

**位置：** `skills/day-trading-pro/`

**用途：**
- 学习技术指标（RSI、MACD、VWAP、K 线形态）
- 计算仓位和止损
- 验证交易策略
- 风险管理建议

### TradingView 量化分析

**位置：** `skills/stock-market-pro/tradingview-quant/`

**用途：**
- 智能选股（多因子评分）
- 技术形态识别（双底、头肩顶等）
- 市场复盘（热点板块、资金流向）
- 个股深度分析（技术面 + 基本面 + 新闻）
- 仓位管理（Kelly 公式、止损止盈）
- 事件驱动分析（财报日历、经济数据）

### 量化自动交易系统

**位置：** `skills/stock-market-pro/quant-trading-system/`

**用途：**
- 4 策略投票决策（动量、均值回归、MACD、超级趋势）
- 自动开平仓
- 止损止盈（-5%/+10%）
- 模拟交易（$10K 虚拟资金）

**支持币种：** BTC、ETH、SOL、XRP

**模式：** 模拟交易 → 实盘交易

**配置：** Hyperliquid API（免费）

### 量化策略回测 (Backtrader)

**位置：** `skills/stock-market-pro/quant-trading-backtrader/`

**用途：**
- 策略开发和回测
- 参数优化（自动寻找最优参数）
- 性能分析（夏普比率、最大回撤、胜率）
- 多标的组合回测

**内置指标：** SMA/EMA/RSI/MACD/布林带等

**最佳实践：**
- 前向分析避免过拟合
- 样本外验证
- 考虑手续费和滑点

**配置：** Python + Backtrader（免费开源）

**支持市场：** A 股、美股、港股、加密货币、外汇、期货

**配置：** 需要申请 RapidAPI Key（免费）
https://rapidapi.com/hypier/api/tradingview-data1

**使用示例：**
```
- "什么是 RSI 背离？如何交易？"
- "账户$10K，风险 2%，止损 5%，能买多少？"
- "帮我看看这个交易计划是否合理"
```

**配套资源：**
- GitHub: https://github.com/yoavfael/day-trading-skill
- ClawHub: https://clawhub.ai/yoavfael/day-trading-skill

### 时区套利 Agent

**位置：** `agents/timezone-arbitrage/`

**策略：** 利用跨时区信息差，在预测市场套利
**首笔交易：** 2026-03-14，$12K → $43.8K（+365%）

---
