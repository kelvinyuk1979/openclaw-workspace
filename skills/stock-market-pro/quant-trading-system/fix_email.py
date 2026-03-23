#!/usr/bin/env python3
"""修复：只在有真实数据时才发送邮件"""

file_path = '/Users/kelvin/.openclaw/workspace/skills/stock-market-pro/quant-trading-system/trading_system.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 send_email_report 方法，添加数据检查
old_check = '''    def send_email_report(self):
        """发送邮件报告"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart'''

new_check = '''    def send_email_report(self):
        """发送邮件报告（只在有真实数据时发送）"""
        # 检查是否有真实数据
        if not self.positions:
            print("📧 无持仓数据，跳过邮件发送")
            return
        
        # 检查数据是否有效（价格不能为 0 或 None）
        for symbol, pos in self.positions.items():
            if not pos.get('entry_price') or pos.get('entry_price') <= 0:
                print(f"📧 {symbol} 价格数据无效，跳过邮件发送")
                return
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart'''

if old_check in content:
    content = content.replace(old_check, new_check)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ 已添加数据质量检查")
else:
    print("⚠️  未找到匹配代码")
