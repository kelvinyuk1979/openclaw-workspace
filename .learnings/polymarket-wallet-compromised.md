# 🔒 安全事件：Polymarket 钱包私钥泄露

**日期:** 2026-03-26  
**严重程度:** 🔴 **严重**  
**状态:** 已处理

---

## 📋 事件经过

### 时间线

| 时间 | 事件 |
|------|------|
| 2026-03-25 09:05 | 第一笔 POL 被盗 (1.746 POL) |
| 2026-03-26 03:46 | OKX 充值 1.943 POL 到账 |
| 2026-03-26 03:46 | 充值立即被盗转 |
| 2026-03-26 17:50 | 发现并清理泄露源 |

### 损失

- **POL:** ~3.7 POL (约 $0.35)
- **USDC/USDT0:** 用户已提前转出，无损失

---

## 🔍 泄露原因

### 根本原因

**私钥被硬编码在多个测试文件中：**

1. `polymarket-trading-system/strategies/event_trading/test_api.py` ❌
2. `polymarket-fast-loop/test_api.py` ❌
3. `polymarket-fast-loop/config.json` ❌
4. `scripts/polymarket_dry_run.py` ❌

### 攻击方式

1. 攻击者扫描 GitHub 仓库中的私钥
2. 自动监控泄露的钱包地址
3. 一旦有钱到账，几秒内自动转走
4. 使用高 Gas 费确保交易优先确认

### 攻击者地址

- **地址:** `0x4bAa613A...83954c441`
- **标记:** Fake_Phishing2387864 (Polygonscan)
- **交易哈希:** `0xa1225f0535...`

---

## ✅ 处理措施

### 已完成

- [x] 删除所有硬编码私钥的文件
- [x] 清理 wallet_config.json 中的私钥
- [x] 更新 .gitignore 保护配置文件
- [x] 提交清理到 git
- [x] 生成新钱包
- [x] 记录安全事件

### 待完成

- [ ] 从 OKX 提现 POL 到新钱包
- [ ] 测试新钱包小额交易
- [ ] 审查所有代码确保无私钥硬编码
- [ ] 设置环境变量管理敏感配置

---

## 📚 教训与改进

### 永远不要

1. ❌ 硬编码私钥到代码
2. ❌ 提交配置文件到 git
3. ❌ 在测试文件中使用真实私钥
4. ❌ 在不安全的地方存储私钥

### 正确做法

1. ✅ 使用环境变量
2. ✅ 使用 .gitignore 保护敏感文件
3. ✅ 使用加密配置管理工具
4. ✅ 测试使用测试网/假私钥
5. ✅ 定期审计代码库

### 配置模板

```bash
# .env (加入 .gitignore)
POLYMARKET_WALLET_ADDRESS=0x...
POLYMARKET_PRIVATE_KEY=0x...
```

```python
# 代码中读取
import os
private_key = os.environ.get('POLYMARKET_PRIVATE_KEY')
```

---

## 🆕 新钱包信息

**地址:** `0x4d392Ed1b9b8c830A4aCF7A997B851b20d9e96eb`  
**创建日期:** 2026-03-26  
**配置文件:** `polymarket-trading-system/config/wallet_config_new.json`

⚠️ **旧钱包地址 (已泄露，请勿使用):** `0x099fCE3812cb2c8fb76D11Cc804832235e4F174b`

---

**记录人:** OpenClaw Agent  
**审核:** 待用户确认
