#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket API 连接测试工具
测试不同的 API 端点和认证方式
"""

import requests
import json
import time
from typing import Optional, Dict

# 可能的 API 端点
API_ENDPOINTS = [
    {
        'name': 'Polymarket Public API',
        'base': 'https://polymarket.com',
        'endpoint': '/api/markets',
        'auth_required': False
    },
    {
        'name': 'Gamma API (v1)',
        'base': 'https://gamma-api.polymarket.com',
        'endpoint': '/markets',
        'auth_required': False
    },
    {
        'name': 'GraphQL API',
        'base': 'https://subgraph.polymarket.com',
        'endpoint': '/graphql',
        'auth_required': False,
        'method': 'POST'
    },
    {
        'name': 'CLOB API (链上订单簿)',
        'base': 'https://clob.polymarket.com',
        'endpoint': '/markets',
        'auth_required': True
    },
]

# 测试用的市场 ID（已知存在的）
TEST_MARKET_IDS = [
    '0x9f7c71e46cb2d22917d6727b0ffc70c92d2bb309a39886a274ef43ab1969b3ce',
]


def test_endpoint(endpoint: Dict, api_key: Optional[str] = None) -> Dict:
    """测试单个 API 端点"""
    result = {
        'name': endpoint['name'],
        'url': f"{endpoint['base']}{endpoint['endpoint']}",
        'status': 'unknown',
        'status_code': None,
        'response_time': None,
        'data': None,
        'error': None
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    if api_key and endpoint.get('auth_required'):
        headers['Authorization'] = f'Bearer {api_key}'
    
    try:
        start_time = time.time()
        
        if endpoint.get('method') == 'POST':
            # GraphQL 查询
            query = """
            {
                markets(first: 5, orderBy: volume, orderDirection: desc) {
                    id
                    question
                    volume
                    liquidity
                }
            }
            """
            response = requests.post(
                f"{endpoint['base']}{endpoint['endpoint']}",
                json={'query': query},
                headers=headers,
                timeout=10
            )
        else:
            response = requests.get(
                f"{endpoint['base']}{endpoint['endpoint']}",
                params={'limit': 5},
                headers=headers,
                timeout=10
            )
        
        result['response_time'] = round((time.time() - start_time) * 1000, 2)
        result['status_code'] = response.status_code
        
        if response.status_code == 200:
            result['status'] = '✅ success'
            result['data'] = response.json()
        elif response.status_code == 401:
            result['status'] = '❌ unauthorized (需要 API Key)'
            result['error'] = '认证失败'
        elif response.status_code == 403:
            result['status'] = '❌ forbidden'
            result['error'] = '访问被拒绝'
        elif response.status_code == 404:
            result['status'] = '❌ not found'
            result['error'] = '端点不存在'
        elif response.status_code == 422:
            result['status'] = '❌ unprocessable entity'
            result['error'] = '请求参数错误'
        else:
            result['status'] = f'❌ HTTP {response.status_code}'
            result['error'] = response.text[:200]
            
    except requests.exceptions.Timeout:
        result['status'] = '❌ timeout'
        result['error'] = '请求超时 (10 秒)'
    except requests.exceptions.ConnectionError as e:
        result['status'] = '❌ connection error'
        result['error'] = str(e)[:200]
    except Exception as e:
        result['status'] = '❌ error'
        result['error'] = str(e)[:200]
    
    return result


def test_web3_connection():
    """测试 Web3 连接（Poly 链）"""
    result = {
        'name': 'Polygon RPC',
        'url': 'https://polygon-rpc.com',
        'status': 'unknown',
        'error': None
    }
    
    try:
        # 简单的 eth_blockNumber 调用
        response = requests.post(
            'https://polygon-rpc.com',
            json={
                'jsonrpc': '2.0',
                'method': 'eth_blockNumber',
                'params': [],
                'id': 1
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                block_num = int(data['result'], 16)
                result['status'] = f'✅ success (最新区块：{block_num})'
            else:
                result['status'] = '❌ error'
                result['error'] = data.get('error', {}).get('message', '未知错误')
        else:
            result['status'] = f'❌ HTTP {response.status_code}'
            
    except Exception as e:
        result['status'] = '❌ error'
        result['error'] = str(e)[:200]
    
    return result


def main():
    """主测试函数"""
    print("=" * 70)
    print("🔌 Polymarket API 连接测试")
    print("=" * 70)
    print()
    
    # 加载配置
    api_key = None
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('polymarket', {}).get('api_key')
            if api_key:
                print(f"📋 已加载 API Key: {api_key[:20]}...{api_key[-10:]}")
    except Exception as e:
        print(f"⚠️  无法加载 config.json: {e}")
    
    print()
    print("-" * 70)
    print("🌐 测试 HTTP API 端点")
    print("-" * 70)
    print()
    
    results = []
    for endpoint in API_ENDPOINTS:
        print(f"测试：{endpoint['name']}")
        result = test_endpoint(endpoint, api_key)
        results.append(result)
        
        print(f"  状态：{result['status']}")
        print(f"  URL:  {result['url']}")
        if result['response_time']:
            print(f"  耗时：{result['response_time']}ms")
        if result['error']:
            print(f"  错误：{result['error']}")
        if result['data']:
            # 显示部分数据
            if isinstance(result['data'], dict):
                keys = list(result['data'].keys())[:5]
                print(f"  数据：{keys}")
            elif isinstance(result['data'], list):
                print(f"  数据：{len(result['data'])} 条记录")
        print()
    
    print("-" * 70)
    print("⛓️  测试 Web3 连接")
    print("-" * 70)
    print()
    
    web3_result = test_web3_connection()
    print(f"测试：{web3_result['name']}")
    print(f"  状态：{web3_result['status']}")
    print(f"  URL:  {web3_result['url']}")
    if web3_result.get('error'):
        print(f"  错误：{web3_result['error']}")
    print()
    
    # 总结
    print("=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    
    success_count = sum(1 for r in results if 'success' in r['status'])
    print(f"HTTP API: {success_count}/{len(results)} 成功")
    print(f"Web3: {'✅ 成功' if 'success' in web3_result['status'] else '❌ 失败'}")
    
    if success_count == 0:
        print()
        print("⚠️  所有公开 API 端点均不可用")
        print()
        print("建议方案:")
        print("  1. 使用官方 SDK: https://github.com/Polymarket/polymarket-python-sdk")
        print("  2. 直接使用 Web3 合约交互 (需要私钥)")
        print("  3. 联系 Polymarket 获取机构 API 访问权限")
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    main()
