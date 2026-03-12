# 🚀 Polymarket Fast Loop

Polymarket 快速交易循环系统 - 自动化预测市场交易

---

## 📋 项目简介

**Polymarket Fast Loop** 是一个用于 Polymarket 预测市场的自动化交易系统。

### 核心功能

- ⚡ **快速循环** - 实时监控市场变化
- 🤖 **自动交易** - 根据策略自动买入/卖出
- 📊 **数据分析** - 市场趋势和赔率分析
- 💰 **套利机会** - 发现跨市场套利机会
- 🔔 **实时提醒** - Telegram 通知重要事件

---

## 🛠️ 安装

### 1. 克隆仓库

```bash
cd /Users/kelvin/.openclaw/workspace
git clone https://github.com/kelvinyuk1979/polymarket-fast-loop.git
cd polymarket-fast-loop
```

### 2. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 3. 配置 API Key

```bash
cp config.example.json config.json
# 编辑 config.json 填入你的 API Key
```

---

## 📁 项目结构

```
polymarket-fast-loop/
├── README.md              # 本文件
├── config.json            # 配置文件
├── requirements.txt       # Python 依赖
├── main.py                # 主程序
├── trader.py              # 交易逻辑
├── monitor.py             # 市场监控
├── analyzer.py            # 数据分析
├── notifier.py            # 通知系统
└── strategies/            # 交易策略
    ├── basic.py           # 基础策略
    ├── arbitrage.py       # 套利策略
    └── momentum.py        # 动量策略
```

---

## 🚀 快速开始

### 1. 基础配置

编辑 `config.json`:

```json
{
  "polymarket": {
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET"
  },
  "telegram": {
    "bot_token": "8652433933:AAEvdtokbbO8R-2zcPTaHx16Sjf9p_Od-gw",
    "chat_id": "5710760402"
  },
  "trading": {
    "max_bet": 100,
    "min_odds": 0.1,
    "stop_loss": 0.2
  }
}
```

### 2. 运行监控

```bash
python3 monitor.py
```

### 3. 启动交易

```bash
python3 main.py
```

---

## 📊 交易策略

### 基础策略 (Basic)

- 低买高卖
- 基于赔率变化
- 适合新手

### 套利策略 (Arbitrage)

- 跨市场套利
- 无风险收益
- 需要快速执行

### 动量策略 (Momentum)

- 跟随市场趋势
- 突破交易
- 高风险高收益

---

## ⚙️ 配置选项

### 交易设置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `max_bet` | 单笔最大投注 | 100 USDC |
| `min_odds` | 最小赔率 | 0.1 |
| `stop_loss` | 止损比例 | 20% |
| `take_profit` | 止盈比例 | 50% |

### 监控设置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `scan_interval` | 扫描间隔 | 5 秒 |
| `market_filter` | 市场筛选 | 热门市场 |
| `volume_min` | 最小交易量 | 1000 USDC |

---

## 🔔 Telegram 通知

已集成 Telegram Bot，自动发送：

- ✅ 交易执行通知
- 📈 盈利/亏损报告
- ⚠️ 风险警告
- 📊 每日总结

**Bot**: @kelvinyukbot

---

## 📈 风险控制

### ⚠️ 重要提示

1. **只用闲钱** - 不要用生活必需资金
2. **设置止损** - 严格执行止损策略
3. **分散投资** - 不要把所有资金投入一个市场
4. **定期复盘** - 每周 review 交易记录

### 安全设置

```json
{
  "risk_management": {
    "daily_limit": 500,      // 每日交易上限
    "position_limit": 5,     // 最大持仓数
    "max_drawdown": 0.3      // 最大回撤
  }
}
```

---

## 🧪 测试

```bash
# 运行测试
python3 -m pytest tests/

# 模拟交易（不使用真实资金）
python3 main.py --dry-run
```

---

## 📝 日志

```bash
# 查看实时日志
tail -f logs/trading.log

# 查看错误日志
tail -f logs/error.log
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## ⚠️ 免责声明

本项目仅供学习研究使用，不构成投资建议。

预测市场交易存在风险，可能导致资金损失。

使用本软件的风险由用户自行承担。

---

**Created by OpenClaw | 2026-03-12**
