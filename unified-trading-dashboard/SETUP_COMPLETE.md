# 🌐 统一交易系统 - 完整配置文档

## 📊 系统总览

现已配置完成 **3 个交易系统**，统一集成到一个看板：

| 系统 | 市场 | 初始资金 | 状态 |
|------|------|----------|------|
| **Polymarket** | 预测市场 | $10,000 USDC | ✅ 运行中 |
| **A 股** | 中国股市 | ¥100,000 CNY | ✅ 运行中 |
| **OKX** | 加密货币 | $10,000 USDT | ✅ 运行中 |

## 🎯 访问看板

**地址：** http://localhost:5002

看板展示：
- 三个系统的账户余额、盈亏、收益率
- 实时交易信号
- 当前持仓
- 策略状态

## 📁 系统位置

```
~/.openclaw/workspace/
├── unified-trading-dashboard/    # 统一看板
│   ├── web_server.py             # Flask 服务器
│   ├── manage.sh                 # 管理脚本
│   └── templates/
│       └── unified_dashboard.html
│
├── polymarket-trading-system/    # Polymarket 系统
├── a-share-trading-system/       # A 股系统
└── okx-trading-system/           # OKX 系统 (新增)
    ├── config/
    │   └── config.json           # API 配置
    ├── data/
    │   ├── account.json          # 账户数据
    │   ├── positions.json        # 持仓数据
    │   └── trades.json           # 交易记录
    ├── logs/
    │   └── latest_signals.json   # 最新信号
    ├── okx_client.py             # OKX API 客户端
    ├── okx_trading_system.py     # 交易系统
    └── README.md
```

## 🔧 管理命令

### 统一看板

```bash
cd ~/.openclaw/workspace/unified-trading-dashboard

./manage.sh start    # 启动看板
./manage.sh stop     # 停止看板
./manage.sh restart  # 重启看板
./manage.sh status   # 查看状态
```

### OKX 交易系统

```bash
cd ~/.openclaw/workspace/okx-trading-system

python3 okx_trading_system.py status  # 查看状态
python3 okx_trading_system.py run     # 运行一次检查
python3 okx_trading_system.py reset   # 重置账户
```

## ⏰ 定时任务

| 系统 | 检查频率 | Cron 状态 |
|------|----------|----------|
| Polymarket | 每 15 分钟 | ✅ 已配置 |
| A 股 | 每 30 分钟 (交易时间) | ✅ 已配置 |
| OKX | 每 5 分钟 | ✅ 已配置 |

## 🎯 OKX 系统策略

4 策略投票系统，需要至少 3 票才执行交易：

1. **动量策略** - RSI < 40 做多，RSI > 60 做空
2. **均值回归** - RSI < 30 做多，RSI > 70 做空
3. **MACD 交叉** - MACD > Signal 做多，反之做空
4. **趋势跟随** - 价格 > MA20 > MA50 做多，反之做空

## 🛑 风险控制

- 单笔最大仓位：10%
- 止损：-5%
- 止盈：+10%
- 最大持仓数：4 个币种
- 支持币种：BTC, ETH, SOL, XRP

## 📝 OKX API 配置

已配置 API（模拟模式）：

```json
{
  "api_key": "bdbaa8d5-0551-4533-b446-fb7306744a77",
  "secret_key": "1B878CF7403705D3D4C994698C055435",
  "mode": "simulation",
  "initial_capital": 10000
}
```

**注意：** 当前为模拟交易模式，不会真实下单。

## ⚠️ 注意事项

1. **OKX API 连接** - 可能需要检查网络连接或 API 权限
2. **模拟交易** - 所有交易均为模拟，不代表实盘表现
3. **看板自启动** - 已配置 launchd，开机自动启动
4. **数据安全** - API 密钥存储在本地配置文件中

## 🚀 下一步

### 立即可用
- ✅ 访问看板查看三个系统状态
- ✅ 手动运行 OKX 交易检查
- ✅ 查看交易信号和持仓

### 后续优化
- 测试 OKX API 连接（可能需要调整网络设置）
- 根据实际表现调整策略参数
- 考虑实盘前充分模拟测试

---

**配置完成时间：** 2026-03-20 09:32  
**看板地址：** http://localhost:5002
