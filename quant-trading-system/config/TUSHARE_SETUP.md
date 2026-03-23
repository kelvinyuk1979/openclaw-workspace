# 📊 Tushare 数据源配置指南

## 步骤 1：注册 Tushare

1. **访问官网**：https://tushare.pro/
2. **注册账号** - 免费，提供手机号注册
3. **登录**后点击右上角头像 → **接口 Token**
4. **复制 Token**（类似：`a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`）

---

## 步骤 2：积分说明

- **注册送 100 积分**
- **基础行情数据**（日线）需要 **120 积分**
- **每日签到** +2 积分
- **邀请好友** +20 积分/人

### 快速获得 120 积分：
1. 注册送 100 积分
2. 签到 2 天（+4 积分）
3. 或者完善个人资料（+10 积分）

---

## 步骤 3：配置 Token

编辑配置文件：
```bash
nano /Users/kelvin/.openclaw/workspace/quant-trading-system/config/tushare_config.json
```

修改内容：
```json
{
  "tushare": {
    "token": "你的 TUSHARE_TOKEN",
    "api_url": "https://api.tushare.pro",
    "enabled": true
  },
  "data_source": "tushare",
  "fallback_to_mock": true
}
```

**关键修改：**
- `token`: 替换为你的 Token
- `enabled`: 改为 `true`
- `data_source`: 改为 `tushare`

---

## 步骤 4：安装 Tushare（如果需要）

```bash
pip3 install tushare
```

---

## 步骤 5：测试

运行一次每日任务：
```bash
cd /Users/kelvin/.openclaw/workspace/quant-trading-system
python3 run_daily.py
```

**成功标志：**
- 🟢 Tushare 已启用
- 不再出现 "Remote end closed connection" 错误
- 正常获取股票数据

---

## 数据源优先级

系统会按以下顺序尝试获取数据：

1. **Tushare**（如果 enabled=true 且 Token 有效）
2. **AkShare**（备用）
3. **模拟数据**（兜底）

---

## 常见问题

### Q: 积分不够怎么办？
A: 每天签到，或者先使用模拟数据跑几天。

### Q: Token 安全吗？
A: Token 只保存在本地配置文件，不会上传。

### Q: Tushare 和 AkShare 哪个更好？
A: 
- **Tushare**: 更稳定，数据质量高，需要积分
- **AkShare**: 免费，但有时不稳定

---

## 配置完成后

告诉我一声，我帮你测试运行！
