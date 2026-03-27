# Polymarket 自动交易系统 - 完整部署指南

## 📋 前提条件

### 1. 非美国 VPS
Polymarket 封锁美国 IP，必须使用非美国 VPS。

**推荐提供商**：
| 提供商 | 位置 | 价格 | 链接 |
|--------|------|------|------|
| DigitalOcean | Amsterdam | $6/月 | digitalocean.com |
| Hetzner | Finland/Germany | $5/月 | hetzner.com |
| Vultr | London/Frankfurt | $6/月 | vultr.com |
| Linode | London/Frankfurt | $5/月 | linode.com |

**创建 VPS 配置**：
- 系统：Ubuntu 22.04 LTS
- 内存：1GB 足够
- 存储：25GB SSD
- 位置：确保不是美国

### 2. 加密货币钱包

**需要的资产**：
- **USDC.e** (Polygon 上的桥接 USDC) - 建议至少$100
- **MATIC** (Gas 费) - 0.1 MATIC 足够数百笔交易

**获取 USDC.e 步骤**：

1. **创建 MetaMask 钱包**
   - 安装 MetaMask 浏览器扩展
   - 创建新钱包，备份助记词
   - 添加 Polygon 网络：
     ```
     Network Name: Polygon
     RPC URL: https://polygon-rpc.com
     Chain ID: 137
     Symbol: MATIC
     Explorer: https://polygonscan.com
     ```

2. **购买并桥接 USDC**
   
   **方法 A：中心化交易所直接提现（推荐）**
   - 在 Binance/OKX/Coinbase 购买 USDC
   - 提现时选择 **Polygon 网络**
   - 地址：你的 MetaMask Polygon 地址
   - ⚠️ 确认选择的是 **USDC.e** 或 **Polygon USDC**，不是 Ethereum USDC
   
   **方法 B：从 Ethereum 桥接**
   - 访问 https://wallet.polygon.technology/bridge
   - 连接钱包
   - 从 Ethereum 桥接 USDC 到 Polygon
   - 会自动转换为 USDC.e
   - Gas 费较高（约$10-30）
   
   **方法 C：从其他链桥接**
   - 使用 https://app.synapseprotocol.com
   - 或 https://hop.exchange
   - 支持从 Arbitrum、Optimism 等链桥接

3. **验证到账**
   - 访问 https://polygonscan.com
   - 输入你的钱包地址
   - 确认 USDC.e 余额

### 3. Anthropic API Key

1. 访问 https://console.anthropic.com
2. 注册/登录账号
3. 创建 API Key
4. 复制密钥（格式：`sk-ant-xxxxxxxx`）
5. 设置账单提醒（可选）

**成本估算**：
- Claude Haiku: ~$0.001/次评估
- 每 10 分钟扫描 40 个市场: ~$0.04
- 每日成本：约$0.5-1

---

## 🚀 部署步骤

### 步骤 1：SSH 登录 VPS

```bash
ssh root@your-vps-ip
```

### 步骤 2：上传部署文件

**方法 A：使用 SCP（推荐）**

在本地电脑执行：
```bash
cd ~/.openclaw/workspace/skills/polymarket-auto-trader/deploy
scp -r * root@your-vps-ip:/opt/
```

**方法 B：在 VPS 上创建文件**

如果无法 SCP，可以在 VPS 上手动创建：

```bash
# 创建目录
mkdir -p /opt/polymarket-trader
cd /opt/polymarket-trader

# 创建 run_trade.py（复制上面生成的内容）
cat > run_trade.py << 'PYTHON_EOF'
...（粘贴 run_trade.py 内容）
PYTHON_EOF
```

### 步骤 3：运行安装脚本

```bash
cd /opt/polymarket-trader
chmod +x setup_vps.sh
./setup_vps.sh
```

### 步骤 4：配置密钥

```bash
cd /opt/polymarket-trader

# 创建.env 文件
cp .env.example .env

# 编辑.env 文件
nano .env

# 填入你的密钥：
# PRIVATE_KEY=你的私钥（不带 0x）
# LLM_API_KEY=sk-ant-你的 Anthropic Key

# 保存退出（Ctrl+X, Y, Enter）

# 设置严格权限
chmod 600 .env
```

