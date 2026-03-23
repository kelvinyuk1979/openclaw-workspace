#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件报告生成器
发送每日战报和每周总结
"""

import smtplib
import json
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailReporter:
    """邮件报告生成器"""
    
    def __init__(self, config_path: str = None):
        """初始化"""
        self.base_dir = Path(__file__).parent.parent  # 指向项目根目录
        self.config_path = config_path or self.base_dir / 'config' / 'config.json'
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def send_daily_report(self, report_data: dict) -> bool:
        """
        发送每日报告
        
        Args:
            report_data: 报告数据
                {
                    'date': str,
                    'capital': float,
                    'pnl': float,
                    'pnl_pct': float,
                    'trades': list,
                    'signals': dict,
                    'top_opportunities': list
                }
        
        Returns:
            是否发送成功
        """
        subject = f"📊 Polymarket 量化机器人每日战报 - {report_data['date']}"
        
        html = self._generate_daily_html(report_data)
        
        return self._send_email(subject, html)
    
    def send_weekly_summary(self, weekly_data: dict) -> bool:
        """
        发送每周总结
        
        Args:
            weekly_data: 周度数据
                {
                    'week_start': str,
                    'week_end': str,
                    'daily_reports': list,
                    'total_pnl': float,
                    'total_return': float,
                    'sharpe': float,
                    'max_drawdown': float,
                    'total_trades': int,
                    'win_rate': float
                }
        
        Returns:
            是否发送成功
        """
        subject = f"📈 Polymarket 量化机器人周报 ({weekly_data['week_start']} ~ {weekly_data['week_end']})"
        
        html = self._generate_weekly_html(weekly_data)
        
        return self._send_email(subject, html)
    
    def _generate_daily_html(self, data: dict) -> str:
        """生成每日报告 HTML"""
        
        # 交易记录表格
        trades_html = ""
        if data.get('trades'):
            trades_html = """
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f0f0f0;">
                    <th style="padding: 10px; border: 1px solid #ddd;">市场</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">信号</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">仓位</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">盈亏</th>
                </tr>
            """
            for t in data['trades'][:10]:  # 最多显示 10 笔
                pnl_color = "green" if t['pnl'] > 0 else "red" if t['pnl'] < 0 else "gray"
                trades_html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{t.get('market', 'N/A')}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{t.get('signal', 'N/A')}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">${t.get('bet_size', 0):,.0f}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: {pnl_color};">
                        {t.get('pnl', 0):+,.0f}
                    </td>
                </tr>
                """
            trades_html += "</table>"
        else:
            trades_html = "<p>今日无交易</p>"
        
        # 信号统计
        signals_html = ""
        if data.get('signals'):
            signals_html = """
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr style="background: #f0f0f0;">
                    <th style="padding: 10px; border: 1px solid #ddd;">策略</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">信号数</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">执行数</th>
                </tr>
            """
            for strategy, count in data['signals'].items():
                signals_html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{strategy}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{count.get('signals', 0)}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{count.get('executed', 0)}</td>
                </tr>
                """
            signals_html += "</table>"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #667eea; }}
                .metric-value {{ font-size: 28px; font-weight: bold; color: #667eea; margin: 10px 0; }}
                .metric-label {{ color: #666; font-size: 14px; }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                h2 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 30px; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Polymarket 量化机器人</h1>
                <p style="font-size: 18px; margin: 10px 0;">每日战报</p>
                <p style="font-size: 14px; opacity: 0.8;">{data['date']}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">账户资金</div>
                    <div class="metric-value">${data['capital']:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">今日盈亏</div>
                    <div class="metric-value {'positive' if data['pnl'] > 0 else 'negative' if data['pnl'] < 0 else ''}">
                        {data['pnl']:+,.0f}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">收益率</div>
                    <div class="metric-value {'positive' if data['pnl_pct'] > 0 else 'negative' if data['pnl_pct'] < 0 else ''}">
                        {data['pnl_pct']:+.2%}
                    </div>
                </div>
            </div>
            
            <h2>📈 策略表现</h2>
            {signals_html}
            
            <h2>💼 交易记录</h2>
            {trades_html}
            
            <h2>🎯 Top 机会</h2>
            <ul>
        """
        
        if data.get('top_opportunities'):
            for opp in data['top_opportunities'][:5]:
                html += f"<li><strong>{opp.get('market', 'N/A')}</strong>: EV={opp.get('ev', 0):+.1%}</li>"
        else:
            html += "<li>无显著机会</li>"
        
        html += f"""
            </ul>
            
            <div class="footer">
                <p>🤖 Polymarket 量化机器人 | 模拟交易</p>
                <p>此报告由系统自动生成，仅供参考，不构成投资建议</p>
                <p>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_weekly_html(self, data: dict) -> str:
        """生成周报 HTML"""
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                .metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 30px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #667eea; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; margin: 10px 0; }}
                .metric-label {{ color: #666; font-size: 14px; }}
                h2 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-top: 30px; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: center; }}
                th {{ background: #f0f0f0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📈 Polymarket 量化机器人</h1>
                <p style="font-size: 18px; margin: 10px 0;">周报总结</p>
                <p style="font-size: 14px; opacity: 0.8;">{data['week_start']} ~ {data['week_end']}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">周收益率</div>
                    <div class="metric-value {'positive' if data['total_return'] > 0 else 'negative' if data['total_return'] < 0 else ''}">
                        {data['total_return']:+.1%}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">夏普比率</div>
                    <div class="metric-value">{data['sharpe']:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">总交易</div>
                    <div class="metric-value">{data['total_trades']} 笔</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">胜率</div>
                    <div class="metric-value">{data['win_rate']:.1%}</div>
                </div>
            </div>
            
            <h2>📊 每日表现</h2>
            <table>
                <tr>
                    <th>日期</th>
                    <th>盈亏</th>
                    <th>收益率</th>
                    <th>交易数</th>
                </tr>
        """
        
        for day in data.get('daily_reports', []):
            pnl_color = "green" if day['pnl'] > 0 else "red" if day['pnl'] < 0 else "gray"
            html += f"""
                <tr>
                    <td>{day['date']}</td>
                    <td style="color: {pnl_color};">{day['pnl']:+,.0f}</td>
                    <td style="color: {pnl_color};">{day['pnl_pct']:+.2%}</td>
                    <td>{day.get('trades', 0)}</td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <h2>📈 累计净值</h2>
            <p>期初：${data.get('start_capital', 10000):,.0f} → 期末：${data.get('end_capital', 10000):,.0f}</p>
            <p>累计盈亏：{data['total_pnl']:+,.0f}</p>
            <p>最大回撤：{data.get('max_drawdown', 0):.1%}</p>
            
            <div class="footer">
                <p>🤖 Polymarket 量化机器人 | 模拟交易</p>
                <p>此报告由系统自动生成，仅供参考，不构成投资建议</p>
                <p>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, html: str) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config['notifications']['email_from']
            msg['To'] = self.config['notifications']['email_to']
            
            html_part = MIMEText(html, 'html', 'utf-8')
            msg.attach(html_part)
            
            server = smtplib.SMTP_SSL(
                self.config['notifications']['smtp_server'],
                self.config['notifications']['smtp_port']
            )
            server.login(
                self.config['notifications']['email_from'],
                self.config['notifications']['smtp_password']
            )
            server.sendmail(
                self.config['notifications']['email_from'],
                [self.config['notifications']['email_to']],
                msg.as_string()
            )
            server.quit()
            
            print(f"✅ 邮件已发送：{subject}")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败：{e}")
            return False


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("📧 邮件报告测试")
    print("="*60)
    
    reporter = EmailReporter()
    
    # 测试每日报告
    test_daily = {
        'date': '2026-03-18',
        'capital': 10500,
        'pnl': 500,
        'pnl_pct': 0.05,
        'trades': [
            {'market': 'fed-cut-jun', 'signal': 'BUY', 'bet_size': 500, 'pnl': 200},
            {'market': 'btc-100k', 'signal': 'BUY', 'bet_size': 300, 'pnl': -100},
        ],
        'signals': {
            'EV 期望值': {'signals': 5, 'executed': 2},
            '基础率': {'signals': 2, 'executed': 0},
            'KL 套利': {'signals': 1, 'executed': 0},
        },
        'top_opportunities': [
            {'market': 'ceasefire-2024', 'ev': 0.443},
            {'market': 'fed-cut-jun', 'ev': 0.212},
        ]
    }
    
    print("\n📊 发送每日报告测试...")
    success = reporter.send_daily_report(test_daily)
    
    if success:
        print("✅ 测试邮件发送成功！")
    else:
        print("❌ 测试邮件发送失败")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
