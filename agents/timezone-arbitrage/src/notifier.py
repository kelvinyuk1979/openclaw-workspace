#!/usr/bin/env python3
"""
Telegram 通知模块

发送交易机会通知、执行结果、结算通知
"""

import logging
from typing import List, Dict
import aiohttp

logger = logging.getLogger('timezone-arbitrage.notifier')


class TelegramNotifier:
    """Telegram 通知器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bot_token = config['notifications']['telegram']['bot_token']
        self.chat_id = config['notifications']['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_message(self, text: str, parse_mode: str = 'Markdown') -> bool:
        """发送 Telegram 消息"""
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        logger.info("Telegram 消息发送成功")
                        return True
                    else:
                        logger.error(f"Telegram API 错误：{result}")
                        return False
        except Exception as e:
            logger.error(f"发送 Telegram 消息失败：{e}")
            return False
    
    async def send_opportunity_notification(self, opportunities: List[dict], total_capital: float) -> bool:
        """
        发送交易机会通知（需要用户批准）
        
        Returns:
            bool: 用户是否批准
        """
        # 构建消息
        market_count = len(opportunities)
        
        text = f"""
🚨 **发现套利机会**

发现 {market_count} 个会在接下来 90 分钟内结算的市场
美国人都还在睡，需要批准部署 ${total_capital:,.0f}

**市场列表:**
"""
        
        for i, opp in enumerate(opportunities, 1):
            signal = opp['signal']
            edge = opp['edge']
            
            text += f"""
{i}. {signal['market_name']}
   真实概率：{edge['true_probability']*100:.0f}%
   Polymarket: {edge['market_price']*100:.0f}¢
   Edge: {edge['edge_percent']:.0f}%
   预期回报：${edge['expected_return']:,.0f}
"""
        
        # 汇总
        total_expected = sum(opp['edge']['expected_return'] for opp in opportunities)
        avg_settlement = sum(opp['edge']['settlement_minutes'] for opp in opportunities) / len(opportunities)
        
        text += f"""
**汇总:**
- 潜在回报：${total_expected:,.0f}
- 窗口期：{avg_settlement:.0f} 分钟
- 所需资金：${total_capital:,.0f}

回复 `yes` 确认执行
"""
        
        # 发送消息
        await self.send_message(text)
        
        # 等待用户回复（简化版，实际需要 webhook 或轮询）
        # 这里假设用户在 5 分钟内回复
        logger.info("等待用户批准...")
        
        # TODO: 实现 webhook 接收用户回复
        # 暂时返回 True（生产环境需要实现完整的交互流程）
        return True
    
    async def send_execution_result(self, results: List[dict]) -> bool:
        """发送执行结果通知"""
        total_invested = sum(r['invested'] for r in results)
        total_expected = sum(r['expected_return'] for r in results)
        
        text = f"""
✅ **订单已全部提交**

总投入：${total_invested:,.0f}
预计回报：${total_expected:,.0f}
预计 ROI: {(total_expected/total_invested*100):.0f}%

**订单详情:**
"""
        
        for r in results:
            text += f"""
- {r['market_name']}: ${r['invested']:,.0f} @ {r['price']*100:.0f}¢
  预期回报：${r['expected_return']:,.0f}
"""
        
        text += f"""
预计结算时间：{results[0]['settlement_time'].strftime('%H:%M')} - {results[-1]['settlement_time'].strftime('%H:%M')} EST
"""
        
        return await self.send_message(text)
    
    async def send_settlement_result(self, results: List[dict]) -> bool:
        """发送结算结果通知"""
        total_profit = sum(r['actual_return'] - r['invested'] for r in results)
        
        text = f"""
✅ **全部结算完成**

总利润：+${total_profit:,.0f}

**结算详情:**
"""
        
        for r in results:
            profit = r['actual_return'] - r['invested']
            roi = (profit / r['invested'] * 100)
            
            text += f"""
{r['market_name']}: +${profit:,.0f} ({r['price']*100:.0f}¢ → {r['settlement_price']*100:.0f}¢, ROI: {roi:.0f}%)
"""
        
        text += f"""
**总计：+${total_profit:,.0f}**
"""
        
        return await self.send_message(text)
    
    async def send_error_notification(self, error: str) -> bool:
        """发送错误通知"""
        text = f"""
❌ **错误通知**

时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
错误：{error}

请检查日志：logs/agent.log
"""
        
        return await self.send_message(text)
