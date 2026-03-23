#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 天气交易机器人 v2.0
基于 NWS 天气预报 + Polymarket 市场定价的套利策略

功能：
- 从 NWS 获取实时天气预报
- 从 Polymarket 获取市场数据
- 自动生成交易信号
- 模拟交易跟踪
- 回测功能
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from nws_api import NWSWeatherAPI
from weather_strategy import WeatherStrategy, WeatherSignal
from monitor import PolymarketMonitor
from weather_alert import send_alert_email

logger = logging.getLogger(__name__)

# 配置
CONFIG = {
    'entry_threshold': 0.15,      # 15¢ 买入
    'exit_threshold': 0.45,       # 45¢ 卖出
    'max_position': 0.05,         # 单笔最大 5%
    'min_confidence': 0.60,       # 最小置信度
    'initial_balance': 1000.0,    # 初始余额
    'cities': ['new_york', 'chicago', 'dallas', 'boston', 'denver'],
    'forecast_days': 5            # 预报天数
}


class WeatherBot:
    """天气交易机器人"""
    
    def __init__(self, config: Dict = None, dry_run: bool = True):
        self.config = config or CONFIG
        self.dry_run = dry_run
        self.balance = self.config['initial_balance']
        
        # 初始化组件
        self.nws_api = NWSWeatherAPI()
        self.strategy = WeatherStrategy(self.config)
        self.pm_monitor = PolymarketMonitor()
        
        # 持仓跟踪
        self.positions = []
        self.trades = []
        
        # 数据目录
        self.data_dir = Path(__file__).parent / 'weather_data'
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info(f"🤖 天气机器人初始化完成 (模拟模式：{dry_run})")
    
    def run_scan(self) -> List[WeatherSignal]:
        """执行一次扫描"""
        logger.info("\n" + "="*60)
        logger.info("🔍 开始扫描天气交易机会")
        logger.info("="*60)
        
        # 第 1 步：获取天气预报
        logger.info("\n📡 获取 NWS 天气预报...")
        all_forecasts = []
        
        for city in self.config['cities']:
            forecasts = self.nws_api.get_daily_highs(city, days=self.config['forecast_days'])
            all_forecasts.extend(forecasts)
            logger.info(f"  {city}: {len(forecasts)} 天预报")
        
        logger.info(f"✅ 共获取 {len(all_forecasts)} 条预报")
        
        # 第 2 步：获取 Polymarket 市场数据
        logger.info("\n📡 获取 Polymarket 市场数据...")
        markets = self.pm_monitor.get_markets(limit=100)
        
        # 筛选天气市场
        weather_markets = [
            m for m in markets 
            if 'temperature' in m.get('title', '').lower() 
            or '°f' in m.get('title', '').lower()
            or 'high' in m.get('title', '').lower()
        ]
        
        logger.info(f"✅ 找到 {len(weather_markets)} 个天气市场")
        
        # 第 3 步：生成交易信号
        logger.info("\n📊 生成交易信号...")
        signals = self.strategy.generate_signals(
            all_forecasts, 
            weather_markets, 
            self.balance
        )
        
        if signals:
            logger.info(f"\n🎯 发现 {len(signals)} 个交易机会:")
            for i, signal in enumerate(signals[:5], 1):
                logger.info(f"\n{i}. {signal.city} - {signal.date}")
                logger.info(f"   预报温度：{signal.forecast_temp}°F")
                logger.info(f"   市场：{signal.market_bucket}")
                logger.info(f"   价格：{signal.market_price:.2f}¢")
                logger.info(f"   置信度：{signal.confidence:.0%}")
                logger.info(f"   期望值：{signal.expected_value:.3f}")
                logger.info(f"   建议仓位：${signal.position_size:.2f}")
                logger.info(f"   原因：{signal.reason}")
            
            # 发送警报邮件
            logger.info("\n📧 发送交易信号通知邮件...")
            email_sent = send_alert_email(signals, self.balance)
            if email_sent:
                logger.info("✅ 警报邮件已发送！请检查邮箱")
            else:
                logger.warning("⚠️ 邮件发送失败")
        else:
            logger.info("⚠️ 暂无交易信号")
        
        # 第 4 步：执行交易（模拟）
        if signals and not self.dry_run:
            logger.info("\n💼 执行交易...")
            for signal in signals[:3]:  # 最多执行前 3 个
                self._execute_signal(signal)
        
        # 保存结果
        self._save_scan_result(signals)
        
        return signals
    
    def _execute_signal(self, signal: WeatherSignal):
        """执行交易信号"""
        if self.dry_run:
            logger.info(f"📝 [模拟] 买入 {signal.position_size:.2f} USD @ {signal.market_price:.2f}¢")
        else:
            # TODO: 实现真实下单
            logger.info(f"💰 真实下单：{signal.position_size:.2f} USD")
        
        # 记录持仓
        self.positions.append({
            'signal': signal,
            'entry_price': signal.market_price,
            'entry_time': datetime.now().isoformat(),
            'shares': signal.position_size / signal.market_price,
            'status': 'open'
        })
        
        # 记录交易
        self.trades.append({
            'type': 'buy',
            'signal': signal,
            'price': signal.market_price,
            'amount': signal.position_size,
            'timestamp': datetime.now().isoformat()
        })
    
    def check_positions(self):
        """检查持仓，判断是否平仓"""
        logger.info("\n📊 检查持仓...")
        
        if not self.positions:
            logger.info("  无持仓")
            return
        
        for pos in self.positions:
            if pos['status'] != 'open':
                continue
            
            signal = pos['signal']
            current_price = self._get_current_price(signal)
            
            if current_price is None:
                continue
            
            # 检查是否应该平仓
            if self.strategy.should_exit(current_price, pos['entry_price']):
                self._close_position(pos, current_price)
    
    def _get_current_price(self, signal: WeatherSignal) -> Optional[float]:
        """获取当前价格"""
        # TODO: 实现实时价格获取
        # 这里简化处理
        return None
    
    def _close_position(self, position: Dict, current_price: float):
        """平仓"""
        shares = position['shares']
        entry_price = position['entry_price']
        
        pnl = shares * (current_price - entry_price)
        pnl_pct = (current_price - entry_price) / entry_price * 100
        
        position['status'] = 'closed'
        position['exit_price'] = current_price
        position['exit_time'] = datetime.now().isoformat()
        position['pnl'] = pnl
        position['pnl_pct'] = pnl_pct
        
        # 更新余额
        self.balance += shares * current_price
        
        logger.info(f"{'✅' if pnl > 0 else '❌'} 平仓：PnL = ${pnl:.2f} ({pnl_pct:.1f}%)")
        
        # 记录交易
        self.trades.append({
            'type': 'sell',
            'position': position,
            'price': current_price,
            'amount': shares * current_price,
            'pnl': pnl,
            'timestamp': datetime.now().isoformat()
        })
    
    def _save_scan_result(self, signals: List[WeatherSignal]):
        """保存扫描结果"""
        result_file = self.data_dir / f"scan_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'balance': self.balance,
            'signals_count': len(signals),
            'signals': [
                {
                    'city': s.city,
                    'date': s.date,
                    'forecast_temp': s.forecast_temp,
                    'market_bucket': s.market_bucket,
                    'market_price': s.market_price,
                    'confidence': s.confidence,
                    'expected_value': s.expected_value,
                    'position_size': s.position_size
                }
                for s in signals
            ],
            'open_positions': len([p for p in self.positions if p['status'] == 'open']),
            'total_trades': len(self.trades)
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 结果已保存：{result_file}")
    
    def get_summary(self) -> Dict:
        """获取交易摘要"""
        closed_trades = [t for t in self.trades if t['type'] == 'sell']
        
        total_pnl = sum(t.get('pnl', 0) for t in closed_trades)
        win_count = sum(1 for t in closed_trades if t.get('pnl', 0) > 0)
        win_rate = win_count / len(closed_trades) if closed_trades else 0
        
        return {
            'balance': self.balance,
            'initial_balance': self.config['initial_balance'],
            'total_pnl': total_pnl,
            'total_trades': len(closed_trades),
            'win_rate': win_rate,
            'open_positions': len([p for p in self.positions if p['status'] == 'open'])
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket 天气交易机器人')
    parser.add_argument('--dry-run', action='store_true', help='模拟交易')
    parser.add_argument('--interval', type=int, default=3600, help='扫描间隔（秒）')
    parser.add_argument('--cities', type=str, nargs='+', help='城市列表')
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置
    config = CONFIG.copy()
    if args.cities:
        config['cities'] = args.cities
    
    # 创建机器人
    bot = WeatherBot(config, dry_run=args.dry_run)
    
    # 运行扫描
    logger.info("\n" + "="*60)
    logger.info("🚀 Polymarket 天气交易机器人 v2.0")
    logger.info("="*60)
    logger.info(f"模式：{'📝 模拟交易' if args.dry_run else '💰 实盘交易'}")
    logger.info(f"城市：{', '.join(config['cities'])}")
    logger.info(f"扫描间隔：{args.interval} 秒")
    logger.info("="*60)
    
    # 单次扫描
    signals = bot.run_scan()
    
    # 显示摘要
    summary = bot.get_summary()
    logger.info("\n" + "="*60)
    logger.info("📊 交易摘要")
    logger.info("="*60)
    logger.info(f"余额：${summary['balance']:.2f}")
    logger.info(f"总盈亏：${summary['total_pnl']:.2f}")
    logger.info(f"交易次数：{summary['total_trades']}")
    logger.info(f"胜率：{summary['win_rate']:.1%}")
    logger.info(f"持仓：{summary['open_positions']} 个")
    logger.info("="*60)


if __name__ == "__main__":
    main()
