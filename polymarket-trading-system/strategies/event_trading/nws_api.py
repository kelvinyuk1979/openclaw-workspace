#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美国国家气象局 (NWS) API
免费获取机场气象站温度预报
https://www.weather.gov/documentation/services-web-api
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# NWS API 端点
NWS_API_BASE = "https://api.weather.gov"

# 主要城市机场气象站坐标
# 使用机场坐标而非市中心，确保与 Polymarket 市场一致
AIRPORT_STATIONS = {
    "new_york": {
        "name": "New York LaGuardia",
        "station": "KLGA",
        "lat": 40.7937,
        "lon": -73.8772,
        "state": "NY"
    },
    "dallas": {
        "name": "Dallas Love Field",
        "station": "KDAL",
        "lat": 32.8471,
        "lon": -96.8519,
        "state": "TX"
    },
    "chicago": {
        "name": "Chicago O'Hare",
        "station": "KORD",
        "lat": 41.9742,
        "lon": -87.9073,
        "state": "IL"
    },
    "los_angeles": {
        "name": "Los Angeles Intl",
        "station": "KLAX",
        "lat": 33.9425,
        "lon": -118.4081,
        "state": "CA"
    },
    "miami": {
        "name": "Miami Intl",
        "station": "KMIA",
        "lat": 25.7959,
        "lon": -80.2870,
        "state": "FL"
    },
    "boston": {
        "name": "Boston Logan",
        "station": "KBOS",
        "lat": 42.3656,
        "lon": -71.0096,
        "state": "MA"
    },
    "denver": {
        "name": "Denver Intl",
        "station": "KDEN",
        "lat": 39.8561,
        "lon": -104.6737,
        "state": "CO"
    },
    "atlanta": {
        "name": "Atlanta Hartsfield",
        "station": "KATL",
        "lat": 33.6407,
        "lon": -84.4277,
        "state": "GA"
    }
}


class NWSWeatherAPI:
    """NWS 天气 API 封装"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Polymarket Weather Bot (your@email.com)',
            'Accept': 'application/geo+json'
        })
    
    def get_forecast(self, lat: float, lon: float) -> Optional[Dict]:
        """
        获取指定地点的天气预报
        
        Args:
            lat: 纬度
            lon: 经度
        
        Returns:
            天气预报数据或 None
        """
        try:
            # 第 1 步：获取预报点
            points_url = f"{NWS_API_BASE}/points/{lat},{lon}"
            response = self.session.get(points_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"获取预报点失败：{response.status_code}")
                return None
            
            points_data = response.json()
            
            # 提取预报 URL
            forecast_url = points_data.get('properties', {}).get('forecast')
            if not forecast_url:
                logger.warning("未找到预报 URL")
                return None
            
            # 第 2 步：获取详细预报
            forecast_response = self.session.get(forecast_url, timeout=10)
            if forecast_response.status_code != 200:
                logger.warning(f"获取预报失败：{forecast_response.status_code}")
                return None
            
            forecast_data = forecast_response.json()
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"NWS API 错误：{e}")
            return None
    
    def get_daily_highs(self, location_key: str, days: int = 7) -> List[Dict]:
        """
        获取指定城市的每日最高温度
        
        Args:
            location_key: 城市标识（如 'new_york'）
            days: 预报天数（最多 7 天）
        
        Returns:
            每日最高温度列表
        """
        if location_key not in AIRPORT_STATIONS:
            logger.error(f"未知城市：{location_key}")
            return []
        
        station = AIRPORT_STATIONS[location_key]
        forecast = self.get_forecast(station['lat'], station['lon'])
        
        if not forecast:
            return []
        
        # 解析预报数据
        periods = forecast.get('properties', {}).get('periods', [])
        
        daily_highs = []
        seen_dates = set()
        
        for period in periods:
            try:
                # 提取日期
                start_time = datetime.fromisoformat(period['startTime'].replace('Z', '+00:00'))
                date_str = start_time.strftime('%Y-%m-%d')
                
                # 跳过已处理的日期
                if date_str in seen_dates:
                    continue
                
                # 只处理白天时段（获取最高温）
                if 'day' in period.get('name', '').lower() or 'afternoon' in period.get('name', '').lower():
                    temp_f = period.get('temperature', 0)
                    temp_unit = period.get('temperatureUnit', 'F')
                    
                    # 转换为华氏度
                    if temp_unit == 'C':
                        temp_f = temp_f * 9/5 + 32
                    
                    daily_highs.append({
                        'date': date_str,
                        'datetime': start_time,
                        'high_temp_f': int(temp_f),
                        'location': station['name'],
                        'state': station['state'],
                        'period_name': period.get('name', ''),
                        'forecast': period.get('detailedForecast', '')[:100]
                    })
                    
                    seen_dates.add(date_str)
                    
                    if len(daily_highs) >= days:
                        break
                        
            except Exception as e:
                logger.debug(f"解析预报时段失败：{e}")
                continue
        
        return daily_highs
    
    def get_all_cities_forecast(self, days: int = 7) -> Dict[str, List[Dict]]:
        """获取所有城市的预报"""
        forecasts = {}
        
        for city_key in AIRPORT_STATIONS.keys():
            logger.info(f"获取 {city_key} 预报...")
            forecasts[city_key] = self.get_daily_highs(city_key, days)
        
        return forecasts


def test_nws_api():
    """测试 NWS API"""
    logger.info("🌤️ 测试 NWS API...")
    
    api = NWSWeatherAPI()
    
    # 测试纽约
    logger.info("\n📍 测试城市：New York (KLGA)")
    forecast = api.get_daily_highs('new_york', days=5)
    
    if forecast:
        logger.info(f"✅ 获取到 {len(forecast)} 天预报\n")
        for day in forecast[:5]:
            logger.info(f"  {day['date']} - 最高温：{day['high_temp_f']}°F")
            logger.info(f"    时段：{day['period_name']}")
    else:
        logger.warning("❌ 获取预报失败")
    
    return len(forecast) > 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_nws_api()
