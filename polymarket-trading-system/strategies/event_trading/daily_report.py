#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 每日交易报告生成器
每天生成市场概览、策略信号、交易总结
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from monitor import PolymarketMonitor
from strategies.basic import BasicStrategy
from strategies.momentum import MomentumStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DailyReport:
    """每日交易报告生成器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.monitor = PolymarketMonitor(config['polymarket'].get('api_key', ''))
        self.basic_strategy = BasicStrategy(config)
        self.momentum_strategy = MomentumStrategy(config)
    
    def generate_market_overview(self) -> Dict:
        """生成市场概览"""
        markets = self.monitor.get_markets(limit=50)
        
        # 计算统计
        total_volume = sum(m['volume'] for m in markets)
        
        # 按交易量排序
        top_volume = sorted(markets, key=lambda x: x['volume'], reverse=True)[:10]
        
        return {
            'total_markets': len(markets),
            'total_volume': total_volume,
            'top_volume': top_volume,
        }
    
    def generate_strategy_signals(self, markets: List[Dict]) -> List[Dict]:
        """生成策略信号"""
        signals = []
        
        # 只分析有流动性的市场
        liquid_markets = [m for m in markets if m['liquidity'] > 50]
        
        # 基础策略信号
        basic_signals = self.basic_strategy.batch_evaluate(liquid_markets, {})
        for s in basic_signals[:5]:  # 最多 5 个信号
            signals.append({
                'strategy': '基础策略',
                'market_id': s.market_id,
                'market_title': s.reason[:30],
                'action': s.action,
                'confidence': f"{s.confidence:.0%}",
                'price': f"{s.price:.4f}",
                'amount': f"{s.amount:.0f} USDC",
                'reason': s.reason
            })
        
        # 动量策略信号
        momentum_signals = self.momentum_strategy.batch_evaluate(liquid_markets)
        for s in momentum_signals[:5]:
            signals.append({
                'strategy': '动量策略',
                'market_id': s.market_id,
                'market_title': s.reason[:30],
                'action': s.action,
                'confidence': f"{s.confidence:.0%}",
                'price': f"{s.price:.4f}",
                'amount': f"{s.amount:.0f} USDC",
                'reason': s.reason
            })
        
        return signals
    
    def get_upcoming_events(self) -> List[Dict]:
        """获取即将到期的市场（作为事件提醒）"""
        markets = self.monitor.get_markets(limit=50)
        
        now = datetime.now()
        upcoming = []
        
        for m in markets:
            end_date_str = m.get('endDate', '')
            if not end_date_str:
                continue
            
            try:
                # 解析日期
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                days_left = (end_date - now).days
                
                # 7 天内到期
                if 0 <= days_left <= 7:
                    upcoming.append({
                        'market_id': m['id'],
                        'title': m['title'][:50],
                        'end_date': end_date_str[:10],
                        'days_left': days_left,
                        'liquidity': m['liquidity']
                    })
            except:
                continue
        
        # 按到期时间排序
        upcoming.sort(key=lambda x: x['days_left'])
        
        return upcoming[:10]
    
    def generate_report(self) -> str:
        """生成完整报告"""
        logger.info("生成每日报告...")
        
        # 市场概览
        overview = self.generate_market_overview()
        
        # 策略信号
        markets = self.monitor.get_markets(limit=100)
        signals = self.generate_strategy_signals(markets)
        
        # 即将到期事件
        upcoming = self.get_upcoming_events()
        
        # 生成报告文本
        report = []
        report.append("=" * 70)
        report.append("📊 Polymarket 每日交易报告")
        report.append(f"**日期**: {datetime.now().strftime('%Y-%m-%d %A')}")
        report.append("=" * 70)
        report.append("")
        
        # 市场概览
        report.append("## 🌐 市场概览")
        report.append("")
        report.append(f"- **热门市场**: {overview['total_markets']} 个")
        report.append(f"- **总交易量**: ${overview['total_volume']:,.0f}")
        report.append(f"- **总交易量**: ${overview['total_volume']:,.0f}")
        report.append("")
        
        if overview['top_volume']:
            report.append("**交易量最高市场**:")
            for i, m in enumerate(overview['top_volume'][:3], 1):
                report.append(f"  {i}. {m['title'][:40]}... - ${m['volume']:,.0f}")
        report.append("")
        
        # 策略信号
        report.append("## 📈 策略信号")
        report.append("")
        
        if signals:
            report.append("| 策略 | 市场 | 信号 | 置信度 | 原因 |")
            report.append("|------|------|------|--------|------|")
            for s in signals[:10]:
                action_map = {
                    'buy_yes': '买入 YES',
                    'buy_no': '买入 NO',
                    'sell': '平仓',
                    'hold': '观望'
                }
                action = action_map.get(s['action'], s['action'])
                report.append(f"| {s['strategy']} | {s['market_id']} | {action} | {s['confidence']} | {s['reason'][:20]} |")
        else:
            report.append("⚠️ 暂无明确交易信号")
        report.append("")
        
        # 即将到期
        report.append("## ⏰ 即将到期（7 天内）")
        report.append("")
        
        if upcoming:
            report.append("| 市场 | 到期日 | 剩余 | 流动性 |")
            report.append("|------|--------|------|--------|")
            for e in upcoming[:5]:
                report.append(f"| {e['title'][:30]}... | {e['end_date']} | {e['days_left']}天 | ${e['liquidity']:.0f} |")
        else:
            report.append("暂无即将到期的市场")
        report.append("")
        
        # 今日建议
        report.append("## 💡 今日建议")
        report.append("")
        
        if signals:
            best_signal = max(signals, key=lambda x: float(x['confidence'].rstrip('%')))
            report.append(f"**最佳机会**: {best_signal['reason']}")
            report.append(f"- 策略：{best_signal['strategy']}")
            report.append(f"- 操作：{best_signal['action']}")
            report.append(f"- 置信度：{best_signal['confidence']}")
            report.append(f"- 建议金额：{best_signal['amount']}")
        else:
            report.append("⚠️ 市场无明显机会，建议观望")
        report.append("")
        
        # 风险提示
        report.append("## ⚠️ 风险提示")
        report.append("")
        report.append("- 本报告仅供参考，不构成投资建议")
        report.append("- 预测市场有风险，可能导致资金损失")
        report.append("- 建议先用模拟模式测试策略")
        report.append("- 只用闲钱投资，设置好止损")
        report.append("")
        
        report.append("=" * 70)
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None):
        """保存报告到文件"""
        if filename is None:
            filename = f"reports/daily_{datetime.now().strftime('%Y%m%d')}.md"
        
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"报告已保存：{filename}")
        return report


def main():
    """主函数"""
    import os
    
    # 创建报告目录
    os.makedirs('reports', exist_ok=True)
    
    # 加载配置
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except:
        config = {
            'polymarket': {'api_key': ''},
            'trading': {'max_bet': 100, 'stop_loss': 0.2, 'take_profit': 0.5},
            'monitor': {'volume_min': 1000}
        }
    
    # 生成报告
    reporter = DailyReport(config)
    report = reporter.save_report()
    
    print()
    print(report)


if __name__ == "__main__":
    main()
