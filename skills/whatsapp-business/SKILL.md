---
name: whatsapp-business
description: WhatsApp Business API 集成工具，支持发送消息、接收消息、模板消息、自动回复等功能。
emoji: 📲
---

# WhatsApp Business - 商务通信技能

## 功能概述

通过 WhatsApp Business API 实现自动化商务通信，支持消息发送、接收、模板消息、客服自动化等功能。

## 核心功能

### 📤 1. 消息发送

```python
class WhatsAppSender:
    """WhatsApp 消息发送器"""
    
    def __init__(self, phone_number_id, access_token):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def send_text_message(self, to, message):
        """发送文本消息"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message,
                "preview_url": True  # 自动解析链接预览
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def send_image_message(self, to, image_url, caption=None):
        """发送图片消息"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption or ""
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def send_document_message(self, to, document_url, filename, caption=None):
        """发送文档消息"""
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": filename,
                "caption": caption or ""
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def send_location_message(self, to, latitude, longitude, name=None, address=None):
        """发送位置消息"""
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "name": name or "",
                "address": address or ""
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def send_contact_message(self, to, contact_info):
        """发送联系人消息"""
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "contacts",
            "contacts": [contact_info]
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def send_interactive_button(self, to, header, body, buttons):
        """发送交互式按钮消息"""
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        if header:
            data["interactive"]["header"] = {"type": "text", "text": header}
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def send_interactive_list(self, to, header, body, footer, sections):
        """发送交互式列表消息"""
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": header},
                "body": {"text": body},
                "footer": {"text": footer},
                "action": {
                    "button": "查看选项",
                    "sections": sections
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
```

### 📥 2. 消息接收（Webhook）

```python
from flask import Flask, request, jsonify
import hashlib
import hmac

app = Flask(__name__)

class WhatsAppWebhook:
    """WhatsApp Webhook 接收器"""
    
    def __init__(self, verify_token):
        self.verify_token = verify_token
    
    def verify_webhook(self, mode, token, challenge):
        """验证 Webhook（首次配置时使用）"""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def handle_message(self, data):
        """处理接收到的消息"""
        try:
            # 解析消息
            entry = data.get('entry', [])
            for item in entry:
                changes = item.get('changes', [])
                for change in changes:
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        messages = value.get('messages', [])
                        
                        for message in messages:
                            from_number = message.get('from')
                            msg_type = message.get('type')
                            timestamp = message.get('timestamp')
                            
                            if msg_type == 'text':
                                text = message.get('text', {}).get('body')
                                self.handle_text_message(from_number, text, timestamp)
                            elif msg_type == 'image':
                                image = message.get('image', {})
                                self.handle_image_message(from_number, image, timestamp)
                            elif msg_type == 'document':
                                document = message.get('document', {})
                                self.handle_document_message(from_number, document, timestamp)
                            elif msg_type == 'button':
                                button = message.get('button', {})
                                self.handle_button_response(from_number, button, timestamp)
            
            return {"status": "success"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def handle_text_message(self, from_number, text, timestamp):
        """处理文本消息"""
        print(f"收到来自 {from_number} 的消息：{text}")
        # 可以在这里添加自动回复逻辑
    
    def handle_image_message(self, from_number, image, timestamp):
        """处理图片消息"""
        print(f"收到来自 {from_number} 的图片：{image.get('mime_type')}")
    
    def handle_document_message(self, from_number, document, timestamp):
        """处理文档消息"""
        print(f"收到来自 {from_number} 的文档：{document.get('filename')}")
    
    def handle_button_response(self, from_number, button, timestamp):
        """处理按钮响应"""
        print(f"收到来自 {from_number} 的按钮点击：{button}")

# Flask Webhook 路由
@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    result = webhook_handler.verify_webhook(mode, token, challenge)
    if result:
        return str(result), 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def receive():
    data = request.get_json()
    result = webhook_handler.handle_message(data)
    return jsonify(result), 200
```

### 📋 3. 模板消息

