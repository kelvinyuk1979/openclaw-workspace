#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 每日简报邮件发送脚本
用法：
  python send_ai_daily_email.py [--date YYYY-MM-DD]
  echo "<html>...</html>" | python send_ai_daily_email.py --stdin --subject "主题"
"""

import smtplib
import json
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "from_email": "4352395@qq.com",
    "password": "eryjlcbeanxnbgcj",
    "to_email": "4352395@qq.com"
}

def get_ai_brief_content(date_str=None):
    """生成 AI 每日简报内容（HTML 格式）"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 这里应该调用 web_search 获取最新新闻
    # 简化版本：返回一个模板
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .headline {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            h1 {{ margin: 0; }}
            h2 {{ color: #667eea; }}
            ul {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 AI 每日简报</h1>
            <p>📅 {date_str}</p>
        </div>
        
        <div class="section">
            <h2>🔥 今日头条</h2>
            <div class="headline">
                <strong>1️⃣ OpenAI 将 Sora 整合进 ChatGPT</strong><br>
                独立 Sora 应用用户量大幅下滑，OpenAI 计划整合到 ChatGPT 提升使用率。
            </div>
            <div class="headline">
                <strong>2️⃣ Anthropic 与美国国防部纠纷</strong><br>
                因拒绝放宽军事 AI 安全限制，Claude 下载量反超 ChatGPT。
            </div>
            <div class="headline">
                <strong>3️⃣ NVIDIA B200 GPU 供不应求</strong><br>
                数据中心 GPU 市场份额 86%，已售罄至 2026 年年中。
            </div>
        </div>
        
        <div class="section">
            <h2>🏢 机构动态</h2>
            <ul>
                <li><strong>Google DeepMind:</strong> Gemini 重大更新，Workspace 全面 AI 化</li>
                <li><strong>Anthropic:</strong> Claude Opus 4.6 发布，EMEA 收入增长 11 倍</li>
                <li><strong>Meta:</strong> LLaMA 4 已发布，开源许可证争议持续</li>
                <li><strong>NVIDIA:</strong> B200 需求"疯狂"，Rubin 架构预计年末量产</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📈 趋势观察</h2>
            <ul>
                <li>🎥 视频 AI 整合加速</li>
                <li>🏛️ AI 安全成差异化竞争点</li>
                <li>💰 AI 基础设施军备竞赛持续</li>
                <li>📊 行业焦点从训练转向推理</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>本简报由 OpenClaw AI 自动生成 | Gemini 3.1 Pro Preview</p>
            <p>如需订阅管理，请回复邮件</p>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email(subject, html_content, to_email=None):
    """发送 HTML 邮件"""
    if to_email is None:
        to_email = EMAIL_CONFIG["to_email"]
    
    # 创建邮件
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_CONFIG["from_email"]
    msg["To"] = to_email
    
    # 添加 HTML 内容
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        # 连接 SMTP 服务器并发送
        print(f"📧 正在连接到 {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}...")
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.login(EMAIL_CONFIG["from_email"], EMAIL_CONFIG["password"])
        
        print(f"📤 发送邮件到 {to_email}...")
        server.sendmail(EMAIL_CONFIG["from_email"], [to_email], msg.as_string())
        server.quit()
        
        print("✅ 邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def main():
    # 解析参数
    date_str = None
    subject = None
    use_stdin = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--date" and i + 1 < len(sys.argv):
            date_str = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--stdin":
            use_stdin = True
            i += 1
        elif sys.argv[i] == "--subject" and i + 1 < len(sys.argv):
            subject = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if use_stdin:
        # 从 stdin 读取 HTML 内容
        print("📰 从 stdin 读取简报内容...")
        html_content = sys.stdin.read()
        if not subject:
            subject = f"🤖 AI 每日简报 - {date_str or datetime.now().strftime('%Y-%m-%d')}"
    else:
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # 生成简报内容
        print(f"📰 生成 {date_str} 的 AI 每日简报...")
        html_content = get_ai_brief_content(date_str)
        
        if not subject:
            subject = f"🤖 AI 每日简报 - {date_str}"
    
    # 发送邮件
    success = send_email(subject, html_content)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