### 步骤 5：合约授权

```bash
/opt/trader/bin/python3 approve_contracts.py
```

这会授权 Polymarket 合约使用你的 USDC.e。

### 步骤 6：测试运行

```bash
/opt/trader/bin/python3 run_trade.py
```

观察输出，确认：
- ✅ CLOB 认证成功
- ✅ 扫描到市场
- ✅ LLM 评估正常
- ✅ 有edge时下订单

### 步骤 7：设置定时任务

```bash
crontab -e

# 添加以下行（每 10 分钟运行一次）
*/10 * * * * cd /opt/polymarket-trader && /opt/trader/bin/python3 run_trade.py >> logs/cron.log 2>&1

# 每小时健康检查
0 * * * * cd /opt/polymarket-trader && /opt/trader/bin/python3 health_check.py >> logs/health.log 2>&1

# 保存退出
```

### 步骤 8：监控

```bash
# 查看实时日志
tail -f logs/cron.log

# 查看 P&L
/opt/trader/bin/python3 pnl_tracker.py

# 运行监控脚本
chmod +x monitor.sh
./monitor.sh
```

---

## 📊 系统工作原理

```
每 10 分钟:
├── 扫描 Polymarket 活跃市场（按交易量排序）
├── 筛选：价格 5%-95%，优先 30 天内到期
├── 用 Claude Haiku 评估真实概率
├── 计算优势：|LLM 概率 - 市场价格|
├── 如果优势 > 5%：
│   ├── Kelly 公式计算仓位
│   ├── 半-Kelly，上限 25%
│   └── 下限价单（GTC）
└── 记录交易，避免重复

每日:
└── LLM 预算重置（$5/天）
```

---

## 💰 成本管理

| 项目 | 成本 |
|------|------|
| VPS | $5-10/月 |
| LLM 推理 | ~$0.04/次 |
| 每日运行（144 次） | ~$0.50-1/天 |
| Gas 费 | ~$0.001/交易 |
| **月度总成本** | **约$20-40** |

**建议起始资金**：$500-1000

---

## ⚠️ 风险管理

### 系统风险
- **LLM 可能犯错**：概率评估不保证准确
- **市场波动**：黑天鹅事件可能导致亏损
- **技术故障**：网络问题、API 变更等

### 建议措施
1. **从小资金开始**：先测试$50-100
2. **设置止损**：单市场最大亏损 50%
3. **定期审查**：每周检查交易记录
4. **分散风险**：不相关市场最多 8 个
5. **保留现金**：至少 20% 仓位留作备用

---

## 🔧 故障排查

### 问题：CLOB 认证失败
```
解决：确认 PRIVATE_KEY 正确，签名类型=0（EOA 钱包）
```

### 问题：USDC.e 余额不足
```
解决：桥接更多 USDC.e 到 Polygon
检查：https://polygonscan.com/address/你的地址
```

### 问题：LLM API 错误
```
解决：检查 ANTHROPIC_API_KEY，确认有余额
```

### 问题：没有交易机会
```
正常：市场效率高，可能几天都没有>5% 优势
```

---

## 📈 监控指标

### 每日检查
- [ ] 日志无错误
- [ ] 有新交易记录
- [ ] 余额正常

### 每周检查
- [ ] P&L 汇总
- [ ] 胜率统计
- [ ] LLM 成本审查

### 每月检查
- [ ] 总体回报
- [ ] 策略调整
- [ ] 系统升级

---

## 🎯 下一步

部署完成后：

1. **运行监控脚本**：`./monitor.sh`
2. **设置告警**（可选）：集成 Telegram/Discord 通知
3. **优化参数**：根据表现调整 EDGE_THRESHOLD、仓位等
4. **添加策略**：可以扩展更多交易策略

---

## 📞 支持

遇到问题：
1. 检查日志：`tail -100 logs/cron.log`
2. 运行健康检查：`python3 health_check.py`
3. 查看 P&L：`python3 pnl_tracker.py`

---

**⚠️ 重要提醒**：
- 这是真实资金交易，不是模拟
- 过往表现不代表未来结果
- 只用你能承受损失的资金
- 定期备份私钥和交易记录