```python
class WhatsAppTemplate:
    """WhatsApp 模板消息管理"""
    
    def __init__(self, phone_number_id, access_token):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def send_template(self, to, template_name, language, components=None):
        """发送模板消息"""
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language
                }
            }
        }
        
        # 添加动态参数（如果有）
        if components:
            data["template"]["components"] = components
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def create_template(self, name, language, category, components):
        """创建新模板（需要在 Meta Business Manager 审批）"""
        url = f"{self.base_url}/{self.phone_number_id}/message_templates"
        
        data = {
            "name": name,
            "language": language,
            "category": category,
            "components": components
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def get_templates(self):
        """获取所有模板"""
        url = f"{self.base_url}/{self.phone_number_id}/message_templates"
        
        response = requests.get(url, headers=headers)
        return response.json()
    
    def delete_template(self, template_name):
        """删除模板"""
        url = f"{self.base_url}/{self.phone_number_id}/message_templates"
        
        data = {
            "name": template_name
        }
        
        response = requests.delete(url, headers=headers, json=data)
        return response.json()

# 模板消息示例
def send_order_confirmation(to, order_id, customer_name, total_amount):
    """发送订单确认模板消息"""
    
    components = [
        {
            "type": "header",
            "parameters": [
                {"type": "text", "text": order_id}
            ]
        },
        {
            "type": "body",
            "parameters": [
                {"type": "text", "text": customer_name},
                {"type": "text", "text": f"${total_amount}"}
            ]
        }
    ]
    
    template.send_template(
        to=to,
        template_name="order_confirmation",
        language="zh_CN",
        components=components
    )
```

### 🤖 4. 自动回复

```python
class WhatsAppAutoReply:
    """WhatsApp 自动回复系统"""
    
    def __init__(self):
        self.rules = []
        self.default_reply = None
    
    def add_rule(self, keyword, response, match_type="contains"):
        """添加自动回复规则"""
        self.rules.append({
            "keyword": keyword,
            "response": response,
            "match_type": match_type  # contains, exact, regex
        })
    
    def set_default_reply(self, response):
        """设置默认回复"""
        self.default_reply = response
    
    def get_reply(self, message):
        """获取回复"""
        message_lower = message.lower()
        
        for rule in self.rules:
            if rule["match_type"] == "contains":
                if rule["keyword"].lower() in message_lower:
                    return rule["response"]
            elif rule["match_type"] == "exact":
                if rule["keyword"].lower() == message_lower:
                    return rule["response"]
            elif rule["match_type"] == "regex":
                import re
                if re.search(rule["keyword"], message, re.IGNORECASE):
                    return rule["response"]
        
        return self.default_reply
    
    def handle_message(self, from_number, message, sender):
        """处理消息并发送回复"""
        reply = self.get_reply(message)
        
        if reply:
            sender.send_text_message(from_number, reply)
            return True
        return False

# 使用示例
auto_reply = WhatsAppAutoReply()

# 添加关键词回复
auto_reply.add_rule("价格", "我们的产品价格请参考官网：https://example.com/pricing")
auto_reply.add_rule("客服", "客服工作时间：周一至周五 9:00-18:00")
auto_reply.add_rule("地址", "公司地址：北京市朝阳区 xxx 路 xxx 号")

# 添加正则表达式回复
auto_reply.add_rule(r"订单.*\d+", "请提供您的订单号，我来帮您查询")

# 设置默认回复
auto_reply.set_default_reply("您好！感谢您的咨询。我们的客服会尽快回复您。")
```

### 📊 5. 消息统计

```python
class WhatsAppAnalytics:
    """WhatsApp 消息统计分析"""
    
    def __init__(self, phone_number_id, access_token):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_insights(self, start_date, end_date):
        """获取消息统计"""
        url = f"{self.base_url}/{self.phone_number_id}/insights"
        
        params = {
            "metric": "messages_sent,messages_delivered,messages_read,messages_failed",
            "since": start_date,
            "until": end_date
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    def get_conversation_stats(self, start_date, end_date):
        """获取会话统计"""
        url = f"{self.base_url}/{self.phone_number_id}/conversation_categories"
        
        params = {
            "since": start_date,
            "until": end_date
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    def get_phone_number_stats(self):
        """获取电话号码统计"""
        url = f"{self.base_url}/{self.phone_number_id}"
        
        params = {
            "fields": "display_phone_number,verified_name,quality_rating"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

# 生成统计报告
def generate_daily_report():
    """生成每日统计报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    stats = analytics.get_insights(yesterday, today)
    
    report = f"""
## 📊 WhatsApp 每日统计报告

**日期**: {yesterday}

### 消息统计
- 发送：{stats.get('messages_sent', 0)}
- 送达：{stats.get('messages_delivered', 0)}
- 阅读：{stats.get('messages_read', 0)}
- 失败：{stats.get('messages_failed', 0)}

### 送达率
{stats.get('messages_delivered', 0) / max(stats.get('messages_sent', 1), 1) * 100:.1f}%

### 阅读率
{stats.get('messages_read', 0) / max(stats.get('messages_delivered', 1), 1) * 100:.1f}%
"""
    return report
```

