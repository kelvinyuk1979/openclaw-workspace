#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 交易执行模块
下单、平仓、风险管理
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Polymarket API 端点
POLYMARKET_API = "https://gamma-api.polymarket.com"

@dataclass
class Position:
    """持仓信息"""
    market_id: str
    side: str  # 'yes' or 'no'
    shares: float
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float


class PolymarketTrader:
    """Polymarket 交易器"""
    
    def __init__(self, api_key: str, api_secret: str = ""):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        self.positions: List[Position] = []
    
    def place_order(self, market_id: str, side: str, price: float, 
                    amount: float, dry_run: bool = False) -> Optional[Dict]:
        """
        下单交易
        
        Args:
            market_id: 市场 ID
            side: 'yes' 或 'no'
            price: 价格 (0-1)
            amount: 金额 (USDC)
            dry_run: 是否模拟交易
        
        Returns:
            订单结果或 None
        """
        if dry_run:
            logger.info(f"📝 [模拟交易] {side.upper()} Market: {market_id[:8]}...")
            logger.info(f"   价格：{price:.4f}, 金额：{amount} USDC")
            return {
                'status': 'dry_run',
                'market_id': market_id,
                'side': side,
                'price': price,
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # 构建订单
            order_data = {
                'marketId': market_id,
                'side': side,  # 'buy' or 'sell'
                'type': 'limit',  # 限价单
                'price': price,
                'size': amount,
                'expiration': 'GTC'  # Good Till Cancel
            }
            
            response = self.session.post(
                f"{POLYMARKET_API}/order",
                json=order_data,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ 下单成功：{result.get('orderId', 'N/A')}")
            return result
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ 下单失败 (HTTP {e.response.status_code}): {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 下单失败：{e}")
            return None
    
    def cancel_order(self, order_id: str, dry_run: bool = False) -> bool:
        """取消订单"""
        if dry_run:
            logger.info(f"📝 [模拟] 取消订单：{order_id}")
            return True
        
        try:
            response = self.session.delete(
                f"{POLYMARKET_API}/order/{order_id}",
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"✅ 订单已取消：{order_id}")
            return True
        except Exception as e:
            logger.error(f"❌ 取消订单失败：{e}")
            return False
    
    def get_positions(self) -> List[Position]:
        """获取当前持仓"""
        try:
            response = self.session.get(
                f"{POLYMARKET_API}/account/positions",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            positions = []
            for pos in data:
                positions.append(Position(
                    market_id=pos.get('marketId'),
                    side=pos.get('side'),
                    shares=float(pos.get('shares', 0)),
                    avg_price=float(pos.get('avgPrice', 0)),
                    current_price=float(pos.get('currentPrice', 0)),
                    pnl=float(pos.get('pnl', 0)),
                    pnl_percent=float(pos.get('pnlPercent', 0))
                ))
            
            self.positions = positions
            logger.info(f"📊 当前持仓：{len(positions)} 个")
            return positions
            
        except Exception as e:
            logger.error(f"❌ 获取持仓失败：{e}")
            return []
    
    def close_position(self, market_id: str, side: str, dry_run: bool = False) -> bool:
        """平仓"""
        if dry_run:
            logger.info(f"📝 [模拟平仓] {market_id[:8]}... {side.upper()}")
            return True
        
        # 实现平仓逻辑（反向交易）
        return self.place_order(market_id, 'sell' if side == 'buy' else 'buy', 
                               0.5, 0, dry_run) is not None
    
    def check_stop_loss(self, position: Position, stop_loss: float, 
                       take_profit: float, dry_run: bool = False) -> Optional[str]:
        """
        检查止损/止盈条件
        
        Returns:
            'stop_loss' / 'take_profit' / None
        """
        pnl_percent = position.pnl_percent
        
        if pnl_percent <= -stop_loss:
            logger.warning(f"⚠️ 触发止损！{position.market_id[:8]}... PnL: {pnl_percent:.2%}")
            return 'stop_loss'
        
        if pnl_percent >= take_profit:
            logger.info(f"🎯 触发止盈！{position.market_id[:8]}... PnL: {pnl_percent:.2%}")
            return 'take_profit'
        
        return None
    
    def get_account_summary(self) -> Optional[Dict]:
        """获取账户概览"""
        try:
            response = self.session.get(
                f"{POLYMARKET_API}/account",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ 获取账户信息失败：{e}")
            return None


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    trader = PolymarketTrader("test_key")
    print("Trader module loaded successfully")
