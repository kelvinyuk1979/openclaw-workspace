#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket Fast Loop - 主程序
自动化预测市场交易

功能：
- 市场扫描
- 信号生成
- 自动交易
- 风险控制
- Telegram 通知
"""

import json
import time
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

# 导入自定义模块
from monitor import PolymarketMonitor, test_connection
from trader import PolymarketTrader
from analyzer import PolymarketAnalyzer
from strategies.basic import BasicStrategy
from strategies.momentum import MomentumStrategy

# 配置日志
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_config() -> Optional[Dict]:
    """加载配置文件"""
    config_path = 'config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"✅ 配置文件加载成功：{config_path}")
            return config
    except FileNotFoundError:
        logger.error(f"❌ 配置文件不存在：{config_path}")
        logger.error("请复制 config.example.json 为 config.json 并填入配置")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 解析失败：{e}")
        return None


class TradingBot:
    """Polymarket 交易机器人"""
    
    def __init__(self, config: Dict, dry_run: bool = True):
        self.config = config
        self.dry_run = dry_run
        self.running = False
        
        # 初始化组件
        api_key = config['polymarket'].get('api_key', '')
        api_secret = config['polymarket'].get('api_secret', '')
        
        self.monitor = PolymarketMonitor(api_key)
        self.trader = PolymarketTrader(api_key, api_secret)
        self.analyzer = PolymarketAnalyzer()
        
        # 初始化策略
        self.basic_strategy = BasicStrategy(config)
        self.momentum_strategy = MomentumStrategy(config)
        
        # 状态跟踪
        self.positions = {}
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.last_check = None
        
        logger.info(f"🤖 交易机器人初始化完成 (模拟模式：{dry_run})")
    
    def scan_and_trade(self):
        """扫描市场并执行交易"""
        logger.info("🔍 开始扫描市场...")
        
        # 获取市场列表
        markets = self.monitor.get_markets(limit=50)
        if not markets:
            logger.warning("⚠️ 未获取到市场数据")
            return
        
        # 获取当前持仓
        if not self.dry_run:
            positions = self.trader.get_positions()
            self.positions = {p.market_id: p for p in positions}
        
        # 策略评估
        decisions = []
        
        # 基础策略
        basic_decisions = self.basic_strategy.batch_evaluate(markets, self.positions)
        decisions.extend(basic_decisions)
        logger.info(f"📊 基础策略生成 {len(basic_decisions)} 个信号")
        
        # 动量策略
        momentum_decisions = self.momentum_strategy.batch_evaluate(markets)
        decisions.extend(momentum_decisions)
        logger.info(f"📈 动量策略生成 {len(momentum_decisions)} 个信号")
        
        # 去重并按置信度排序
        unique_decisions = {}
        for d in decisions:
            if d.market_id not in unique_decisions or d.confidence > unique_decisions[d.market_id].confidence:
                unique_decisions[d.market_id] = d
        
        sorted_decisions = sorted(unique_decisions.values(), key=lambda x: x.confidence, reverse=True)
        
        # 执行交易
        if sorted_decisions:
            logger.info(f"\n🎯 发现 {len(sorted_decisions)} 个交易机会:")
            for i, decision in enumerate(sorted_decisions[:5], 1):
                market_id_str = str(decision.market_id)[:8]
                logger.info(f"  {i}. [{decision.confidence:.0%}] {decision.action.upper()} "
                           f"{market_id_str}... - {decision.reason}")
            
            # 执行最高置信度的交易（限制每日交易次数）
            max_trades_per_day = self.config.get('risk_management', {}).get('daily_limit', 5)
            
            if self.trades_today < max_trades_per_day:
                best_decision = sorted_decisions[0]
                self.execute_decision(best_decision)
            else:
                logger.warning(f"⚠️ 已达每日交易上限 ({max_trades_per_day})")
        else:
            logger.info("💤 暂无交易机会")
        
        self.last_check = datetime.now()
    
    def execute_decision(self, decision):
        """执行交易决策"""
        market_id_str = str(decision.market_id)[:8]
        logger.info(f"\n💼 执行交易：{decision.action.upper()}")
        logger.info(f"   市场：{market_id_str}...")
        logger.info(f"   价格：{decision.price:.4f}")
        logger.info(f"   金额：{decision.amount} USDC")
        logger.info(f"   原因：{decision.reason}")
        
        if self.dry_run:
            logger.info("   📝 [模拟交易，未实际执行]")
            return
        
        # 确定交易方向
        if decision.action in ['buy_yes', 'buy_no']:
            side = 'yes' if decision.action == 'buy_yes' else 'no'
            result = self.trader.place_order(
                market_id=decision.market_id,
                side=side,
                price=decision.price,
                amount=decision.amount,
                dry_run=False
            )
            
            if result:
                self.trades_today += 1
                logger.info("✅ 交易执行成功")
            else:
                logger.error("❌ 交易执行失败")
        
        elif decision.action == 'sell':
            # 平仓逻辑
            position = self.positions.get(decision.market_id)
            if position:
                success = self.trader.close_position(
                    market_id=decision.market_id,
                    side=position.side,
                    dry_run=False
                )
                if success:
                    logger.info("✅ 平仓成功")
                else:
                    logger.error("❌ 平仓失败")
    
    def check_risk_limits(self) -> bool:
        """检查风险限制"""
        risk_config = self.config.get('risk_management', {})
        
        # 检查每日交易上限
        daily_limit = risk_config.get('daily_limit', 5)
        if self.trades_today >= daily_limit:
            logger.warning(f"⚠️ 已达每日交易上限：{self.trades_today}/{daily_limit}")
            return False
        
        # 检查最大回撤
        max_drawdown = risk_config.get('max_drawdown', 0.3)
        if self.daily_pnl < -max_drawdown * 1000:  # 假设本金 1000
            logger.warning(f"⚠️ 触及最大回撤限制：{self.daily_pnl:.2f}")
            return False
        
        return True
    
    def print_status(self):
        """打印状态报告"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 交易状态报告")
        logger.info("=" * 60)
        logger.info(f"   运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   模式：{'📝 模拟交易' if self.dry_run else '💰 实盘交易'}")
        logger.info(f"   今日交易：{self.trades_today} 笔")
        logger.info(f"   今日盈亏：{self.daily_pnl:.2f} USDC")
        logger.info(f"   当前持仓：{len(self.positions)} 个")
        logger.info(f"   最后扫描：{self.last_check.strftime('%H:%M:%S') if self.last_check else 'N/A'}")
        logger.info("=" * 60 + "\n")
    
    def run(self, scan_interval: int = 5):
        """主循环"""
        logger.info("\n🚀 开始交易循环...")
        logger.info(f"   扫描间隔：{scan_interval} 秒")
        logger.info(f"   按 Ctrl+C 停止\n")
        
        self.running = True
        
        try:
            while self.running:
                # 检查风险限制
                if self.check_risk_limits():
                    # 扫描和交易
                    self.scan_and_trade()
                    
                    # 打印状态（每小时）
                    if self.last_check and (datetime.now() - self.last_check).seconds > 3600:
                        self.print_status()
                
                # 等待下一次扫描
                time.sleep(scan_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⛔ 用户中断，停止交易")
            self.running = False
        except Exception as e:
            logger.error(f"❌ 交易循环错误：{e}")
            self.running = False
        finally:
            self.print_status()
            logger.info("👋 交易机器人已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket Fast Loop - 自动化交易系统')
    parser.add_argument('--dry-run', action='store_true', help='模拟交易（不使用真实资金）')
    parser.add_argument('--interval', type=int, default=5, help='扫描间隔（秒）')
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("🚀 Polymarket Fast Loop 启动")
    logger.info(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 加载配置
    config = load_config()
    if not config:
        return
    
    # 显示配置
    logger.info("\n📋 配置信息:")
    logger.info(f"   最大投注：{config['trading']['max_bet']} USDC")
    logger.info(f"   止损比例：{config['trading']['stop_loss'] * 100}%")
    logger.info(f"   止盈比例：{config['trading']['take_profit'] * 100}%")
    logger.info(f"   扫描间隔：{args.interval} 秒")
    
    # 测试 API 连接
    if not args.dry_run:
        logger.info("\n🔌 测试 API 连接...")
        if not test_connection(config['polymarket']['api_key']):
            logger.warning("⚠️ API 连接测试失败，但仍可继续（可能是测试环境）")
    
    # 创建并运行机器人
    bot = TradingBot(config, dry_run=args.dry_run)
    bot.run(scan_interval=args.interval)


if __name__ == "__main__":
    main()
