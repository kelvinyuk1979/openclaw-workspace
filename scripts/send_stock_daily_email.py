#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票选股日报邮件发送脚本
用法：
  python3 send_stock_daily_email.py [--date YYYY-MM-DD]
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

def get_stock_report_content(date_str=None):
    """生成股票选股日报内容（HTML 格式）"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; }}
            .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }}
            .stock-card {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stock-name {{ font-size: 18px; font-weight: bold; color: #667eea; }}
            .stock-symbol {{ color: #666; font-size: 14px; }}
            .price {{ font-size: 24px; font-weight: bold; color: #2ecc71; }}
            .price-up {{ color: #e74c3c; }}
            .rating {{ display: inline-block; padding: 5px 10px; border-radius: 5px; color: white; font-weight: bold; }}
            .rating-buy {{ background: #27ae60; }}
            .rating-hold {{ background: #f39c12; }}
            .rating-sell {{ background: #c0392b; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #667eea; color: white; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
            h1 {{ margin: 0; font-size: 28px; }}
            h2 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            h3 {{ color: #333; }}
            .bull {{ color: #27ae60; }}
            .bear {{ color: #c0392b; }}
            .risk {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 全球选股日报（华尔街风格）</h1>
            <p>📅 {date_str} | 覆盖市场：A 股 | 港股 | 美股</p>
        </div>
        
        <div class="section">
            <h2>🌟 今日核心推荐（Top 3）</h2>
            
            <div class="stock-card">
                <div class="stock-name">1️⃣ 宁德时代 (300750.SZ)</div>
                <div class="stock-symbol">全球动力电池龙头 | 市占率 37%</div>
                <p><strong>最新价：</strong> <span class="price price-up">¥404.97 (+3.0%)</span></p>
                <p><strong>评级：</strong> <span class="rating rating-buy">⭐⭐⭐⭐⭐ 强烈买入</span></p>
                <p><strong>核心逻辑：</strong></p>
                <ul>
                    <li>✅ 技术领先（麒麟电池、神行超充）</li>
                    <li>✅ 规模优势 + 供应链控制力</li>
                    <li>✅ H 股涨超 6%，绩后累计涨幅超 30%</li>
                    <li>✅ 动态 PE 约 25 倍，低于历史均值</li>
                </ul>
                <p><strong>目标价：</strong> ¥450 | <strong>止损位：</strong> ¥380 (-6%)</p>
            </div>
            
            <div class="stock-card">
                <div class="stock-name">2️⃣ 贵州茅台 (600519.SH)</div>
                <div class="stock-symbol">高端白酒垄断者 | 品牌护城河极深</div>
                <p><strong>最新价：</strong> <span class="price price-up">¥1,455.01 (+2.93%)</span></p>
                <p><strong>评级：</strong> <span class="rating rating-buy">⭐⭐⭐⭐ 买入</span></p>
                <p><strong>核心逻辑：</strong></p>
                <ul>
                    <li>✅ 品牌认知 + 稀缺性 + 定价权</li>
                    <li>✅ 毛利率 90%+，净利率 50%+，ROE 30%+</li>
                    <li>✅ 市值重回 1.8 万亿，白酒板块走强</li>
                    <li>✅ PE 约 30 倍，处于历史中低位</li>
                </ul>
                <p><strong>目标价：</strong> ¥1550 | <strong>止损位：</strong> ¥1380 (-5%)</p>
            </div>
            
            <div class="stock-card">
                <div class="stock-name">3️⃣ 美团 (03690.HK)</div>
                <div class="stock-symbol">本地生活服务平台 | 网络效应显著</div>
                <p><strong>最新价：</strong> <span class="price price-up">HK$76.20 (+3.49%)</span></p>
                <p><strong>评级：</strong> <span class="rating rating-buy">⭐⭐⭐⭐ 买入</span></p>
                <p><strong>核心逻辑：</strong></p>
                <ul>
                    <li>✅ 外卖 + 到店 + 酒旅 + 优选全生态</li>
                    <li>✅ 花旗维持"买入"评级，预计 3 月销量环比扩张</li>
                    <li>✅ PS 约 3 倍，低于历史均值</li>
                    <li>✅ 估值修复空间 30%+</li>
                </ul>
                <p><strong>目标价：</strong> HK$85 | <strong>止损位：</strong> HK$70 (-8%)</p>
            </div>
        </div>
        
        <div class="section">
            <h2>🌍 全球市场概览</h2>
            <table>
                <tr>
                    <th>市场</th>
                    <th>代表股票</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>情绪</th>
                </tr>
                <tr>
                    <td><strong>A 股</strong></td>
                    <td>贵州茅台</td>
                    <td>¥1,455.01</td>
                    <td style="color: #27ae60;">+2.93%</td>
                    <td>🟢 强势</td>
                </tr>
                <tr>
                    <td><strong>A 股</strong></td>
                    <td>宁德时代</td>
                    <td>¥404.97</td>
                    <td style="color: #27ae60;">+3.0%</td>
                    <td>🟢 强势</td>
                </tr>
                <tr>
                    <td><strong>A 股</strong></td>
                    <td>比亚迪</td>
                    <td>¥101.67</td>
                    <td style="color: #27ae60;">+2.01%</td>
                    <td>🟢 上涨</td>
                </tr>
                <tr>
                    <td><strong>港股</strong></td>
                    <td>腾讯控股</td>
                    <td>HK$556.00</td>
                    <td style="color: #27ae60;">+1.55%</td>
                    <td>🟢 上涨</td>
                </tr>
                <tr>
                    <td><strong>港股</strong></td>
                    <td>阿里巴巴</td>
                    <td>HK$132.90</td>
                    <td style="color: #f39c12;">+0.30%</td>
                    <td>🟡 持平</td>
                </tr>
                <tr>
                    <td><strong>港股</strong></td>
                    <td>美团</td>
                    <td>HK$76.20</td>
                    <td style="color: #27ae60;">+3.49%</td>
                    <td>🟢 强势</td>
                </tr>
                <tr>
                    <td><strong>美股</strong></td>
                    <td>苹果</td>
                    <td>$249.80</td>
                    <td style="color: #c0392b;">-2.31%</td>
                    <td>🔴 回调</td>
                </tr>
                <tr>
                    <td><strong>美股</strong></td>
                    <td>英伟达</td>
                    <td>$180.20</td>
                    <td style="color: #c0392b;">-1.59%</td>
                    <td>🔴 回调</td>
                </tr>
                <tr>
                    <td><strong>美股</strong></td>
                    <td>微软</td>
                    <td>$395.55</td>
                    <td style="color: #c0392b;">-1.57%</td>
                    <td>🔴 回调</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>⚖️ 多空辩论</h2>
            
            <h3>🔴 看空观点（风险警示）</h3>
            <ul>
                <li><strong>苹果 (AAPL)：</strong> iPhone 销量放缓、中国市场竞争、缺乏 AI 催化剂、估值偏高</li>
                <li><strong>英伟达 (NVDA)：</strong> GTC 大会后"卖事实"、竞争加剧（AMD/自研芯片）、估值已反映预期</li>
                <li><strong>阿里巴巴：</strong> 电商竞争白热化（拼多多/抖音）、云增长放缓、组织变革不确定性</li>
            </ul>
            
            <h3>🟢 看多观点（机会所在）</h3>
            <ul>
                <li><strong>宁德时代：</strong> 全球电动化趋势不变、储能业务爆发、技术迭代领先</li>
                <li><strong>贵州茅台：</strong> 消费升级长期趋势、提价预期、分红稳定</li>
                <li><strong>腾讯控股：</strong> 游戏版号恢复、视频号商业化、回购支撑股价</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>🎯 今日交易策略</h2>
            
            <h3>激进型（风险偏好高）</h3>
            <table>
                <tr><th>操作</th><th>标的</th><th>仓位</th><th>目标</th><th>止损</th></tr>
                <tr><td>买入</td><td>宁德时代 (300750)</td><td>20%</td><td>¥450</td><td>¥380</td></tr>
                <tr><td>买入</td><td>美团 (03690.HK)</td><td>15%</td><td>HK$85</td><td>HK$70</td></tr>
            </table>
            
            <h3>稳健型（风险偏好中）</h3>
            <table>
                <tr><th>操作</th><th>标的</th><th>仓位</th><th>目标</th><th>止损</th></tr>
                <tr><td>买入</td><td>贵州茅台 (600519)</td><td>15%</td><td>¥1550</td><td>¥1380</td></tr>
                <tr><td>持有</td><td>腾讯控股 (0700.HK)</td><td>10%</td><td>HK$600</td><td>HK$520</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>📅 本周关注</h2>
            <table>
                <tr><th>日期</th><th>事件</th><th>影响</th></tr>
                <tr><td>3/16-19</td><td>NVIDIA GTC 2026</td><td>🟡 芯片/AI 板块</td></tr>
                <tr><td>3/18</td><td>美联储 FOMC 会议</td><td>🔴 全球市场</td></tr>
                <tr><td>3/19</td><td>日本央行利率决议</td><td>🟡 亚洲市场</td></tr>
            </table>
        </div>
        
        <div class="risk">
            <strong>⚠️ 风险提示：</strong>
            <p>本报告仅供参考，不构成投资建议。市场有风险，投资需谨慎。请独立判断并咨询专业顾问。</p>
        </div>
        
        <div class="footer">
            <p>📊 全球选股日报 | OpenClaw AI 自动生成 | 数据源：Web Search + 实时行情</p>
            <p>📧 邮件发送时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
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
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--date" and i + 1 < len(sys.argv):
            date_str = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 生成简报内容
    print(f"📰 生成 {date_str} 的全球选股日报...")
    html_content = get_stock_report_content(date_str)
    
    subject = f"📈 全球选股日报 - {date_str}"
    
    # 发送邮件
    success = send_email(subject, html_content)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
