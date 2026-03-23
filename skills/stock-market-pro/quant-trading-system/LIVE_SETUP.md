# 🎯 实盘交易配置指南

当前系统支持以下交易所：

---

## 📊 支持的交易所

| 交易所 | 支持市场 | API 文档 | 推荐度 |
|--------|----------|----------|--------|
| **OKX** | 现货/合约 | [OKX API](https://www.okx.com/docs-v5/zh/) | ⭐⭐⭐⭐⭐ |
| **Binance** | 现货/合约 | [Binance API](https://binance-docs.github.io/apidocs/) | ⭐⭐⭐⭐ |
| **Hyperliquid** | 合约 | [Hyperliquid API](https://hyperliquid.gitbook.io/) | ⭐⭐⭐⭐ |
| **Bybit** | 现货/合约 | [Bybit API](https://bybit-exchange.github.io/docs/) | ⭐⭐⭐ |

---

## 🔑 配置步骤

### 1. 选择交易所

**推荐：OKX**
- ✅ 流动性好
- ✅ API 稳定
- ✅ 支持中国用户
- ✅ 手续费低

### 2. 获取 API Key

以 OKX 为例：

1. 登录 https://www.okx.com
2. 进入 **个人中心 → API 管理**
3. 点击 **创建 API**
4. 设置权限：
   - ✅ 读取权限
   - ✅ 交易权限
   - ❌ 提现权限（安全）
5. 保存：
   - API Key
   - Secret Key
   - Passphrase

### 3. 配置到系统

创建配置文件：

```bash
cd /Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system
nano config_live.json
```

内容：

```json
{
  "mode": "live",
  "exchange": "okx",
  "api_key": "YOUR_API_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "passphrase": "YOUR_PASSPHRASE",
  "testnet": true,
  "initial_capital": 10000,
  "risk_control": {
    "max_position_pct": 0.10,
    "stop_loss": -0.05,
    "take_profit": 0.10,
    "max_positions": 4
  }
}
```

### 4. 测试连接

```bash
python3 test_api.py
```

### 5. 切换实盘

```bash
# 模拟盘 → 实盘
python3 switch_mode.py live
```

---

## ⚠️ 风险提示

1. **先测试网** - OKX/Bybit 都有测试网
2. **小额开始** - 先测试 $100-500
3. **设置止损** - 每笔交易必须有止损
4. **监控日志** - 实时查看交易执行
5. **保留现金** - 至少 20% 现金储备

---

## 📞 下一步

**请告诉我：**

1. **选择哪个交易所？** (OKX/Binance/Hyperliquid/Bybit)
2. **已有 API Key 吗？** (有/没有)
3. **先测试网还是直接实盘？** (测试网/实盘)

我会帮你配置好。
