#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小众股票价格提醒脚本
监控股票价格，触发提醒时发送邮件/通知
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 配置
CONFIG_FILE = Path("/Users/kelvin/.openclaw/workspace/projects/stock-tracking/price_alerts_config.json")
DATA_DIR = Path("/Users/kelvin/.openclaw/workspace/projects/stock-tracking")

# 默认提醒配置
DEFAULT_ALERTS = {
    "688012_中微公司": {
        "code": "688012",
        "name": "中微公司",
        "alerts": [
            {"type": "drop", "threshold": -10, "action": "考虑止损"},
            {"type": "rise", "threshold": 15, "action": "考虑加仓"},
            {"type": "drop", "threshold": -15, "action": "严格执行止损"}
        ]
    },
    "300861_美畅股份": {
        "code": "300861",
        "name": "美畅股份",
        "alerts": [
            {"type": "drop", "threshold": -10, "action": "考虑止损"},
            {"type": "rise", "threshold": 20, "action": "考虑加仓"}
        ]
    },
    "835185_贝特瑞": {
        "code": "835185",
        "name": "贝特瑞",
        "alerts": [
            {"type": "drop", "threshold": -15, "action": "考虑止损"},
            {"type": "rise", "threshold": 25, "action": "考虑加仓"}
        ]
    }
}