## 配置示例

### 配置文件 (~/.openclaw/config/whatsapp.json)

```json
{
  "whatsapp": {
    "phone_number_id": "你的电话号码 ID",
    "access_token": "EAAxxxxx",
    "business_account_id": "商务账户 ID",
    "verify_token": "自定义验证令牌",
    "webhook_url": "https://your-domain.com/webhook",
    "default_language": "zh_CN"
  },
  "auto_reply": {
    "enabled": true,
    "rules": [
      {"keyword": "价格", "response": "价格请咨询客服"},
      {"keyword": "客服", "response": "客服时间：9:00-18:00"}
    ],
    "default_reply": "感谢您的消息，我们会尽快回复"
  },
  "templates": {
    "order_confirmation": "order_confirmation",
    "shipping_notification": "shipping_notification",
    "appointment_reminder": "appointment_reminder"
  }
}
```

## 使用场景

### ✅ 适用场景

- **电商订单通知** - 订单确认、发货通知、物流更新
- **客服自动化** - 常见问题自动回复、工单创建
- **预约提醒** - 医疗、美容、咨询服务预约
- **营销通知** - 促销活动、新品上架（需合规）
- **内部通知** - 团队消息、系统告警

### ❌ 限制和注意事项

- **24 小时规则** - 用户主动联系后 24 小时内可免费回复
- **模板审批** - 营销类模板需 Meta 审批
- **消息质量** - 质量评分过低会被限制发送
- **用户同意** - 需获得用户同意才能发送消息

## 最佳实践

### 1. 消息质量维护

```python
def maintain_quality():
    """维护消息质量"""
    # 避免发送用户未订阅的消息
    # 提供明确的退订选项
    # 监控质量评分
    quality = analytics.get_phone_number_stats()
    if quality.get('quality_rating') == 'RED':
        # 质量过低，暂停发送
        pause_sending()
```

### 2. 模板设计

```python
# 好的模板设计
GOOD_TEMPLATE = {
    "name": "order_update",
    "category": "UTILITY",  # 实用类，容易审批
    "components": [
        {"type": "HEADER", "format": "TEXT"},
        {"type": "BODY", "text": "您的订单 {{1}} 已{{2}}"},
        {"type": "BUTTONS", "buttons": [
            {"type": "QUICK_REPLY", "text": "查看详情"}
        ]}
    ]
}
```

### 3. 错误处理

```python
def safe_send(to, message):
    """安全发送消息"""
    try:
        result = sender.send_text_message(to, message)
        
        if 'error' in result:
            error_code = result['error'].get('code')
            
            if error_code == 130429:  # 用户未授权
                log_opt_out(to)
            elif error_code == 131047:  # 质量过低
                pause_campaign()
            elif error_code == 131008:  # 频率限制
                time.sleep(60)
                safe_send(to, message)
        
        return result
    
    except Exception as e:
        log_error(e)
        return None
```

## 注意事项

1. **API 费用** - 24 小时外的消息按会话收费
2. **隐私合规** - 遵守 GDPR 等隐私法规
3. **消息质量** - 保持高质量，避免被举报
4. **模板审批** - 提前 1-2 天提交审批
5. **频率限制** - 避免短时间内大量发送

## 扩展方向

- 🛒 电商订单系统集成
- 📅 日历/预约系统集成
- 🎫 工单系统集成
- 📈 CRM 系统集成
- 🤖 AI 客服对话增强
