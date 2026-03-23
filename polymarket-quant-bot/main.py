#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 量化交易机器人 - 主入口
5 大数学公式驱动：EV、贝叶斯、凯利、基础率、KL 散度
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加 src 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ev_calculator import EVCalculator
from kelly_position import KellyPosition
from bayes_updater import BayesUpdater
from base_rate_scanner import BaseRateScanner
from kl_arb_detector import KLArbDetector
from data_fetcher import MockPolymarketAPI, PolymarketAPI
from prediction_model import PredictionModel
from email_reporter import EmailReporter

class PolymarketQuantBot:
    """Polymarket 量化交易机器人"""
    
    def __init__(self, config_path: str = None, use_real_api: bool = False):
        """初始化机器人"""
        self.base_dir = Path(__file__).parent
        self.config_path = config_path or self.base_dir / 'config' / 'config.json'
        self.config = self.load_config()
        
        # 初始化 API
        if use_real_api and self.config.get('api_key'):
            self.api = PolymarketAPI(api_key=self.config['api_key'])
            print(f"🔌 使用真实 Polymarket API")
        else:
            self.api = MockPolymarketAPI()
            print(f"🔌 使用模拟 API（测试模式）")
        
        # 初始化各模块
        self.model = PredictionModel()
        self.ev_calc = EVCalculator(
            threshold=self.config['strategies']['ev_strategy']['ev_threshold']
        )
        self.kelly = KellyPosition(
            fraction=self.config['risk_control']['kelly_fraction']
        )
        self.bayes = BayesUpdater()
        self.base_rate = BaseRateScanner()
        self.kl_detector = KLArbDetector(
            threshold=self.config['strategies']['kl_arb_strategy']['kl_threshold']
        )
        self.reporter = EmailReporter()
        
        # 账户状态
        self.account = {
            'capital': self.config['account']['initial_capital'],
            'positions': {},
            'trades': []
        }
        
        print(f"✅ Polymarket 量化机器人初始化完成")
        print(f"📊 模式：{self.config['mode']}")
        print(f"💰 初始资金：${self.account['capital']:,.0f}")
    
    def load_config(self):
        """加载配置文件"""
        import json
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def scan_ev_opportunities(self, markets: list) -> list:
        """扫描 EV 机会"""
        return self.ev_calc.scan_dict(markets)
    
    def scan_base_rate_opportunities(self, markets: list) -> list:
        """扫描基础率机会"""
        return self.base_rate.scan_multiple(markets)
    
    def scan_kl_arbitrage(self, markets: dict) -> list:
        """扫描 KL 套利机会"""
        return self.kl_detector.scan(markets)
    
    def calculate_position(self, win_prob: float, price: float) -> float:
        """计算仓位"""
        odds = self.kelly.calculate_odds_from_price(price)
        return self.kelly.position_size(
            self.account['capital'],
            win_prob,
            odds,
            max_position=self.config['account']['max_position_size']
        )
    
    def run_daily(self):
        """每日运行"""
        print("\n" + "="*60)
        print(f"🤖 Polymarket 量化机器人 - 每日运行")
        print(f"📅 日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # 1. 从 API 获取市场数据
        print("\n🔌 从 API 获取市场数据...")
        markets_data = self.api.get_markets(limit=20)
        print(f"✅ 获取到 {len(markets_data)} 个市场")
        
        # 转换为统一格式
        markets_for_ev = []
        markets_for_base_rate = []
        markets_for_kl = {}
        
        print("\n🧠 运行预测模型...")
        
        for m in markets_data:
            market_id = m['id']
            yes_price = m['yes_price']
            
            # 使用预测模型计算真实概率
            market_price, pred_prob, ev, factors = self.model.calculate_ev(m)
            
            markets_for_ev.append({
                'market': market_id,
                'market_price': yes_price,
                'model_p': pred_prob,
                'ev': ev,
                'factors': factors
            })
            
            # 基础率策略
            category = m.get('category', 'unknown')
            event_type = f"{category}_default"
            markets_for_base_rate.append({
                'event_type': event_type,
                'market_price': yes_price
            })
            
            # KL 散度策略
            markets_for_kl[market_id] = [yes_price, 1 - yes_price]
        
        # 2. 扫描 EV 机会
        print("\n📊 扫描 EV 机会...")
        ev_opps = self.scan_ev_opportunities(markets_for_ev)
        
        if ev_opps:
            print(f"✅ 发现 {len(ev_opps)} 个 EV 机会")
            for opp in ev_opps[:5]:
                position = self.calculate_position(opp['model_p'], opp['market_price'])
                top_factor = max(opp['factors'].items(), key=lambda x: x[1])[0] if opp.get('factors') else 'N/A'
                print(f"  {opp['market']}:")
                print(f"    市场价={opp['market_price']:.0%}, 预测价={opp['model_p']:.0%}, EV={opp['ev']:+.1%}")
                print(f"    主导因子：{top_factor}, 建议仓位=${position:,.0f}")
        else:
            print("⚠️  无 EV 机会")
        
        # 3. 扫描基础率机会
        print("\n📊 扫描基础率机会...")
        br_opps = self.scan_base_rate_opportunities(markets_for_base_rate)
        
        if br_opps:
            print(f"✅ 发现 {len(br_opps)} 个基础率机会")
            for opp in br_opps[:5]:
                print(f"  {opp['event_type']}: 缺口={opp['gap']:+.0%}, 信号={opp['signal']}")
        else:
            print("⚠️  无基础率机会")
        
        # 4. 扫描 KL 套利
        print("\n📊 扫描 KL 套利机会...")
        kl_opps = self.scan_kl_arbitrage(markets_for_kl)
        
        arb_opps = [o for o in kl_opps if o['signal'] == 'ARB']
        if arb_opps:
            print(f"✅ 发现 {len(arb_opps)} 个套利机会")
            for opp in arb_opps[:5]:
                print(f"  {opp['market_a']} vs {opp['market_b']}: KL={opp['kl_divergence']:.4f}")
        else:
            print("⚠️  无 KL 套利机会")
        
        # 生成报告并发送邮件
        self.generate_and_send_report(ev_opps, br_opps, arb_opps)
        
        print("\n" + "="*60)
        print("✅ 每日运行完成")
        print("="*60)
    
    def generate_and_send_report(self, ev_opps: list, br_opps: list, arb_opps: list):
        """生成报告并发送邮件"""
        report_dir = self.base_dir / 'reports'
        report_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 生成模拟交易
        trades = []
        for opp in ev_opps[:3]:
            position = self.calculate_position(opp['model_p'], opp['market_price'])
            if position > 0:
                import random
                pnl_ratio = random.uniform(-0.1, 0.2)
                pnl = position * pnl_ratio
                
                trades.append({
                    'market': opp['market'],
                    'signal': 'BUY',
                    'bet_size': position,
                    'pnl': pnl
                })
        
        # 计算总盈亏
        total_pnl = sum(t['pnl'] for t in trades) if trades else 0
        self.account['capital'] += total_pnl
        
        # 保存交易记录
        self.account['trades'].extend([{
            **t,
            'timestamp': datetime.now().isoformat(),
            'date': date_str
        } for t in trades])
        
        # 生成邮件报告数据
        report_data = {
            'date': date_str,
            'capital': self.account['capital'],
            'pnl': total_pnl,
            'pnl_pct': total_pnl / self.account['capital'] if self.account['capital'] > 0 else 0,
            'trades': trades,
            'signals': {
                'EV 期望值': {'signals': len(ev_opps), 'executed': len([t for t in trades if t['signal'] == 'BUY'])},
                '基础率套利': {'signals': len(br_opps), 'executed': 0},
                'KL 散度套利': {'signals': len(arb_opps), 'executed': 0},
            },
            'top_opportunities': ev_opps[:5] if ev_opps else []
        }
        
        # 发送电子邮件
        print("\n📧 发送每日报告邮件...")
        email_sent = self.reporter.send_daily_report(report_data)
        
        if email_sent:
            print("✅ 邮件发送成功！")
        else:
            print("⚠️  邮件发送失败，已保存本地报告")
        
        # 保存本地 Markdown 报告
        report_file = report_dir / f'daily_report_{date_str}.md'
        self._save_markdown_report(report_file, report_data)
        print(f"📄 报告已保存：{report_file}")
    
    def _save_markdown_report(self, report_file: Path, report_data: dict):
        """保存 Markdown 格式报告"""
        report = f"""# 📊 Polymarket 量化机器人每日报告
**日期：** {report_data['date']}
**模式：** {self.config['mode']}

---

## 💰 账户概览

| 项目 | 数值 |
|------|------|
| 总资金 | ${report_data['capital']:,.0f} |
| 今日盈亏 | {report_data['pnl']:+,.0f} |
| 收益率 | {report_data['pnl_pct']:+.2%} |
| 交易数 | {len(report_data['trades'])} |

---

## 📈 策略表现

| 策略 | 信号数 | 执行数 |
|------|--------|--------|
| EV 期望值 | {report_data['signals']['EV 期望值']['signals']} | {report_data['signals']['EV 期望值']['executed']} |
| 基础率套利 | {report_data['signals']['基础率套利']['signals']} | 0 |
| KL 散度套利 | {report_data['signals']['KL 散度套利']['signals']} | 0 |

---

## 💼 交易记录

"""
        if report_data['trades']:
            report += "| 市场 | 信号 | 仓位 | 盈亏 |\n|------|------|------|------|\n"
            for t in report_data['trades']:
                pnl_color = "🟢" if t['pnl'] > 0 else "🔴" if t['pnl'] < 0 else "⚪"
                report += f"| {t['market']} | {t['signal']} | ${t['bet_size']:,.0f} | {pnl_color} {t['pnl']:+,.0f} |\n"
        else:
            report += "今日无交易\n"
        
        report += "\n---\n\n*报告生成时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 Polymarket 量化交易机器人启动")
    print("="*60)
    
    bot = PolymarketQuantBot()
    bot.run_daily()
    
    print("\n✅ 机器人运行完成！\n")


if __name__ == "__main__":
    main()
