#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket API 数据获取模块
获取市场数据、价格、交易量等信息
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

class PolymarketAPI:
    """Polymarket API 客户端"""
    
    def __init__(self, api_key: str = None):
        """
        初始化
        
        Args:
            api_key: Polymarket API Key（可选，公共端点不需要）
        """
        self.base_url = "https://api.polymarket.com"
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def get_markets(self, category: str = None, limit: int = 50) -> List[Dict]:
        """
        获取市场列表
        
        Args:
            category: 分类（politics, crypto, sports, etc.）
            limit: 返回数量限制
        
        Returns:
            市场列表
        """
        endpoint = f"{self.base_url}/markets"
        params = {'limit': limit}
        
        if category:
            params['category'] = category
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取市场列表失败：{e}")
            return []
    
    def get_market_orders(self, market_id: str) -> Dict:
        """
        获取市场订单簿
        
        Args:
            market_id: 市场 ID
        
        Returns:
            订单簿数据
        """
        endpoint = f"{self.base_url}/markets/{market_id}/order-book"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取订单簿失败：{e}")
            return {}
    
    def get_market_prices(self, market_id: str) -> Dict:
        """
        获取市场价格
        
        Args:
            market_id: 市场 ID
        
        Returns:
            价格数据（yes/no 价格）
        """
        endpoint = f"{self.base_url}/markets/{market_id}/price"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取价格失败：{e}")
            return {}
    
    def get_market_trades(self, market_id: str, limit: int = 100) -> List[Dict]:
        """
        获取市场交易历史
        
        Args:
            market_id: 市场 ID
            limit: 返回数量
        
        Returns:
            交易历史
        """
        endpoint = f"{self.base_url}/markets/{market_id}/trades"
        params = {'limit': limit}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取交易历史失败：{e}")
            return []
    
    def get_user_positions(self, user_address: str) -> List[Dict]:
        """
        获取用户持仓
        
        Args:
            user_address: 钱包地址
        
        Returns:
            持仓列表
        """
        endpoint = f"{self.base_url}/users/{user_address}/positions"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取持仓失败：{e}")
            return []
    
    def search_markets(self, query: str) -> List[Dict]:
        """
        搜索市场
        
        Args:
            query: 搜索关键词
        
        Returns:
            匹配的市场列表
        """
        endpoint = f"{self.base_url}/markets/search"
        params = {'q': query}
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 搜索市场失败：{e}")
            return []
    
    def get_market_details(self, market_id: str) -> Dict:
        """
        获取市场详情
        
        Args:
            market_id: 市场 ID
        
        Returns:
            市场详细信息
        """
        endpoint = f"{self.base_url}/markets/{market_id}"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取市场详情失败：{e}")
            return {}
    
    def get_categories(self) -> List[Dict]:
        """
        获取所有分类
        
        Returns:
            分类列表
        """
        endpoint = f"{self.base_url}/categories"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取分类失败：{e}")
            return []
    
    def get_market_volume(self, market_id: str) -> Dict:
        """
        获取市场交易量
        
        Args:
            market_id: 市场 ID
        
        Returns:
            交易量数据
        """
        endpoint = f"{self.base_url}/markets/{market_id}/volume"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取交易量失败：{e}")
            return {}


class MockPolymarketAPI:
    """模拟 Polymarket API（用于测试，无需真实 API）"""
    
    def __init__(self):
        """初始化模拟数据"""
        self.mock_markets = [
            {
                'id': 'fed-cut-jun-2026',
                'title': 'Will the Fed cut rates in June 2026?',
                'category': 'economics',
                'yes_price': 0.40,
                'no_price': 0.60,
                'volume_24h': 125000,
                'open_interest': 450000
            },
            {
                'id': 'trump-oh-2026',
                'title': 'Will Trump be in Ohio in 2026?',
                'category': 'politics',
                'yes_price': 0.52,
                'no_price': 0.48,
                'volume_24h': 85000,
                'open_interest': 320000
            },
            {
                'id': 'ceasefire-2024',
                'title': 'Will there be a ceasefire in 2024?',
                'category': 'geopolitics',
                'yes_price': 0.30,
                'no_price': 0.70,
                'volume_24h': 250000,
                'open_interest': 680000
            },
            {
                'id': 'btc-100k-2026',
                'title': 'Will BTC reach $100K in 2026?',
                'category': 'crypto',
                'yes_price': 0.65,
                'no_price': 0.35,
                'volume_24h': 520000,
                'open_interest': 1200000
            },
            {
                'id': 'eth-etf-2026',
                'title': 'Will ETH ETF be approved in 2026?',
                'category': 'crypto',
                'yes_price': 0.55,
                'no_price': 0.45,
                'volume_24h': 180000,
                'open_interest': 420000
            }
        ]
    
    def get_markets(self, category: str = None, limit: int = 50) -> List[Dict]:
        """获取模拟市场数据"""
        markets = self.mock_markets.copy()
        
        if category:
            markets = [m for m in markets if m['category'] == category]
        
        return markets[:limit]
    
    def get_market_details(self, market_id: str) -> Dict:
        """获取模拟市场详情"""
        for m in self.mock_markets:
            if m['id'] == market_id:
                return m
        return {}
    
    def search_markets(self, query: str) -> List[Dict]:
        """搜索模拟市场"""
        query = query.lower()
        return [m for m in self.mock_markets if query in m['title'].lower()]


def main():
    """测试函数"""
    print("\n" + "="*60)
    print("🔌 Polymarket API 数据获取 - 测试")
    print("="*60)
    
    # 使用模拟 API（无需真实 API Key）
    api = MockPolymarketAPI()
    
    # 测试 1：获取所有市场
    print("\n📊 测试 1：获取市场列表")
    print("-" * 60)
    
    markets = api.get_markets(limit=10)
    
    print(f"市场总数：{len(markets)}\n")
    print(f"{'市场 ID':<25} {'分类':<15} {'Yes 价':<10} {'24h 量':<12}")
    print("-" * 65)
    
    for m in markets:
        print(f"{m['id']:<25} {m['category']:<15} {m['yes_price']:<10.0%} "
              f"${m['volume_24h']:<11,.0f}")
    
    # 测试 2：按分类筛选
    print("\n\n📊 测试 2：按分类筛选（Crypto）")
    print("-" * 60)
    
    crypto_markets = api.get_markets(category='crypto', limit=10)
    
    for m in crypto_markets:
        print(f"  {m['title']}")
        print(f"    Yes: {m['yes_price']:.0%}, Volume: ${m['volume_24h']:,}\n")
    
    # 测试 3：搜索市场
    print("\n📊 测试 3：搜索市场（关键词：Fed）")
    print("-" * 60)
    
    search_results = api.search_markets('Fed')
    
    for m in search_results:
        print(f"  ✅ {m['title']}")
    
    # 测试 4：获取市场详情
    print("\n\n📊 测试 4：获取市场详情")
    print("-" * 60)
    
    details = api.get_market_details('btc-100k-2026')
    if details:
        print(f"标题：{details['title']}")
        print(f"分类：{details['category']}")
        print(f"Yes 价格：{details['yes_price']:.0%}")
        print(f"No 价格：{details['no_price']:.0%}")
        print(f"24h 交易量：${details['volume_24h']:,}")
        print(f"未平仓合约：${details['open_interest']:,}")
    
    print("\n" + "="*60)
    print("💡 提示：真实 API 需要配置 API Key")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
