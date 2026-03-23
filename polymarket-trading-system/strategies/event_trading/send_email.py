#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送 Polymarket 日报到邮箱
使用 QQ 邮箱 SMTP 服务
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_today_report() -> str:
    """获取今日日报内容"""
    report_path = Path(__file__).parent / 'reports' / f"daily_{datetime.now().strftime('%Y%m%d')}.md"
    
    if report_path.exists():
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # 生成新报告
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from daily_report import DailyReport
        import json
        
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {
                'trading': {'max_bet': 100, 'stop_loss': 0.2, 'take_profit': 0.5},
                'monitor': {'volume_min': 1000}
            }
        
        reporter = DailyReport(config)
        return reporter.save_report()


def send_email(subject: str, content: str, to_email: str):
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        content: 邮件内容（Markdown 格式）
        to_email: 收件人邮箱
    """
    # QQ 邮箱 SMTP 配置
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # SSL 端口
    
    # 从 .env 文件读取配置
    from_email = "4352395@qq.com"
    email_password = "eryjlcbeanxnbgcj"  # QQ 邮箱授权码
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # 转换 Markdown 为 HTML（简单版本）
    html_content = content.replace('\n', '<br>\n')
    html_content = html_content.replace('## ', '<h2>').replace('# ', '<h1>')
    html_content = html_content.replace('**', '<b>').replace('*', '<i>')
    
    # 添加内容
    text_part = MIMEText(content, 'plain', 'utf-8')
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(text_part)
    msg.attach(html_part)
    
    try:
        # 连接 SMTP 服务器
        logger.info(f"连接 SMTP 服务器：{smtp_server}:{smtp_port}")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_email, email_password)
        
        # 发送邮件
        logger.info(f"发送邮件到：{to_email}")
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()
        
        logger.info("✅ 邮件发送成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 邮件发送失败：{e}")
        return False


def send_email_via_api(subject: str, content: str, to_email: str):
    """
    使用第三方邮件 API 发送（推荐）
    
    可选服务：
    - SendGrid (https://sendgrid.com)
    - Mailgun (https://www.mailgun.com)
    - 阿里云邮件推送 (https://www.aliyun.com/product/directmail)
    """
    # 这里以 SendGrid 为例
    import os
    
    api_key = os.environ.get('SENDGRID_API_KEY', '')
    if not api_key:
        logger.warning("⚠️ 未配置 SENDGRID_API_KEY，使用备用方案")
        return False
    
    try:
        import requests
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": subject
                }
            ],
            "from": {"email": "noreply@yourdomain.com"},
            "content": [
                {
                    "type": "text/plain",
                    "value": content
                }
            ]
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 202:
            logger.info("✅ 邮件发送成功！")
            return True
        else:
            logger.error(f"❌ 发送失败：{response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 邮件发送失败：{e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='发送 Polymarket 日报')
    parser.add_argument('--to', type=str, default='4352395@qq.com', help='收件人邮箱')
    parser.add_argument('--method', type=str, choices=['smtp', 'api'], default='smtp', help='发送方式')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    # 获取日报
    logger.info("获取今日日报...")
    content = get_today_report()
    
    # 邮件主题
    subject = f"📊 Polymarket 每日交易报告 - {datetime.now().strftime('%Y-%m-%d')}"
    
    # 发送邮件
    if args.method == 'api':
        success = send_email_via_api(subject, content, args.to)
    else:
        success = send_email(subject, content, args.to)
    
    if success:
        print(f"\n✅ 日报已发送到：{args.to}")
    else:
        print(f"\n❌ 发送失败，请检查配置")
        print("\n配置说明:")
        print("  方案 1 (SMTP): 编辑 send_email.py，填入你的 QQ 邮箱和授权码")
        print("  方案 2 (API): 设置环境变量 SENDGRID_API_KEY")


if __name__ == "__main__":
    main()
