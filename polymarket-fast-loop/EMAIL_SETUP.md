# 📧 邮件推送配置指南

**目标**: 每天 8:00 自动发送 Polymarket 日报到 4352395@qq.com

---

## 方案 1: QQ 邮箱 SMTP（推荐⭐，免费）

### 第 1 步：获取 QQ 邮箱授权码

1. 登录 QQ 邮箱网页版：https://mail.qq.com
2. 点击 **设置** → **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务**
4. 开启 **IMAP/SMTP 服务**
5. 点击 **生成授权码**
6. 按提示发送短信验证
7. 复制生成的授权码（16 位字母）

### 第 2 步：配置发件人邮箱

编辑配置文件：
```bash
nano /Users/kelvin/.openclaw/workspace/polymarket-fast-loop/.env
```

填入：
```bash
# QQ 邮箱配置
SENDER_EMAIL=你的 QQ 号@qq.com
SENDER_AUTH_CODE=你的授权码（16 位）
RECEIVER_EMAIL=4352395@qq.com
```

### 第 3 步：测试发送

```bash
cd /Users/kelvin/.openclaw/workspace/polymarket-fast-loop
python3 send_email.py --to 4352395@qq.com
```

---

## 方案 2: 使用系统邮件（如果已配置）

如果 macOS 已配置邮件：

```bash
# 测试
echo "测试邮件" | mail -s "测试" 4352395@qq.com
```

---

## 方案 3: 第三方邮件 API（高级）

### SendGrid（每月免费 100 封）

1. 注册：https://sendgrid.com
2. 创建 API Key
3. 设置环境变量：
   ```bash
   export SENDGRID_API_KEY=你的_API_Key
   ```

### 阿里云邮件推送（便宜）

- 国内到达率高
- 每天免费 200 封
- https://www.aliyun.com/product/directmail

---

## ⚙️ 自动发送配置

### 修改 Cron Job

编辑现有的每日日报 Cron，添加邮件发送：

```bash
# 查看现有 Cron
openclaw cron list
```

更新为每天 8:00 运行 `send_email.py`

---

## 📝 邮件内容示例

```
主题：📊 Polymarket 每日交易报告 - 2026-03-13

📊 Polymarket 每日交易报告
**日期**: 2026-03-13 Friday

## 🌐 市场概览
- 热门市场：31 个
- 总交易量：$3,556,801,000

## 📈 策略信号
发现 5 个交易机会...

## 💡 今日建议
最佳机会：高价买入 NO
置信度：90%
```

---

## 🚀 快速开始

**最简单的方案**：使用你的 QQ 邮箱发件

1. 打开 QQ 邮箱 → 设置 → 账户
2. 开启 SMTP 服务，获取授权码
3. 运行：
   ```bash
   cd /Users/kelvin/.openclaw/workspace/polymarket-fast-loop
   nano .env
   # 填入 SENDER_EMAIL=你的 QQ 号@qq.com
   # 填入 SENDER_AUTH_CODE=授权码
   python3 send_email.py --to 4352395@qq.com
   ```

---

## ❓ 常见问题

### Q: 授权码是什么？
A: QQ 邮箱的安全验证机制，不是登录密码。在设置→账户中生成。

### Q: 邮件被当作垃圾邮件？
A: 第一次发送可能需要确认，后续会正常。

### Q: 能自定义发送时间吗？
A: 可以，修改 Cron 表达式即可。

---

**需要我帮你配置吗？** 告诉我你的 QQ 邮箱号码，我指导你完成！
