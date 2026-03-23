#!/usr/bin/env python3
"""
时区套利 Agent - 主程序入口

策略：利用跨时区信息差，在美国交易者 asleep 时段执行套利
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

import yaml

from monitor import InformationSourceMonitor
from analyzer import EdgeAnalyzer
from executor import TradeExecutor
from notifier import TelegramNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('timezone-arbitrage')


class TimezoneArbitrageAgent:
    """时区套利 Agent 主类"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """初始化 Agent"""
        self.config = self._load_config(config_path)
        self.running = False
        
        # 初始化组件
        self.monitor = InformationSourceMonitor(self.config)
        self.analyzer = EdgeAnalyzer(self.config)
        self.executor = TradeExecutor(self.config)
        self.notifier = TelegramNotifier(self.config)
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ 时区套利 Agent 初始化完成")
    
    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 替换环境变量
        import os
        for key, value in os.environ.items():
            if isinstance(config, dict):
                config_str = yaml.dump(config)
                config_str = config_str.replace(f'${{{key}}}', value)
                config = yaml.safe_load(config_str)
        
        return config
    
    def _signal_handler(self, signum, frame):
        """处理停止信号"""
        logger.info(f"收到信号 {signum}，正在停止...")
        self.running = False
    
    async def check_trading_hours(self) -> bool:
        """检查是否在交易时段内（美东时间凌晨 2-6 点）"""
        from pytz import timezone
        est = timezone('US/Eastern')
        now_est = datetime.now(est)
        
        start_hour = int(self.config['trading']['trading_hours']['start'].split(':')[0])
        end_hour = int(self.config['trading']['trading_hours']['end'].split(':')[0])
        
        return start_hour <= now_est.hour < end_hour
    
    async def find_opportunities(self) -> list:
        """发现套利机会"""
        opportunities = []
        
        # 从所有信息源获取最新数据
        signals = await self.monitor.get_all_signals()
        logger.info(f"获取到 {len(signals)} 个信号")
        
        for signal in signals:
            # 计算 Edge
            edge_data = self.analyzer.calculate_edge(signal)
            
            if edge_data['edge_percent'] >= self.config['trading']['min_edge_percent']:
                # 检查结算窗口
                if edge_data['settlement_minutes'] <= self.config['trading']['settlement_window_min']:
                    opportunities.append({
                        'signal': signal,
                        'edge': edge_data
                    })
                    logger.info(f"发现机会：{signal['market_name']} - Edge {edge_data['edge_percent']:.1f}%")
        
        return opportunities
    
    async def execute_trade(self, opportunities: list) -> bool:
        """执行交易"""
        total_capital = sum(opp['edge']['required_capital'] for opp in opportunities)
        
        # 发送通知等待批准
        approval = await self.notifier.send_opportunity_notification(opportunities, total_capital)
        
        if not approval:
            logger.info("用户未批准，取消交易")
            return False
        
        # 执行交易
        results = await self.executor.execute_multiple(opportunities)
        
        # 发送执行结果
        await self.notifier.send_execution_result(results)
        
        return True
    
    async def run(self):
        """主运行循环"""
        self.running = True
        logger.info("🚀 时区套利 Agent 启动")
        
        while self.running:
            try:
                # 检查交易时段
                if await self.check_trading_hours():
                    logger.info("当前在交易时段内，开始扫描...")
                    
                    # 发现机会
                    opportunities = await self.find_opportunities()
                    
                    if opportunities:
                        logger.info(f"发现 {len(opportunities)} 个套利机会")
                        
                        # 执行交易
                        await self.execute_trade(opportunities)
                    else:
                        logger.info("未发现符合条件的机会")
                else:
                    logger.debug("不在交易时段内，跳过扫描")
                
                # 等待 5 分钟
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"运行错误：{e}", exc_info=True)
                await asyncio.sleep(60)
        
        logger.info("时区套利 Agent 已停止")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='时区套利 Agent')
    parser.add_argument('--dev', action='store_true', help='开发模式')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    args = parser.parse_args()
    
    agent = TimezoneArbitrageAgent(config_path=args.config)
    await agent.run()


if __name__ == '__main__':
    asyncio.run(main())
