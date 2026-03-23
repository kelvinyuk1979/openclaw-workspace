#!/usr/bin/env python3
import re

with open('/tmp/poly_test.txt', 'r') as f:
    content = f.read()

lines = content.split('\n')

markets = []
i = 0

while i < len(lines):
    line = lines[i].strip()
    
    # 市场标题：[标题](/event/xxx) 单独一行，不含 Image
    if (line.startswith('[') and '](' in line and '/event/' in line and 
        'Image' not in line and line.count('[') == 1 and line.count('](') == 1):
        
        title = line.split('](')[0].replace('[', '').strip()
        
        # 跳过空标题
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
                    volume = vol
            
            # 遇到下一个市场就停止
            if (next_line.startswith('[') and '/event/' in next_line and 
                next_line.count('[') == 1):
                break
        
        if volume > 0:
            yes = outcomes[0]['price'] if outcomes else 0.5
            no = outcomes[1]['price'] if len(outcomes) > 1 else 1.0 - yes
            
            markets.append({
                'title': title,
                'yes': yes,
                'no': no,
                'volume': volume,
                'outcomes': [o['name'] for o in outcomes]
            })
    
    i += 1

# 排序
markets.sort(key=lambda x: x['volume'], reverse=True)

print(f"✅ 解析到 {len(markets)} 个市场\n")

for idx, m in enumerate(markets[:10], 1):
    print(f"{idx}. {m['title']}")
    print(f"   YES: {m['yes']:.1%} ({m['outcomes'][0] if m['outcomes'] else 'N/A'})")
    print(f"   NO:  {m['no']:.1%} ({m['outcomes'][1] if len(m['outcomes'])>1 else 'N/A'})")
    print(f"   Vol: ${m['volume']:,.0f}")
    print()
