#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误通知邮件 - 当任务失败时立即发送通知
"""

import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "from_email": "4352395@qq.com",
    "password": "eryjlcbeanxnbgcj",
    "to_email": "4352395@qq.com"
}

def send_error_notification(task_name, error_message, timestamp=None):
    """发送错误通知邮件"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    subject = f"⚠️ 错误通知 - {task_name} - {timestamp[:10]}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; }}
            .error-box {{ background: #fee; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .section h2 {{ color: #e74c3c; margin-top: 0; }}
            .timestamp {{ color: #999; font-size: 14px; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
            code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚠️ 任务失败通知</h1>
            <p style="font-size: 18px; margin: 10px 0;">{task_name}</p>
        </div>
        
        <div class="error-box">
            <strong>❌ 错误信息：</strong><br>
            <code style="display: block; margin-top: 10px; white-space: pre-wrap;">{error_message}</code>
        </div>
        
        <div class="section">
            <h2>📋 详细信息</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>任务名称</strong></td><td>{task_name}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>发生时间</strong></td><td>{timestamp}</td></tr>
                <tr><td style="padding: 8px;"><strong>通知类型</strong></td><td>自动错误通知</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🔧 建议操作</h2>
            <ul>
                <li>检查系统日志</li>
                <li>确认数据源/服务是否正常</li>
                <li>查看网络连接状态</li>
                <li>必要时手动重试任务</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>🤖 A 股量化交易系统 | 自动错误通知</p>
            <p class="timestamp">此邮件由系统自动发送，请勿回复</p>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_CONFIG["from_email"]
    msg["To"] = EMAIL_CONFIG["to_email"]
    
    html_part = MIMEText(html, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.login(EMAIL_CONFIG["from_email"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["from_email"], [EMAIL_CONFIG["to_email"]], msg.as_string())
        server.quit()
        print(f"✅ 错误通知邮件已发送：{task_name}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False


def main():
    """测试函数"""
    send_error_notification(
        "测试任务",
        "这是一个测试错误通知\n用于验证邮件系统是否正常工作",
        datetime.now().isoformat()
    )


if __name__ == "__main__":
    main()
