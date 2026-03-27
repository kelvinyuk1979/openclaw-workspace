# 📱 告警通知设置指南

## 方案 A：Telegram 告警（推荐）

### 为什么选择 Telegram？
- ✅ 免费
- ✅ 实时推送
- ✅ 支持 Markdown 格式
- ✅ 可以发送图表和图片
- ✅ 隐私性好（不需要手机号）

---

### 步骤 1：创建 Telegram Bot

**在 Telegram 中操作**：

1. 打开 Telegram App
2. 搜索 `@BotFather`（官方 Bot 创建工具）
3. 点击 Start
4. 发送命令：`/newbot`
5. 输入 Bot 名称：`Polymarket Trader`
6. 输入 Bot 用户名：`poly_trade_alert_bot`（必须以 bot 结尾）
7. BotFather 会返回 Token，格式：
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
8. **保存这个 Token**（后续要用）

---

### 步骤 2：获取 Chat ID

**方法 1：通过 API 获取**

1. 在 Telegram 搜索你刚创建的 Bot
2. 点击 Start 开始对话
3. 访问这个 URL（替换 YOUR_TOKEN）：
   ```
   https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrsTUVwxyz/getUpdates
   ```
4. 找到响应中的 `"chat":{"id":123456789,...}`
5. **保存 Chat ID**（一串数字）

**方法 2：使用现成 Bot**

1. 搜索 `@userinfobot`
2. 点击 Start
3. 它会直接告诉你 Chat ID

---

### 步骤 3：配置告警脚本

**在 VPS 上操作**：

```bash
cd /opt/polymarket-trader

# 运行设置脚本
/opt/trader/bin/python3 telegram_alert.py setup
```

按提示输入：
- Bot Token
- Chat ID

**或手动创建配置文件**：

```bash
cat > telegram_config.json << EOF
{
  "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
  "chat_id": "123456789"
}
EOF
```

---

### 步骤 4：集成到交易脚本

**修改 `run_trade.py`**，在文件开头添加：

```python
# 在 import 部分添加
from telegram_alert import TelegramAlert
alert = TelegramAlert()

# 在交易成功后添加（约第 200 行）
if result:
    alert.send_trade_alert(
        market=market["question"],
        side=side,
        shares=shares,
        price=price_rounded,
        edge=edge,
        status="filled"
    )
```

**在错误处理部分添加**（约第 220 行）：

```python
except Exception as e:
    log.error(f"Trade failed: {e}")
    alert.send_error_alert(str(e))
```

---

### 步骤 5：设置每日总结

**添加 Cron 任务**：

```bash
crontab -e

# 添加每日晚上 10 点发送总结
0 22 * * * cd /opt/polymarket-trader && /opt/trader/bin/python3 -c "
from telegram_alert import TelegramAlert
alert = TelegramAlert()
# 这里需要添加获取当日数据的逻辑
alert.send_daily_summary(trades=5, pnl=12.34, llm_cost=0.50, balance=1234.56)
"
```

---

### 测试告警

```bash
# 发送测试消息
/opt/trader/bin/python3 -c "
from telegram_alert import TelegramAlert
alert = TelegramAlert()
alert.send('✅ Polymarket Trader 测试消息')
"
```

检查 Telegram 是否收到消息。

---

## 方案 B：Discord 告警

### 适用场景
- 已经有 Discord 服务器
- 想要群聊告警
- 需要 Webhook 集成

---

### 步骤 1：创建 Webhook

1. 打开 Discord 服务器
2. 选择要发送告警的频道
3. 点击频道设置 → 整合 → Webhooks
4. 点击新建 Webhook
5. 命名：Polymarket Trader
6. 复制 Webhook URL（格式：`https://discord.com/api/webhooks/...`）

---

### 步骤 2：配置脚本

```bash
cd /opt/polymarket-trader

# 编辑 Discord 告警脚本
nano discord_alert.sh

# 替换这一行：
DISCORD_WEBHOOK_URL="你的 Webhook URL"
```

---

### 步骤 3：测试

```bash
chmod +x discord_alert.sh
./discord_alert.sh "✅ 测试消息"
```

---

## 方案 C：邮件告警

### 适用场景
- 不想装额外 App
- 需要正式报告
- 已有邮件系统

---

### 使用 QQ 邮箱发送（国内推荐）

**步骤 1：获取授权码**

1. 登录 QQ 邮箱网页版
2. 设置 → 账户
3. 开启 POP3/SMTP 服务
4. 生成授权码（不是登录密码！）
5. 保存授权码

---

**步骤 2：创建邮件脚本**

