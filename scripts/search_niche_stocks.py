#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小众股票行业搜索工具
搜索特定行业的隐形冠军和专精特新股票
"""

import json
from datetime import datetime
from pathlib import Path

# 行业股票数据库
INDUSTRY_DATABASE = {
    "半导体": [
        {"code": "688012", "name": "中微公司", "subsector": "刻蚀设备", "market": "A 股", "cap": "~1200 亿", "rank": "全球前三"},
        {"code": "688981", "name": "中芯国际", "subsector": "晶圆代工", "market": "A 股", "cap": "~4000 亿", "rank": "全球第五"},
        {"code": "300782", "name": "卓胜微", "subsector": "射频芯片", "market": "A 股", "cap": "~500 亿", "rank": "国内第一"},
        {"code": "688008", "name": "澜起科技", "subsector": "内存接口", "market": "A 股", "cap": "~600 亿", "rank": "全球领先"},
        {"code": "688256", "name": "寒武纪", "subsector": "AI 芯片", "market": "A 股", "cap": "~800 亿", "rank": "国内领先"},
    ],
    "光伏": [
        {"code": "300763", "name": "锦浪科技", "subsector": "逆变器", "market": "A 股", "cap": "~400 亿", "rank": "全球前三"},
        {"code": "688390", "name": "固德威", "subsector": "逆变器", "market": "A 股", "cap": "~200 亿", "rank": "全球前五"},
        {"code": "300861", "name": "美畅股份", "subsector": "切割丝", "market": "A 股", "cap": "~150 亿", "rank": "全球第一"},
        {"code": "601012", "name": "隆基绿能", "subsector": "硅片/组件", "market": "A 股", "cap": "~1500 亿", "rank": "全球第一"},
        {"code": "01799.HK", "name": "协鑫新能源", "subsector": "硅材料", "market": "港股", "cap": "~150 亿", "rank": "全球第一"},
    ],
    "医药": [
        {"code": "300601", "name": "康泰生物", "subsector": "疫苗", "market": "A 股", "cap": "~300 亿", "rank": "国内前三"},
        {"code": "688016", "name": "心脉医疗", "subsector": "支架", "market": "A 股", "cap": "~120 亿", "rank": "国内第一"},
        {"code": "300723", "name": "一品红", "subsector": "儿童药", "market": "A 股", "cap": "~100 亿", "rank": "国内第一"},
        {"code": "688180", "name": "君实生物", "subsector": "创新药", "market": "A 股", "cap": "~350 亿", "rank": "国内领先"},
        {"code": "02269.HK", "name": "药明生物", "subsector": "CRO", "market": "港股", "cap": "~1500 亿", "rank": "全球第二"},
        {"code": "01801.HK", "name": "信达生物", "subsector": "创新药", "market": "港股", "cap": "~600 亿", "rank": "国内领先"},
        {"code": "833575", "name": "康乐卫士", "subsector": "疫苗", "market": "北交所", "cap": "~80 亿", "rank": "在研 9 价 HPV"},
        {"code": "872925", "name": "锦好医疗", "subsector": "助听器", "market": "北交所", "cap": "~20 亿", "rank": "国产替代"},
    ],
    "新能源": [
        {"code": "835185", "name": "贝特瑞", "subsector": "负极材料", "market": "北交所", "cap": "~300 亿", "rank": "全球第一"},
        {"code": "02208.HK", "name": "金风科技", "subsector": "风电整机", "market": "港股", "cap": "~400 亿", "rank": "全球第二"},
        {"code": "300014", "name": "亿纬锂能", "subsector": "锂电池", "market": "A 股", "cap": "~1000 亿", "rank": "国内前三"},
    ],
    "软件": [
        {"code": "688111", "name": "金山办公", "subsector": "办公软件", "market": "A 股", "cap": "~1500 亿", "rank": "国内第一"},
        {"code": "300496", "name": "中科创达", "subsector": "操作系统", "market": "A 股", "cap": "~300 亿", "rank": "国内领先"},
        {"code": "688588", "name": "凌志软件", "subsector": "金融 IT", "market": "A 股", "cap": "~50 亿", "rank": "细分龙头"},
    ],
    "材料": [
        {"code": "688122", "name": "西部超导", "subsector": "超导材料", "market": "A 股", "cap": "~250 亿", "rank": "国内第一"},
        {"code": "300073", "name": "当升科技", "subsector": "正极材料", "market": "A 股", "cap": "~200 亿", "rank": "全球领先"},
    ],
    "高端制造": [
        {"code": "688001", "name": "华兴源创", "subsector": "检测设备", "market": "A 股", "cap": "~150 亿", "rank": "国内领先"},
        {"code": "830779", "name": "武汉蓝电", "subsector": "电池测试", "market": "北交所", "cap": "~30 亿", "rank": "细分垄断"},
        {"code": "832000", "name": "寰宇科技", "subsector": "连接器", "market": "北交所", "cap": "~25 亿", "rank": "军工配套"},
    ],
}

def search_by_industry(industry_keyword):
    """按行业搜索"""
    results = []
    
    for industry, stocks in INDUSTRY_DATABASE.items():
        if industry_keyword.lower() in industry.lower():
            for stock in stocks:
                stock["industry"] = industry
                results.append(stock)
    
    return results

def search_by_subsector(subsector_keyword):
    """按细分领域搜索"""
    results = []
    
    for industry, stocks in INDUSTRY_DATABASE.items():
        for stock in stocks:
            if subsector_keyword.lower() in stock["subsector"].lower():
                stock["industry"] = industry
                results.append(stock)
    
    return results

def search_by_market(market):
    """按市场搜索"""
    results = []
    
    for industry, stocks in INDUSTRY_DATABASE.items():
        for stock in stocks:
            if market in stock["market"]:
                stock["industry"] = industry
                results.append(stock)
    
    return results

def filter_by_market_cap(min_cap=0, max_cap=float('inf')):
    """按市值过滤"""
    results = []
    
    for industry, stocks in INDUSTRY_DATABASE.items():
        for stock in stocks:
            # 简化处理，实际需要解析市值字符串
            results.append(stock)
    
    return results

def generate_search_report(results, search_type, keyword):
    """生成搜索报告"""
    report = f"""# 🔍 小众股票行业搜索结果

