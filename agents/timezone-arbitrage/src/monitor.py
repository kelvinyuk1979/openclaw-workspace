#!/usr/bin/env python3
"""
信息源监控模块

监控多个时区的信息源：
- RSS Feed（政府、央行公告）
- 直播流（议会、会议）
- API（财经快讯）
"""

import asyncio
import logging
import feedparser
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import re

logger = logging.getLogger('timezone-arbitrage.monitor')


class InformationSourceMonitor:
    """信息源监控器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.sources = config['sources']
        self.session = None
        self.last_check = {}  # 记录每个信息源最后检查时间
        self.signal_cache = []  # 缓存未处理的信号
    
    async def start(self):
        """启动监控会话"""
        self.session = aiohttp.ClientSession()
        logger.info(f"✅ 启动监控 {len(self.sources)} 个信息源")
    
    async def stop(self):
        """停止监控"""
        if self.session:
            await self.session.close()
            logger.info("监控会话已关闭")
    
    async def get_all_signals(self) -> List[dict]:
        """获取所有信息源的最新信号"""
        if not self.session:
            await self.start()
        
        all_signals = []
        
        # 并行检查所有信息源
        tasks = []
        for source_name, source_config in self.sources.items():
            if source_config.get('enabled', True):
                tasks.append(self.check_source(source_name, source_config))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_signals.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"检查信息源失败：{result}")
        
        return all_signals
    
    async def check_source(self, source_name: str, source_config: dict) -> List[dict]:
        """检查单个信息源"""
        source_type = source_config['type']
        signals = []
        
        try:
            if source_type == 'rss':
                signals = await self._check_rss(source_name, source_config)
            elif source_type == 'livestream':
                signals = await self._check_livestream(source_name, source_config)
            elif source_type == 'api':
                signals = await self._check_api(source_name, source_config)
            else:
                logger.warning(f"未知的信息源类型：{source_type}")
            
            # 更新最后检查时间
            self.last_check[source_name] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"检查 {source_name} 失败：{e}", exc_info=True)
        
        return signals
    
    async def _check_rss(self, source_name: str, source_config: dict) -> List[dict]:
        """检查 RSS Feed"""
        url = source_config['url']
        keywords = source_config.get('keywords', [])
        timezone = source_config.get('timezone', 'UTC')
        confidence_weight = source_config.get('confidence_weight', 0.8)
        
        logger.debug(f"检查 RSS: {source_name} ({url})")
        
        # 获取 RSS 内容
        async with self.session.get(url, timeout=10) as response:
            rss_content = await response.text()
        
        # 解析 RSS
        feed = feedparser.parse(rss_content)
        signals = []
        
        # 检查最新条目
        for entry in feed.entries[:5]:  # 只检查最近 5 条
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            published = entry.get('published_parsed')
            
            # 检查是否包含关键词
            text = f"{title} {summary}".lower()
            matched_keywords = [kw for kw in keywords if kw.lower() in text]
            
            if matched_keywords:
                # 提取概率信息（从标题或摘要中）
                true_prob = self._extract_probability(text, title)
                
                if true_prob:
                    signal = {
                        'source_name': source_name,
                        'source_type': 'rss',
                        'market_name': self._extract_market_name(title, matched_keywords),
                        'true_probability': true_prob,
                        'confidence': confidence_weight,
                        'detected_at': datetime.utcnow(),
                        'raw_data': {
                            'title': title,
                            'summary': summary,
                            'published': published,
                            'link': entry.get('link', '')
                        }
                    }
                    signals.append(signal)
                    logger.info(f"📡 RSS 信号：{source_name} - {title[:50]}")
        
        return signals
    
    async def _check_livestream(self, source_name: str, source_config: dict) -> List[dict]:
        """检查直播流（简化版：检查直播页面文本）"""
        url = source_config['url']
        keywords = source_config.get('keywords', [])
        confidence_weight = source_config.get('confidence_weight', 0.8)
        
        logger.debug(f"检查直播：{source_name} ({url})")
        
        # 获取直播页面内容
        async with self.session.get(url, timeout=10) as response:
            page_content = await response.text()
        
        # 提取关键信息（简化：搜索关键词）
        text = page_content.lower()
        matched_keywords = [kw for kw in keywords if kw.lower() in text]
        
        signals = []
        if matched_keywords:
            # 检测投票/决策状态
            status = self._detect_livestream_status(text, matched_keywords)
            
            if status:
                signal = {
                    'source_name': source_name,
                    'source_type': 'livestream',
                    'market_name': self._extract_market_name(source_name, matched_keywords),
                    'true_probability': status['probability'],
                    'confidence': confidence_weight,
                    'detected_at': datetime.utcnow(),
                    'raw_data': {
                        'status': status,
                        'url': url
                    }
                }
                signals.append(signal)
                logger.info(f"📺 直播信号：{source_name} - {status['description']}")
        
        return signals
    
    async def _check_api(self, source_name: str, source_config: dict) -> List[dict]:
        """检查 API 接口"""
        url = source_config['url']
        keywords = source_config.get('keywords', [])
        confidence_weight = source_config.get('confidence_weight', 0.8)
        
        logger.debug(f"检查 API: {source_name} ({url})")
        
        # 调用 API（简化示例）
        try:
            async with self.session.get(url, timeout=10) as response:
                data = await response.json()
            
            signals = []
            # 处理 API 响应（根据实际 API 格式调整）
            for item in data.get('items', [])[:5]:
                text = f"{item.get('title', '')} {item.get('content', '')}".lower()
                matched_keywords = [kw for kw in keywords if kw.lower() in text]
                
                if matched_keywords:
                    true_prob = self._extract_probability(text, item.get('title', ''))
                    
                    if true_prob:
                        signal = {
                            'source_name': source_name,
                            'source_type': 'api',
                            'market_name': self._extract_market_name(item.get('title', ''), matched_keywords),
                            'true_probability': true_prob,
                            'confidence': confidence_weight,
                            'detected_at': datetime.utcnow(),
                            'raw_data': item
                        }
                        signals.append(signal)
            
            return signals
        except Exception as e:
            logger.error(f"API 调用失败 {source_name}: {e}")
            return []
    
    def _extract_probability(self, text: str, title: str) -> Optional[float]:
        """从文本中提取概率信息"""
        # 查找百分比
        percent_matches = re.findall(r'(\d+)%', text)
        if percent_matches:
            return float(percent_matches[0]) / 100.0
        
        # 查找概率描述
        prob_keywords = {
            'confirmed': 0.95,
            'official': 0.90,
            'announced': 0.85,
            'likely': 0.70,
            'probable': 0.65,
            'possible': 0.50
        }
        
        for keyword, prob in prob_keywords.items():
            if keyword in text.lower():
                return prob
        
        # 默认值
        return 0.60
    
    def _extract_market_name(self, title: str, keywords: List[str]) -> str:
        """提取市场名称"""
        # 简化：使用关键词组合作为市场名称
        return f"{keywords[0]} - {title[:30]}"
    
    def _detect_livestream_status(self, text: str, keywords: List[str]) -> Optional[dict]:
        """检测直播状态（投票结果、决策等）"""
        # 检测投票领先
        if 'yes' in text and 'leading' in text:
            # 提取领先比例
            match = re.search(r'yes.*?(\d+)%', text)
            prob = float(match.group(1)) / 100.0 if match else 0.70
            
            return {
                'probability': prob,
                'description': f"YES leading with {prob*100:.0f}%"
            }
        
        # 检测确认
        if 'confirmed' in text or 'approved' in text:
            return {
                'probability': 0.95,
                'description': 'Confirmed/Approved'
            }
        
        return None


class SignalProcessor:
    """信号处理器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.signal_history = []
    
    def process_signal(self, signal: dict) -> dict:
        """处理单个信号，添加额外信息"""
        # 计算结算时间
        settlement_time = self._estimate_settlement_time(signal)
        signal['settlement_time'] = settlement_time
        
        # 计算到结算的时间（分钟）
        minutes_to_settlement = (settlement_time - datetime.utcnow()).total_seconds() / 60
        signal['minutes_to_settlement'] = minutes_to_settlement
        
        # 检查是否在交易窗口内
        signal['in_trading_window'] = self._check_trading_window(settlement_time)
        
        # 添加信号 ID
        signal['signal_id'] = f"{signal['source_name']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return signal
    
    def _estimate_settlement_time(self, signal: dict) -> datetime:
        """估算结算时间"""
        # 基于信息源类型和市场名称估算
        source_type = signal['source_type']
        
        if source_type == 'rss':
            # RSS 公告通常在 1-2 小时内结算
            return datetime.utcnow() + timedelta(hours=1.5)
        elif source_type == 'livestream':
            # 直播中的事件通常在 30-90 分钟内结算
            return datetime.utcnow() + timedelta(minutes=60)
        elif source_type == 'api':
            # API 快讯通常在 1-3 小时内结算
            return datetime.utcnow() + timedelta(hours=2)
        else:
            return datetime.utcnow() + timedelta(hours=2)
    
    def _check_trading_window(self, settlement_time: datetime) -> bool:
        """检查是否在交易窗口内（美东时间凌晨 2-6 点）"""
        from pytz import timezone
        est = timezone('US/Eastern')
        settlement_est = settlement_time.astimezone(est)
        
        start_hour = int(self.config['trading']['trading_hours']['start'].split(':')[0])
        end_hour = int(self.config['trading']['trading_hours']['end'].split(':')[0])
        
        return start_hour <= settlement_est.hour < end_hour
