#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 市场监控模块
使用 Jina AI Reader 免费抓取实时数据
https://r.jina.ai
"""

import requests
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

JINA_READER_BASE = "https://r.jina.ai/http://"
POLYMARKET_BASE = "https://polymarket.com"


class PolymarketMonitor:
    """Polymarket 市场监控器 - Jina AI 版本"""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self._cache = []
        self._cache_time = None
    
    def get_markets(self, limit: int = 50, category: str = "trending") -> List[Dict]:
        """获取市场列表"""
        try:
            # 使用缓存（5 分钟内）
            now = datetime.now()
            if self._cache and self._cache_time and (now - self._cache_time).seconds < 300:
                return self._cache[:limit]
            
            url = POLYMARKET_BASE
            jina_url = f"{JINA_READER_BASE}{url}"
            logger.info(f"📡 使用 Jina AI 抓取：{url}")
            
            response = self.session.get(jina_url, timeout=20)
            response.raise_for_status()
            
            markets = self._parse_content(response.text, limit)
            self._cache = markets
            self._cache_time = now
            
            logger.info(f"✅ 获取到 {len(markets)} 个市场")
            return markets
            
        except Exception as e:
            logger.error(f"❌ 抓取失败：{e}")
            return self._cache[:limit] if self._cache else []
    
    def _parse_content(self, content: str, limit: int) -> List[Dict]:
        """解析内容"""
        markets = []
        lines = content.split('\n')
        i = 0
        
        while i < len(lines) and len(markets) < limit:
            line = lines[i].strip()
            
            # 严格的市场标题检测：[标题](/event/xxx) 单独一行
            if (line.startswith('[') and '](' in line and '/event/' in line and 
                'Image' not in line and line.count('[') == 1 and line.count('](') == 1):
                
                title = line.split('](')[0].replace('[', '').strip()
                
                if len(title) < 5:
                    i += 1
                    continue
                
                # 扫描后续行
                outcomes = []
                volume = 0
                
                for j in range(i+1, min(i+30, len(lines))):
                    next_line = lines[j].strip()
                    
                    # Outcomes: [名字 XX%](链接)
                    if next_line.count('[') >= 1 and '](' in next_line and '%' in next_line and 'Image' not in next_line:
                        matches = re.findall(r'\[([^\]]+\s+\d+%)\]', next_line)
                        for m in matches:
                            pct_match = re.search(r'(\d+)%', m)
                            if pct_match:
                                name = m.replace(f' {pct_match.group(1)}%', '').strip()
                                pct = int(pct_match.group(1))
                                if name and len(name) < 40:
                                    outcomes.append({'name': name, 'price': pct/100.0})
                    
                    # 交易量
                    if '$' in next_line and 'Vol' in next_line:
                        vol_match = re.search(r'\$(\d+(?:\.\d+)?)([MKB]?)\s*Vol', next_line)
                        if vol_match:
                            vol = float(vol_match.group(1))
                            unit = vol_match.group(2).upper()
                            if unit == 'M': vol *= 1_000_000
                            elif unit == 'K': vol *= 1_000
                            elif unit == 'B': vol *= 1_000_000_000
                            volume = vol
                    
                    # 遇到下一个市场就停止
                    if (next_line.startswith('[') and '/event/' in next_line and 
                        next_line.count('[') == 1):
                        break
                
                if volume > 0:
                    yes = outcomes[0]['price'] if outcomes else 0.5
                    no = outcomes[1]['price'] if len(outcomes) > 1 else (1.0 - yes)
                    
                    markets.append({
                        'id': hash(title) % 1000000,
                        'title': title,
                        'yesBid': yes,
                        'noBid': no,
                        'volume': volume,
                        'liquidity': volume * 0.05,
                        'active': True,
                        'outcomes': [o['name'] for o in outcomes],
                        'category': ''
                    })
            
            i += 1
        
        markets.sort(key=lambda x: x['volume'], reverse=True)
        return markets
    
    def scan_opportunities(self, markets: List[Dict], config: Dict) -> List[Dict]:
        """扫描交易机会"""
        opportunities = []
        for m in markets:
            if m['volume'] < 10000:
                continue
            
            # 极端价格
            if m['yesBid'] < 0.15 or m['yesBid'] > 0.85:
                opportunities.append({
                    'type': 'extreme',
                    'market_id': m['id'],
                    'title': m['title'],
                    'yes_price': m['yesBid'],
                    'reason': f"极端价格 {m['yesBid']:.1%}"
                })
            
            # 接近 50/50
            if 0.45 < m['yesBid'] < 0.55:
                opportunities.append({
                    'type': 'coinflip',
                    'market_id': m['id'],
                    'title': m['title'],
                    'yes_price': m['yesBid'],
                    'reason': "势均力敌"
                })
        
        return opportunities


def test_connection():
    logger.info("🔌 测试 Jina AI...")
    monitor = PolymarketMonitor()
    markets = monitor.get_markets(limit=10)
    
    if markets:
        logger.info("✅ 成功！")
        logger.info("")
        logger.info("📊 热门市场 TOP 10:")
        logger.info("")
        for i, m in enumerate(markets[:10], 1):
            logger.info(f"{i}. {m['title']}")
            logger.info(f"   YES: {m['yesBid']:.1%} | NO: {m['noBid']:.1%}")
            logger.info(f"   交易量：${m['volume']:,.0f}")
            if m.get('outcomes'):
                logger.info(f"   选项：{', '.join(m['outcomes'][:3])}")
            logger.info("")
        return True
    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_connection()
