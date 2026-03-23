# 📊 三系统统一量化交易配置完成

## ✅ 已配置系统

| 系统 | 市场 | 初始资金 | 自动交易 | 邮件汇报 |
|------|------|----------|----------|----------|
| **Polymarket** | 预测市场 | $10,000 USDC | ✅ 每 15 分钟 | ✅ 上午 9 点 + 下午 5 点 |
| **A 股** | 中国股市 | ¥100,000 CNY | ✅ 每 30 分钟 | ✅ 上午 9 点 + 下午 5 点 |
| **OKX** | 加密货币 | $10,000 USDT | ✅ 每 5 分钟 | ✅ 上午 9 点 + 下午 5 点 |

## 📧 邮件汇报

**发送时间：**
- 上午 9:00（Asia/Shanghai）
- 下午 5:00（Asia/Shanghai）

**收件人：** 4352395@qq.com

**邮件内容：**
- 三个系统总盈亏汇总
- 各系统详细状态（余额、盈亏、收益率）
- OKX 最新交易信号
- 当前持仓情况

## ⏰ 定时任务清单

### 交易检查
| 任务 | 频率 | 状态 |
|------|------|------|
| OKX 量化交易检查 | 每 5 分钟 | ✅ 运行中 |
| 量化交易系统（A 股/其他） | 每 5 分钟 | ✅ 运行中 |
| Polymarket 扫描 | 每 15 分钟 | ✅ 运行中 |
| A 股扫描 | 每 30 分钟 | ✅ 运行中 |

### 邮件汇报
| 任务 | 时间 | 状态 |
|------|------|------|
| 量化交易日报 - 上午 9 点 | 每天 9:00 | ✅ 已配置 |
| 量化交易日报 - 下午 5 点 | 每天 17:00 | ✅ 已配置 |

## 🎯 交易策略

### Polymarket（3 策略）
1. **量化核心** - EV 值套利（40% 资金）
2. **天气套利** - 天气预测市场价差（30% 资金）
3. **事件交易** - 政治/体育事件（30% 资金）

### A 股（3 策略）
1. **技术面** - MA/MACD/RSI/KDJ/布林带（40% 资金）
2. **基本面** - PE/ROE/增长率（35% 资金）
3. **情绪面** - 新闻/社交/资金流（25% 资金）

### OKX（4 策略投票）
1. **动量策略** - RSI 超买超卖
2. **均值回归** - 极端 RSI 反转
3. **MACD 交叉** - 趋势交叉信号
4. **趋势跟随** - MA20/MA50 排列

## 🛑 风险控制

| 系统 | 止损 | 止盈 | 单笔最大 | 最大持仓 |
|------|------|------|----------|----------|
| Polymarket | -10% | +20% | 10% | 根据策略 |
| A 股 | -8% | +15% | 20% | 10 只股票 |
| OKX | -5% | +10% | 10% | 4 个币种 |

## 📁 文件位置

```
~/.openclaw/workspace/
├── trading-daily-report.py        # 统一邮件汇报脚本 ⭐ 新增
├── unified-trading-dashboard/     # 统一看板
│   └── web_server.py              # http://localhost:5002
├── polymarket-trading-system/     # Polymarket 系统
├── a-share-trading-system/        # A 股系统
└── okx-trading-system/            # OKX 系统 ⭐ 新增
```

## 🔧 管理命令

### 查看系统状态
```bash
# Polymarket
cd ~/.openclaw/workspace/polymarket-trading-system
python3 main.py status

# A 股
cd ~/.openclaw/workspace/a-share-trading-system
python3 main.py status

# OKX
cd ~/.openclaw/workspace/okx-trading-system
python3 okx_trading_system.py status
```

### 手动发送邮件
```bash
cd ~/.openclaw/workspace
python3 trading-daily-report.py 上午  # 发送上午版
python3 trading-daily-report.py 下午  # 发送下午版
```

### 查看 cron 任务
```bash
export PATH="/opt/homebrew/bin:/opt/homebrew/Cellar/node@22/22.22.1_1/bin:$PATH"
openclaw cron list
```

## 📊 统一看板

**访问地址：** http://localhost:5002

实时展示三个系统的：
- 账户余额和盈亏
- 当前持仓
- 最新信号
- 策略状态

## ⚠️ 注意事项

1. **模拟交易模式** - 所有系统当前均为模拟交易，不会真实下单
2. **邮件配置** - 使用 QQ 邮箱 SMTP 服务
3. **API 限制** - OKX API 可能受网络影响，已配置重试机制
4. **风险控制** - 实盘前建议充分测试至少 1 个月

## 📈 下一步优化建议

### 已完成 ✅
- [x] OKX 系统创建和集成
- [x] 三系统统一邮件汇报
- [x] 定时任务配置
- [x] 看板集成

### 可考虑加强 🔄
- [ ] 添加实盘交易开关（当前为模拟模式）
- [ ] 增加微信/钉钉通知
- [ ] 添加策略回测功能
- [ ] 增加更多交易对/股票池
- [ ] 动态调整仓位（根据市场波动率）

---

**配置完成时间：** 2026-03-20 13:20  
**配置者：** AI Assistant  
**模式：** 模拟交易 + 邮件汇报