**搜索类型：** {search_type}  
**关键词：** {keyword}  
**结果数量：** {len(results)} 只  
**搜索时间：** {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 📊 搜索结果

| 代码 | 名称 | 细分领域 | 行业 | 市场 | 市值 | 地位 |
|------|------|----------|------|------|------|------|
"""
    
    for stock in results:
        report += f"| {stock['code']} | {stock['name']} | {stock['subsector']} | {stock.get('industry', '-')} | {stock['market']} | {stock['cap']} | {stock['rank']} |\n"
    
    report += f"""
---

## 📈 市场分析

### 行业特点
[待分析]

### 投资逻辑
[待分析]

### 风险提示
[待分析]

---

## 💡 建议关注

### 第一梯队（龙头）
[待筛选]

### 第二梯队（成长）
[待筛选]

### 第三梯队（潜力）
[待筛选]

---

*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*数据来源：小众股票数据库*
*免责声明：仅供参考，不构成投资建议*
"""
    
    return report

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python3 search_niche_stocks.py <搜索类型> <关键词>")
        print("\n搜索类型:")
        print("  industry  - 按行业搜索 (如：半导体、光伏、医药)")
        print("  subsector - 按细分领域搜索 (如：逆变器、疫苗、芯片)")
        print("  market    - 按市场搜索 (如：A 股、港股、北交所)")
        print("\n示例:")
        print("  python3 search_niche_stocks.py industry 半导体")
        print("  python3 search_niche_stocks.py subsector 逆变器")
        print("  python3 search_niche_stocks.py market 北交所")
        return
    
    search_type = sys.argv[1]
    keyword = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🔍 搜索小众股票：{search_type} = {keyword}")
    
    if search_type == "industry":
        results = search_by_industry(keyword)
    elif search_type == "subsector":
        results = search_by_subsector(keyword)
    elif search_type == "market":
        results = search_by_market(keyword)
    else:
        print(f"❌ 未知搜索类型：{search_type}")
        return
    
    if not results:
        print("⚠️  未找到匹配的股票")
        return
    
    print(f"✅ 找到 {len(results)} 只股票")
    
    # 生成报告
    report = generate_search_report(results, search_type, keyword)
    
    # 保存到文件
    output_file = Path(f"/Users/kelvin/.openclaw/workspace/projects/stock-tracking/search_{search_type}_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ 报告已保存：{output_file}")
    
    # 打印简要结果
    print("\n📊 搜索结果概览:")
    print("-" * 80)
    for stock in results[:10]:  # 只显示前 10 只
        print(f"{stock['code']} | {stock['name']:<10} | {stock['subsector']:<10} | {stock['market']:<6} | {stock['cap']:<8} | {stock['rank']}")
    
    if len(results) > 10:
        print(f"... 还有 {len(results) - 10} 只股票，请查看完整报告")

if __name__ == "__main__":
    main()
