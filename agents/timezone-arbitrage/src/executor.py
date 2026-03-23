#!/usr/bin/env python3
"""
交易执行模块

负责：
- 连接 Polymarket API
- 执行订单
- 监控订单状态
- 记录交易结果
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import aiohttp
import hashlib
import hmac
import time

logger = logging.getLogger('timezone-arbitrage.executor')


class OrderType(str, Enum):
    """订单类型"""
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class Order:
    """订单数据结构"""
    order_id: str
    market_id: str
    market_name: str
    side: str  # "yes" or "no"
    order_type: OrderType
    price: float  # 价格（美分，0-1）
    quantity: float  # 数量（美元）
    status: OrderStatus
    filled_quantity: float
    average_price: float
    created_at: datetime
    updated_at: datetime
    raw_response: dict


class TradeExecutor:
    """交易执行器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.api_key = config['polymarket']['api_key']
        self.api_secret = config['polymarket']['api_secret']
        self.base_url = "https://api.polymarket.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 订单簿缓存
        self.order_cache = {}
        
        # 风控参数
        self.rate_limit = config['polymarket']['rate_limit']
        self.slippage = config['polymarket']['slippage']
        
        logger.info("✅ 交易执行器初始化完成")
    
    async def start(self):
        """启动交易会话"""
        self.session = aiohttp.ClientSession(
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        logger.info("交易会话已启动")
    
    async def stop(self):
        """停止交易会话"""
        if self.session:
            await self.session.close()
            logger.info("交易会话已关闭")
    
    def _generate_signature(self, method: str, path: str, timestamp: int, body: str = "") -> str:
        """生成 API 请求签名"""
        message = f"{timestamp}{method}{path}"
        if body:
            message += body
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def _request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        """发送 API 请求"""
        if not self.session:
            await self.start()
        
        timestamp = int(time.time() * 1000)
        body = ""
        
        if data:
            import json
            body = json.dumps(data, separators=(',', ':'))
        
        signature = self._generate_signature(method, path, timestamp, body)
        
        headers = {
            'POLYMARKET_API_KEY': self.api_key,
            'POLYMARKET_API_SIGNATURE': signature,
            'POLYMARKET_API_TIMESTAMP': str(timestamp)
        }
        
        url = f"{self.base_url}{path}"
        
        try:
            async with self.session.request(
                method,
                url,
                headers=headers,
                json=data if data else None,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return result
                else:
                    logger.error(f"API 错误 {response.status}: {result}")
                    raise Exception(f"API 错误：{result}")
        
        except aiohttp.ClientError as e:
            logger.error(f"网络错误：{e}")
            raise
        except Exception as e:
            logger.error(f"请求失败：{e}")
            raise
    
    async def get_market_info(self, market_id: str) -> dict:
        """获取市场信息"""
        path = f"/markets/{market_id}"
        return await self._request("GET", path)
    
    async def get_orderbook(self, market_id: str) -> dict:
        """获取订单簿"""
        path = f"/orderbook/{market_id}"
        return await self._request("GET", path)
    
    async def get_balance(self) -> dict:
        """获取账户余额"""
        path = "/balances"
        return await self._request("GET", path)
    
    async def place_order(
        self,
        market_id: str,
        side: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: OrderType = OrderType.MARKET
    ) -> Order:
        """
        下单
        
        Args:
            market_id: 市场 ID
            side: "yes" 或 "no"
            quantity: 数量（美元）
            price: 价格（美分，0-1），限价单必填
            order_type: 订单类型
        
        Returns:
            Order: 订单对象
        """
        path = "/order"
        
        # 构建订单数据
        data = {
            "market_id": market_id,
            "side": side,
            "quantity": quantity,
            "order_type": order_type.value
        }
        
        if order_type == OrderType.LIMIT and price:
            data["price"] = price
        
        # 生成订单 ID
        order_id = f"tz_arb_{market_id}_{int(time.time())}"
        data["client_order_id"] = order_id
        
        try:
            response = await self._request("POST", path, data)
            
            order = Order(
                order_id=order_id,
                market_id=market_id,
                market_name=data.get('market_name', market_id),
                side=side,
                order_type=order_type,
                price=price if price else response.get('price', 0),
                quantity=quantity,
                status=OrderStatus.SUBMITTED,
                filled_quantity=response.get('filled_quantity', 0),
                average_price=response.get('average_price', 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                raw_response=response
            )
            
            logger.info(f"📦 订单已提交：{order_id} - {side} ${quantity} @ {price or 'MARKET'}")
            
            # 缓存订单
            self.order_cache[order_id] = order
            
            return order
        
        except Exception as e:
            logger.error(f"下单失败：{e}")
            raise
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        path = f"/order/{order_id}"
        
        try:
            await self._request("DELETE", path)
            logger.info(f"❌ 订单已取消：{order_id}")
            return True
        except Exception as e:
            logger.error(f"取消订单失败：{e}")
            return False
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """查询订单状态"""
        path = f"/order/{order_id}"
        
        try:
            response = await self._request("GET", path)
            status = response.get('status', 'unknown')
            return OrderStatus(status)
        except Exception as e:
            logger.error(f"查询订单状态失败：{e}")
            return OrderStatus.FAILED
    
    async def execute_multiple(self, opportunities: List[dict]) -> List[dict]:
        """
        批量执行交易
        
        Args:
            opportunities: 机会列表（包含 edge 数据）
        
        Returns:
            List[dict]: 执行结果
        """
        results = []
        
        for opp in opportunities:
            signal = opp['signal']
            edge = opp['edge']
            
            try:
                # 获取市场信息
                market_info = await self.get_market_info(signal['market_id'])
                
                # 检查滑点
                current_price = market_info.get('yes_price', 0)
                max_price = current_price * (1 + self.slippage['max_slippage_percent'] / 100)
                
                if edge['market_price'] > max_price:
                    logger.warning(f"滑点过大，跳过 {signal['market_name']}: {edge['market_price']} > {max_price}")
                    continue
                
                # 下单
                order = await self.place_order(
                    market_id=signal['market_id'],
                    side="yes",  # 做多 YES
                    quantity=edge['required_capital'],
                    price=edge['market_price'] if self.slippage['use_limit_orders'] else None,
                    order_type=OrderType.LIMIT if self.slippage['use_limit_orders'] else OrderType.MARKET
                )
                
                # 等待订单成交（简化版）
                await asyncio.sleep(2)
                
                result = {
                    'market_name': signal['market_name'],
                    'market_id': signal['market_id'],
                    'order_id': order.order_id,
                    'invested': edge['required_capital'],
                    'price': edge['market_price'],
                    'expected_return': edge['expected_return'],
                    'settlement_time': signal['settlement_time'],
                    'status': 'submitted'
                }
                
                results.append(result)
                logger.info(f"✅ 执行成功：{signal['market_name']} - ${edge['required_capital']} @ {edge['market_price']*100:.1f}¢")
            
            except Exception as e:
                logger.error(f"执行失败 {signal['market_name']}: {e}")
                results.append({
                    'market_name': signal['market_name'],
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results
    
    async def monitor_orders(self, order_ids: List[str]) -> List[Order]:
        """监控订单状态"""
        orders = []
        
        for order_id in order_ids:
            try:
                status = await self.get_order_status(order_id)
                
                if order_id in self.order_cache:
                    order = self.order_cache[order_id]
                    order.status = status
                    order.updated_at = datetime.utcnow()
                    orders.append(order)
                    
                    logger.info(f"订单状态：{order_id} - {status.value}")
            
            except Exception as e:
                logger.error(f"监控订单失败 {order_id}: {e}")
        
        return orders
    
    async def check_settlement(self, market_id: str) -> Tuple[bool, float]:
        """
        检查市场结算结果
        
        Returns:
            Tuple[bool, float]: (是否结算，结算价格)
        """
        try:
            market_info = await self.get_market_info(market_id)
            
            is_settled = market_info.get('settled', False)
            settlement_price = market_info.get('settlement_price', 0)
            
            if is_settled:
                logger.info(f"✅ 市场已结算：{market_id} - {settlement_price}")
            
            return is_settled, settlement_price
        
        except Exception as e:
            logger.error(f"检查结算失败 {market_id}: {e}")
            return False, 0


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.daily_volume = 0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.daily_pnl = 0
    
    def check_pre_trade(self, trade_size: float) -> Tuple[bool, str]:
        """
        交易前风控检查
        
        Returns:
            Tuple[bool, str]: (是否允许交易，原因)
        """
        risk_config = self.config['risk_management']
        
        # 检查每日交易量
        if self.daily_volume + trade_size > risk_config['max_daily_volume']:
            return False, "超过每日交易量限制"
        
        # 检查连续亏损
        if self.consecutive_losses >= risk_config['kill_switch']['consecutive_losses']:
            return False, "连续亏损达到限制"
        
        # 检查每日亏损
        if abs(self.daily_pnl) >= risk_config['kill_switch']['daily_loss_threshold']:
            return False, "达到每日亏损阈值"
        
        return True, "通过风控检查"
    
    def record_trade(self, trade_size: float, pnl: float):
        """记录交易"""
        self.daily_volume += trade_size
        self.daily_trades += 1
        self.daily_pnl += pnl
        
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        logger.info(f"风控记录：交易量=${self.daily_volume}, 交易数={self.daily_trades}, PnL=${self.daily_pnl}")
    
    def reset_daily(self):
        """重置每日统计"""
        self.daily_volume = 0
        self.daily_trades = 0
        self.daily_pnl = 0
        self.consecutive_losses = 0
        logger.info("风控统计已重置")