```bash
cat > email_alert.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = '4352395@qq.com'
    msg['To'] = '4352395@qq.com'
    
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login('4352395@qq.com', '你的授权码')
    server.send_message(msg)
    server.quit()
PYTHON_EOF
```

---

## 方案 D：微信告警（通过 Server 酱）

### 适用场景
- 只用微信
- 不想装 Telegram

---

### 步骤

1. 访问 https://sct.ftqq.com
2. 微信扫码登录
3. 获取 SendKey
4. 创建脚本：

```bash
cat > wechat_alert.sh << 'BASH_EOF'
#!/bin/bash
SENDKEY="你的 SendKey"
MESSAGE="$1"

curl -X POST "https://sctapi.ftqq.com/${SENDKEY}.send" \
     -d title="Polymarket 告警" \
     -d desp="$MESSAGE"
BASH_EOF
```

---

## 告警类型和触发条件

### 1. 交易告警（实时）

**触发条件**：
- 新订单成交
- 订单被拒绝
- 仓位平仓

**内容**：
```
✅ 新交易
🟢 方向：YES
📊 市场：BTC > $100K in 2026
💰 股数：50
💵 价格：$0.35
📈 优势：+15%
```

---

### 2. 错误告警（实时）

**触发条件**：
- API 连接失败
- 余额不足
- 合约授权错误
- LLM API 错误

**内容**：
```
🚨 严重错误
❌ CLOB 认证失败
错误：Invalid private key
时间：2026-03-27 10:30
```

---

### 3. 健康检查告警（每小时）

**触发条件**：
- API 不可达
- 余额低于阈值
- 超过 24 小时无交易

**内容**：
```
🏥 健康检查告警
⚠️  API 不可达
⚠️  余额低于$50
时间：2026-03-27 10:00
```

---

### 4. 每日总结（每天 22:00）

**内容**：
```
📊 今日交易总结

📈 交易次数：5
💰 P&L: +$12.34
💸 LLM 成本：$0.50
💵 余额：$1,234.56

日期：2026-03-27
```

---

## 推荐配置

| 告警类型 | Telegram | Discord | 邮件 | 微信 |
|----------|----------|---------|------|------|
| 交易告警 | ✅ 实时 | ✅ 实时 | ❌ | ⚠️ 可能延迟 |
| 错误告警 | ✅ 实时 | ✅ 实时 | ⚠️ 延迟 | ⚠️ 延迟 |
| 健康检查 | ✅ | ✅ | ❌ | ❌ |
| 每日总结 | ✅ | ✅ | ✅ | ✅ |

**推荐组合**：
- **主力**：Telegram（所有告警）
- **备用**：邮件（每日总结）

---

## 完整集成示例

**修改 `run_trade.py`**：

```python
# 在文件开头
from telegram_alert import TelegramAlert
alert = TelegramAlert()

# 在主循环开始
log.info("Starting trading cycle...")
alert.send("🔄 开始新一轮交易检查...")

# 在交易成功时
if result:
    trades_placed += 1
    alert.send_trade_alert(
        market=market["question"],
        side=side,
        shares=shares,
        price=price_rounded,
        edge=edge,
        status="filled"
    )

# 在错误时
except Exception as e:
    log.error(f"Error: {e}")
    alert.send_error_alert(f"交易错误：{str(e)[:200]}")

# 在结束时
log.info(f"Cycle complete: {trades_placed} trades")
if trades_placed > 0:
    alert.send(f"✅ 本轮完成 {trades_placed} 笔交易")
```

---

## 成本对比

| 方案 | 成本 | 延迟 | 可靠性 | 推荐度 |
|------|------|------|--------|--------|
| Telegram | 免费 | <1 秒 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Discord | 免费 | <1 秒 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 邮件 | 免费 | 1-5 分钟 | ⭐⭐⭐ | ⭐⭐ |
| 微信 | 免费 | 1-10 分钟 | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 故障排查

### Telegram 收不到消息

```bash
# 检查配置
cat telegram_config.json

# 测试 API
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# 检查 Bot 是否被拉黑
# 在 Telegram 中重新搜索 Bot，点击 Start
```

### 消息格式错误

- 确保 Markdown 语法正确
- 消息长度不超过 4000 字符
- 特殊字符要转义

---

## 下一步

配置完成后：

1. ✅ 测试所有告警类型
2. ✅ 调整告警频率（避免骚扰）
3. ✅ 设置免打扰时段（可选）
4. ✅ 定期检查告警日志

**需要我帮你**：
- 创建完整的集成代码？
- 设置告警频率限制？
- 添加更多告警类型？

告诉我！🚀
