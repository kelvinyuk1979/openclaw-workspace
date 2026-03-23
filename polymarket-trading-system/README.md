# 🤖 Polymarket 统一交易系统

整合了三个独立策略的统一量化交易平台。

## 📊 策略组成

| 策略 | 资金来源 | 核心逻辑 | 扫描频率 |
|------|----------|----------|----------|
| **量化核心** | 40% | EV/贝叶斯/凯利/KL 散度/基础率 | 可配置（默认 15 分钟） |
| **天气套利** | 30% | NWS 气象数据 vs Polymarket 盘口 | 可配置（默认手动） |
| **事件交易** | 30% | 政治/经济/事件预测 | 可配置（默认手动） |

## 🚀 快速开始

### 1. 配置

编辑 `config/unified_config.json`:

```json
{
  "mode": "simulation",
  "account": {"initial_capital": 10000},
  "strategies": {
    "quant_core": {"enabled": true, "allocation": 0.40},
    "weather_arb": {"enabled": true, "allocation": 0.30},
    "event_trading": {"enabled": true, "allocation": 0.30}
  }
}
```

### 2. 运行

```bash
cd polymarket-trading-system
python3 main.py
```

### 3. 定时任务（OpenClaw Cron）

系统已配置 OpenClaw 定时任务，每天 9:00 AM 和 5:00 PM 自动运行并发送邮件。

## 📁 项目结构

```
polymarket-trading-system/
├── config/
│   └── unified_config.json    # 统一配置
├── strategies/
│   ├── quant_core/            # 量化核心策略
│   ├── weather_arb/           # 天气套利策略
│   └── event_trading/         # 事件交易策略
├── reports/
│   └── daily_report.py        # 统一邮件报告
├── logs/                      # 运行日志
├── data/                      # 缓存数据
├── drafts/                    # 邮件草稿
├── main.py                    # 主入口
└── README.md                  # 本文档
```

## ⚙️ 配置说明

### 策略开关

```json
"strategies": {
  "quant_core": {
    "enabled": true,
    "allocation": 0.40,
    "scan_interval_minutes": 15
  }
}
```

### 风险控制

```json
"risk_control": {
  "max_total_exposure": 0.80,
  "stop_loss": -0.10,
  "take_profit": 0.20,
  "daily_loss_limit": -0.05
}
```

### 邮件配置

```json
"email": {
  "enabled": true,
  "to": "4352395@qq.com",
  "smtp_server": "smtp.qq.com",
  "smtp_port": 587
}
```

## 📧 邮件报告

统一报告包含：
- 账户概览（余额、盈亏、收益率）
- 各策略表现（信号数、交易数）
- 今日汇总
- 策略配置状态

**发送时间：** 每天 9:00 AM 和 5:00 PM（Asia/Shanghai）

## 🔄 迁移说明

本项目整合了以下三个独立项目：

| 原项目 | 新位置 | 状态 |
|--------|--------|------|
| `polymarket-quant-bot` | `strategies/quant_core/` | ✅ 已迁移 |
| `polymarket-weather-bot` | `strategies/weather_arb/` | ✅ 已迁移 |
| `polymarket-fast-loop` | `strategies/event_trading/` | ✅ 已迁移 |

**原项目保留**，测试稳定后可手动删除。

## ⚠️ 风险提示

- **模拟交易** - 当前为模拟模式，不构成投资建议
- **历史数据** - 回测结果不代表未来表现
- **市场风险** - 预测市场波动大，可能损失本金
- **技术风险** - API 故障、网络问题等

---

**版本：** 1.0  
**最后更新：** 2026-03-19  
**联系：** 4352395@qq.com
