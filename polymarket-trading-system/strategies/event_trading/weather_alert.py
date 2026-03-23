#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气交易信号邮件通知
发现交易机会时立即发送邮件
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
from pathlib import Path

from weather_strategy import WeatherSignal

logger = logging.getLogger(__name__)

# 邮箱配置
SENDER_EMAIL = "4352395@qq.com"
SENDER_AUTH_CODE = "eryjlcbeanxnbgcj"
RECEIVER_EMAIL = "4352395@qq.com"

# SMTP 配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465


def create_alert_email(signals: List[WeatherSignal], balance: float = 1000.0) -> str:
    """
    创建交易信号通知邮件
    
    Args:
        signals: 交易信号列表
        balance: 当前余额
    
    Returns:
        邮件内容（HTML 格式）
    """
    if not signals:
        return ""
    
    # 邮件主题
    subject = f"🚨 天气交易机会！{len(signals)} 个信号 - {datetime.now().strftime('%m-%d %H:%M')}"
    
    # 邮件内容
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .signal {{ border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; margin: 15px 0; background: #fafafa; }}
        .signal-high {{ border-color: #ff6b6b; background: #fff5f5; }}
        .signal-medium {{ border-color: #ffd93d; background: #fffdf0; }}
        .signal-title {{ font-size: 18px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .signal-detail {{ margin: 8px 0; }}
        .label {{ font-weight: bold; color: #555; }}
        .value {{ color: #333; }}
        .highlight {{ color: #ff6b6b; font-weight: bold; }}
        .btn {{ display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px 10px 0; }}
        .btn:hover {{ background: #5568d3; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 2px solid #e0e0e0; font-size: 12px; color: #888; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌤️ 天气交易机会提醒</h1>
            <p>发现 <strong>{len(signals)}</strong> 个交易信号 | 余额：${balance:.2f}</p>
            <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
    
    # 添加每个信号
    for i, signal in enumerate(signals[:5], 1):  # 最多显示 5 个
        # 根据置信度选择样式
        if signal.confidence >= 0.80:
            signal_class = "signal-high"
            priority = "🔴 高优先级"
        elif signal.confidence >= 0.65:
            signal_class = "signal-medium"
            priority = "🟡 中优先级"
        else:
            signal_class = "signal"
            priority = "🟢 低优先级"
        
        # 生成 Polymarket 搜索链接
        search_url = f"https://polymarket.com/search?q={signal.city.replace(' ', '+')}+temperature"
        
        html += f"""
        <div class="signal {signal_class}">
            <div class="signal-title">
                信号 #{i} {priority}
            </div>
            
            <div class="signal-detail">
                <span class="label">📍 城市：</span>
                <span class="value">{signal.city}</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">📅 日期：</span>
                <span class="value">{signal.date}</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">🌡️ 预报温度：</span>
                <span class="highlight">{signal.forecast_temp}°F</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">📊 市场：</span>
                <span class="value">{signal.market_bucket}</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">💰 当前价格：</span>
                <span class="highlight">{signal.market_price:.2f}¢</span>
                <span style="color: #888; font-size: 12px;">(建议买入价 &lt;15¢)</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">📈 置信度：</span>
                <span class="highlight">{signal.confidence:.0%}</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">💵 期望值：</span>
                <span class="value">{signal.expected_value:.3f}</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">💼 建议仓位：</span>
                <span class="highlight">${signal.position_size:.2f}</span>
                <span style="color: #888; font-size: 12px;">(余额的 5%)</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">🎯 止盈价格：</span>
                <span class="value">45¢</span>
                <span style="color: #888; font-size: 12px;">(预期收益 {((0.45 - signal.market_price) / signal.market_price * 100):.0f}%)</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">📉 止损价格：</span>
                <span class="value">{signal.market_price * 0.5:.2f}¢</span>
                <span style="color: #888; font-size: 12px;">(最大亏损 50%)</span>
            </div>
            
            <div class="signal-detail">
                <span class="label">💡 原因：</span>
                <span class="value">{signal.reason}</span>
            </div>
            
            <div style="margin-top: 15px;">
                <a href="{search_url}" class="btn" target="_blank">🔗 打开 Polymarket 市场</a>
            </div>
        </div>
"""
    
    # 操作指南
    html += """
        <div class="warning">
            <strong>⚠️ 交易步骤：</strong>
            <ol>
                <li>点击上方"打开 Polymarket 市场"按钮</li>
                <li>找到对应的温度市场</li>
                <li>确认价格与邮件中一致（价格可能已变化）</li>
                <li>买入 YES 份额（建议金额见上）</li>
                <li>设置提醒：价格达到 45¢ 时卖出止盈</li>
            </ol>
        </div>
        
        <div class="footer">
            <p><strong>⚠️ 风险提示：</strong></p>
            <ul>
                <li>本邮件仅供参考，不构成投资建议</li>
                <li>预测市场有风险，可能导致资金损失</li>
                <li>建议先用小额资金测试（$10-20）</li>
                <li>设置好止盈止损，不要贪心</li>
                <li>只用闲钱投资，不要用生活必需资金</li>
            </ul>
            <p style="margin-top: 20px;">
                这是自动发送的交易提醒邮件 | Polymarket 天气交易机器人 v2.0<br>
                如有问题请检查系统配置
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return subject, html


def send_alert_email(signals: List[WeatherSignal], balance: float = 1000.0) -> bool:
    """
    发送交易信号通知邮件
    
    Args:
        signals: 交易信号列表
        balance: 当前余额
    
    Returns:
        是否发送成功
    """
    if not signals:
        logger.info("无交易信号，不发送邮件")
        return False
    
    try:
        # 创建邮件
        subject, html_content = create_alert_email(signals, balance)
        
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        # 添加内容
        text_content = f"发现 {len(signals)} 个交易信号，请查看 HTML 邮件"
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 发送邮件
        logger.info(f"连接 SMTP 服务器：{SMTP_SERVER}:{SMTP_PORT}")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_AUTH_CODE)
        
        logger.info(f"发送邮件到：{RECEIVER_EMAIL}")
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()
        
        logger.info("✅ 警报邮件发送成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 邮件发送失败：{e}")
        return False


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    
    # 创建测试信号
    test_signals = [
        WeatherSignal(
            city="New York LaGuardia",
            date="2026-03-16",
            forecast_temp=61,
            market_bucket="60-62°F",
            market_price=0.08,
            signal_type="buy_yes",
            confidence=0.85,
            expected_value=0.425,
            position_size=50.0,
            reason="NWS 预报 61°F，市场定价 8¢ (EV: 0.425)"
        )
    ]
    
    success = send_alert_email(test_signals)
    print(f"\n测试{'成功' if success else '失败'}")