def load_config():
    """加载提醒配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_ALERTS

def get_latest_price(stock_key, stock_config, max_retries=3):
    """获取最新价格（使用 AkShare 实时数据，带重试机制）"""
    import akshare as ak
    import pandas as pd
    import time
    
    code = stock_config["code"]
    market = stock_config.get("market", "A")
    
    for attempt in range(max_retries):
        try:
            # 获取实时行情数据
            if market == "A":
                # A 股实时行情
                df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
                if df.empty:
                    print(f"⚠️ 无法获取 {code} 数据")
                    return None
                
                # 获取最新收盘价和涨跌幅
                latest = df.iloc[-1]
                prev_close = df.iloc[-2]["close"] if len(df) > 1 else latest["close"]
                current_price = latest["close"]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                return {
                    "price": round(current_price, 2),
                    "change_pct": round(change_pct, 2),
                    "date": latest["date"]
                }
            elif market == "HK":
                # 港股实时行情
                df = ak.stock_hk_hist(symbol=code, period="daily", adjust="qfq")
                if df.empty:
                    return None
                latest = df.iloc[-1]
                prev_close = df.iloc[-2]["close"] if len(df) > 1 else latest["close"]
                current_price = latest["close"]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                return {
                    "price": round(current_price, 2),
                    "change_pct": round(change_pct, 2),
                    "date": latest["date"]
                }
            elif market == "US":
                # 美股实时行情
                df = ak.stock_us_hist(symbol=code, period="daily", adjust="qfq")
                if df.empty:
                    return None
                latest = df.iloc[-1]
                prev_close = df.iloc[-2]["close"] if len(df) > 1 else latest["close"]
                current_price = latest["close"]
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                return {
                    "price": round(current_price, 2),
                    "change_pct": round(change_pct, 2),
                    "date": latest["date"]
                }
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避：2s, 4s, 8s
                print(f"⚠️ 获取 {code} 价格失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                print(f"   等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"❌ 获取 {code} 价格失败 (已重试 {max_retries} 次): {e}")
                return None
    
    return None

def check_alerts(config):
    """检查是否触发提醒"""
    triggered = []
    
    for stock_key, stock_config in config.items():
        price_data = get_latest_price(stock_key, stock_config)
        if price_data is None:
            continue
        
        for alert in stock_config.get("alerts", []):
            threshold = alert["threshold"]
            change = price_data["change_pct"]
            
            should_alert = False
            if alert["type"] == "drop" and change <= threshold:
                should_alert = True
            elif alert["type"] == "rise" and change >= threshold:
                should_alert = True
            
            if should_alert:
                triggered.append({
                    "stock": stock_config["name"],
                    "code": stock_config["code"],
                    "price": price_data["price"],
                    "change": change,
                    "alert_type": alert["type"],
                    "threshold": threshold,
                    "action": alert["action"],
                    "timestamp": datetime.now().isoformat()
                })
    
    return triggered

def send_alert_email(triggered_alerts):
    """发送提醒邮件"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    if not triggered_alerts:
        return True
    
    EMAIL_CONFIG = {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "from_email": "4352395@qq.com",
        "password": "eryjlcbeanxnbgcj",
        "to_email": "4352395@qq.com"
    }
    
    subject = f"🚨 价格提醒 - {len(triggered_alerts)} 只股票触发警报"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .alert {{ padding: 15px; margin: 10px 0; border-radius: 8px; }}
            .alert-danger {{ background: #ffe6e6; border-left: 4px solid #c0392b; }}
            .alert-warning {{ background: #fff3cd; border-left: 4px solid #f39c12; }}
            .alert-success {{ background: #e6ffe6; border-left: 4px solid #27ae60; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #667eea; color: white; }}
            .red {{ color: #c0392b; font-weight: bold; }}
            .green {{ color: #27ae60; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>🚨 小众股票价格提醒</h1>
        <p><strong>时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        <p><strong>触发警报数：</strong>{len(triggered_alerts)} 只</p>
        
        <h2>📊 警报详情</h2>
        <table>
            <tr>
                <th>代码</th>
                <th>名称</th>
                <th>现价</th>
                <th>涨跌幅</th>
                <th>警报类型</th>
                <th>触发阈值</th>
                <th>建议操作</th>
            </tr>
    """
    
    for alert in triggered_alerts:
        color_class = "alert-danger" if alert["change"] < -5 else "alert-warning" if alert["change"] < 0 else "alert-success"
        change_color = "red" if alert["change"] < 0 else "green"
        
        html_content += f"""
            <tr>
                <td>{alert['code']}</td>
                <td>{alert['stock']}</td>
                <td>{alert['price']}</td>
                <td class="{change_color}">{alert['change']:+.2f}%</td>
                <td>{'📉 下跌' if alert['alert_type'] == 'drop' else '📈 上涨'}</td>
                <td>{alert['threshold']:+.1f}%</td>
                <td><strong>{alert['action']}</strong></td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
            <h3>💡 操作建议</h3>
            <ul>
                <li>严格执行止损纪律，不要抱有侥幸心理</li>
                <li>加仓前确认基本面没有变化</li>
                <li>如有疑问，先减仓观望</li>
            </ul>
        </div>
        
        <p style="margin-top: 30px; color: #999; font-size: 12px;">
            此邮件由小众股票跟踪系统自动发送<br>
            免责声明：仅供参考，不构成投资建议
        </p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_CONFIG["from_email"]
    msg["To"] = EMAIL_CONFIG["to_email"]
    
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.login(EMAIL_CONFIG["from_email"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["from_email"], [EMAIL_CONFIG["to_email"]], msg.as_string())
        server.quit()
        print(f"✅ 提醒邮件已发送 ({len(triggered_alerts)} 条警报)")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def main():
    """主函数"""
    print("🔔 检查价格提醒...")
    
    # 加载配置
    config = load_config()
    print(f"📋 监控 {len(config)} 只股票")
    
    # 检查警报
    triggered = check_alerts(config)
    
    if triggered:
        print(f"🚨 触发 {len(triggered)} 条警报！")
        for alert in triggered:
            print(f"  - {alert['code']} {alert['name']}: {alert['change']:+.2f}% ({alert['action']})")
        
        # 发送提醒邮件
        send_alert_email(triggered)
        
        # 保存警报记录
        alert_file = DATA_DIR / f"price_alerts_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(alert_file, "w", encoding="utf-8") as f:
            json.dump(triggered, f, ensure_ascii=False, indent=2)
        print(f"✅ 警报记录已保存：{alert_file}")
    else:
        print("✅ 无触发警报")
    
    print("\n✅ 价格提醒检查完成！")

if __name__ == "__main__":
    main()
