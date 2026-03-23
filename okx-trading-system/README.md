# ₿ OKX 量化交易系统

加密货币自动交易系统 - 多策略投票 + 模拟交易

## 🚀 快速开始

### 1. 运行交易检查

```bash
cd ~/.openclaw/workspace/okx-trading-system

# 查看状态
python3 okx_trading_system.py status

# 运行一次交易检查
python3 okx_trading_system.py run

# 重置账户
python3 okx_trading_system.py reset
```

### 2. 配置

编辑 `config/config.json`:

```json
{
  "api_key": "your_api_key",
  "secret_key": "your_secret_key",
  "mode": "simulation",  // simulation 或 live
  "initial_capital": 10000,
  "symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"]
}
```

## 📊 核心特性

| 特性 | 说明 |
|------|------|
| 🗳️ **多策略投票** | 4 种策略共识决策 |
| 💰 **自动仓位** | 每笔最大 10% 资金 |
| 🛑 **止损止盈** | -5% 止损，+10% 止盈 |
| 📡 **OKX API** | 实时行情数据 |
| 🧪 **模拟交易** | 虚拟$10,000 USDT 起步 |

## 🎯 4 大策略

| 策略 | 原理 | 信号条件 |
|------|------|----------|
| 动量 | RSI 超买超卖 | RSI<40 多，RSI>60 空 |
| 均值回归 | 极端 RSI 反转 | RSI<30 多，RSI>70 空 |
| MACD | 趋势交叉 | MACD>Signal 多，反之空 |
| 趋势 | 均线排列 | 价格>MA20>MA50 多，反之空 |

## 📁 文件结构

```
okx-trading-system/
├── config/
│   └── config.json        # API 配置
├── data/
│   ├── account.json       # 账户数据
│   ├── positions.json     # 持仓数据
│   └── trades.json        # 交易记录
├── logs/
│   └── latest_signals.json # 最新信号
├── okx_client.py          # OKX API 客户端
├── okx_trading_system.py  # 交易系统主程序
└── README.md
```

## 🔧 定时任务

系统已配置 cron 任务，每 5 分钟自动检查：

```bash
# 查看 cron 状态
openclaw cron list

# 手动触发检查
python3 okx_trading_system.py run
```

## 📈 看板集成

OKX 系统已集成到统一看板：

- **访问地址：** http://localhost:5002
- **展示内容：** 账户余额、持仓、最新信号

## ⚠️ 风险提示

- **模拟交易** 不代表实盘表现
- 加密货币波动大，谨慎投资
- 不要投资输不起的钱
- 建议先模拟测试至少 1 个月

## 📊 当前配置

- **模式：** 模拟交易
- **初始资金：** $10,000 USDT
- **支持币种：** BTC, ETH, SOL, XRP
- **止损：** -5%
- **止盈：** +10%
- **检查间隔：** 5 分钟

---

**创建日期：** 2026-03-20  
**API:** OKX  
**模式：** 模拟交易
