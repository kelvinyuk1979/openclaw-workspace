# 🎯 Polymarket 实盘配置指南

从模拟交易切换到真实 Polymarket API。

---

## 📋 前置条件

1. **Polymarket 账户** - 已注册并验证
2. **API Key** - 从 Polymarket 后台获取
3. **USDC 余额** - 账户内有足够资金
4. **Polygon 钱包** - MetaMask 等支持 Polygon 网络的钱包

---

## 🔑 获取 API Key

1. 登录 https://polymarket.com
2. 进入 **Settings → API**
3. 点击 **Create New Key**
4. 设置权限（建议只给 `trade` 和 `read`）
5. 复制并保存 API Key（只显示一次）

---

## ⚙️ 配置实盘模式

### 1. 编辑配置文件

```bash
cd ~/.openclaw/workspace/polymarket-trading-system
nano config/unified_config.json
```

### 2. 修改配置

```json
{
  "mode": "LIVE",  // 从 "simulation" 改为 "LIVE"
  
  "account": {
    "initial_capital": 10000,
    "currency": "USDC"
  },
  
  "api": {
    "polymarket_key": "YOUR_API_KEY_HERE",
    "wallet_address": "0xYOUR_WALLET_ADDRESS",
    "private_key": "YOUR_PRIVATE_KEY"  // 可选，用于自动签名
  },
  
  "strategies": {
    "quant_core": {
      "enabled": true,
      "allocation": 0.40,
      "live_trading": true  // 启用实盘
    },
    "weather_arb": {
      "enabled": true,
      "allocation": 0.30,
      "live_trading": true
    },
    "event_trading": {
      "enabled": true,
      "allocation": 0.30,
      "live_trading": true
    }
  },
  
  "risk_control": {
    "max_total_exposure": 0.80,
    "stop_loss": -0.10,
    "take_profit": 0.20,
    "daily_loss_limit": -0.05,
    "max_single_bet": 100  // 单笔最大投注（USDC）
  }
}
```

---

## 🚀 启动实盘交易

### 测试模式（推荐先测试）

```bash
# 模拟 API 调用，不实际下单
python3 main.py --dry-run
```

### 实盘模式

```bash
# 真实下单
python3 main.py --live
```

---

## 📊 监控实盘

### Web 看板

访问：http://localhost:5000

- 实时余额
- 持仓详情
- 交易记录
- 盈亏统计

### 日志文件

```bash
# 查看实时日志
tail -f logs/cron.log
tail -f logs/scan.log
```

### 邮件报告

每天 9AM/5PM 自动发送统一报告到配置邮箱。

---

## ⚠️ 风险控制

### 建议配置

| 参数 | 保守 | 中等 | 激进 |
|------|------|------|------|
| 单笔最大 | $50 | $100 | $200 |
| 总仓位 | 50% | 80% | 100% |
| 止损 | -5% | -10% | -15% |
| 止盈 | 10% | 20% | 30% |

### 安全建议

1. **从小额开始** - 先测试 $100-500
2. **设置止损** - 每笔交易必须有止损
3. **定期检查** - 每天查看持仓和盈亏
4. **保留现金** - 至少保留 20% 现金
5. **备份私钥** - 离线保存钱包私钥

---

## 🔄 切换回模拟模式

```json
{
  "mode": "simulation",  // 改回 "simulation"
  "strategies": {
    "quant_core": {"live_trading": false}
  }
}
```

---

## 📞 常见问题

### Q: API Key 无效？
A: 检查权限设置，确保有 `trade` 权限。

### Q: 交易失败？
A: 检查 USDC 余额和 Polygon Gas 费。

### Q: 如何停止实盘？
A: Ctrl+C 停止程序，或设置 `live_trading: false`。

### Q: 亏损怎么办？
A: 立即停止，检查策略参数，调整风险配置。

---

## 📄 相关文件

- 配置：`config/unified_config.json`
- 日志：`logs/cron.log`, `logs/scan.log`
- 交易记录：`simulation.json`
- Web 看板：`web_server.py`

---

**⚠️ 风险提示：** 实盘交易有风险，可能导致本金损失。请谨慎操作！

**最后更新：** 2026-03-19
