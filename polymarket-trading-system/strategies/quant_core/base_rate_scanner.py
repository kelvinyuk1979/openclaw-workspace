#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础率扫描器 [FRM-004]
识别市场定价与历史基础率的偏差，发现套利机会
"""

from typing import Dict, Optional, List

class BaseRateScanner:
    """基础率扫描器"""
    
    def __init__(self):
        """初始化基础率数据库"""
        # 历史基础率数据
        # 来源：历史统计、学术研究、专业数据库
        self.base_rates = {
            # 政治类
            'incumbent_approval_50plus': 0.82,  # 支持率>50% 的现任者胜率
            'incumbent_approval_below_40': 0.35,  # 支持率<40% 的现任者胜率
            'primary_challenger_vs_incumbent': 0.25,  # 挑战者 vs 现任者初选
            
            # 经济类
            'fed_hold_unemp_below_4': 0.74,  # 失业率<4% 时美联储按兵不动
            'recession_after_inversion': 0.68,  # 收益率倒挂后衰退概率
            'rate_cut_after_hike_cycle': 0.85,  # 加息周期后降息概率
            
            # 地缘政治类
            'ceasefire_after_talks': 0.41,  # 谈判后停火概率
            'escalation_after_strike': 0.35,  # 袭击后升级概率
            
            #  crypto 类
            'crypto_etf_approval': 0.65,  # 加密货币 ETF 获批概率（历史平均）
            'btc_halving_bull_run': 0.75,  # 减半后牛市概率
            
            # 体育类
            'home_team_win': 0.58,  # 主队胜率（所有运动平均）
            'favorite_win_spread': 0.52,  # 热门队赢盘率
            
            # 商业类
            'merger_approval': 0.78,  # 并购案获批概率
            'ipo_first_day_pop': 0.65,  # IPO 首日上涨概率
        }
    
    def scan(self, market_price: float, event_type: str) -> Optional[Dict]:
        """
        扫描单个市场的基础率偏差
        
        Args:
            market_price: 市场价格（0-1）
            event_type: 事件类型（匹配 base_rates 键名）
        
        Returns:
            机会字典 或 None
        """
        base_rate = self.base_rates.get(event_type)
        
        if not base_rate:
            return None
        
        gap = base_rate - market_price
        
        if abs(gap) < 0.05:  # 缺口小于 5% 不交易
            return None
        
        signal = 'BUY' if gap > 0 else 'SELL'
        
        return {
            'event_type': event_type,
            'base_rate': base_rate,
            'market_price': market_price,
            'gap': gap,
            'edge': abs(gap),
            'signal': signal,
            'confidence': 'HIGH' if abs(gap) > 0.15 else 'MEDIUM'
        }
    
    def scan_multiple(self, markets: List[Dict]) -> List[Dict]:
        """
        扫描多个市场
        
        Args:
            markets: [{'event_type': str, 'market_price': float}, ...]
        
        Returns:
            机会列表（按 edge 排序）
        """
        opportunities = []
        
        for m in markets:
            result = self.scan(m['market_price'], m['event_type'])
            if result:
                opportunities.append(result)
        
        # 按 edge 排序
        opportunities.sort(key=lambda x: x['edge'], reverse=True)
        
        return opportunities
    
    def add_base_rate(self, event_type: str, rate: float, source: str = '') -> bool:
        """
        添加新的基础率数据
        
        Args:
            event_type: 事件类型
            rate: 基础率（0-1）
            source: 数据来源
        
        Returns:
            是否成功
        """
        if rate < 0 or rate > 1:
            return False
        
        self.base_rates[event_type] = rate
        return True
    
    def get_base_rate(self, event_type: str) -> Optional[float]:
        """获取特定事件类型的基础率"""
        return self.base_rates.get(event_type)
    
    def list_all(self) -> Dict:
        """列出所有基础率"""
        return self.base_rates.copy()


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("📊 基础率扫描器 - 测试")
    print("="*60)
    
    scanner = BaseRateScanner()
    
    # 测试场景
    test_markets = [
        {'event_type': 'incumbent_approval_50plus', 'market_price': 0.60},
        {'event_type': 'fed_hold_unemp_below_4', 'market_price': 0.80},
        {'event_type': 'ceasefire_after_talks', 'market_price': 0.25},
        {'event_type': 'crypto_etf_approval', 'market_price': 0.55},
        {'event_type': 'btc_halving_bull_run', 'market_price': 0.85},
    ]
    
    print("\n🔍 扫描市场...\n")
    print(f"{'事件类型':<35} {'基础率':<10} {'市场价':<10} {'缺口':<10} {'信号':<8}")
    print("-" * 75)
    
    opportunities = scanner.scan_multiple(test_markets)
    
    if opportunities:
        for opp in opportunities:
            print(f"{opp['event_type']:<35} {opp['base_rate']:<10.0%} "
                  f"{opp['market_price']:<10.0%} {opp['gap']:<+10.0%} {opp['signal']:<8}")
        
        print(f"\n✅ 发现 {len(opportunities)} 个套利机会")
    else:
        print("⚠️  无套利机会（所有缺口 < 5%）")
    
    # 显示所有基础率
    print("\n\n📚 基础率数据库：")
    print("-" * 60)
    
    for event_type, rate in sorted(scanner.base_rates.items()):
        print(f"  {event_type:<35} {rate:.0%}")
    
    print("\n" + "="*60)
    print("💡 提示：基础率帮助避免代表性启发式偏差")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
