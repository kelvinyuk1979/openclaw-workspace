import re

with open('bot_v1.py', 'r') as f:
    content = f.read()

# 1. 注入 Session 和 Retry
import_block = """import re
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timezone, timedelta"""

# 创建 session 的代码块
session_init = """
# 创建全局会话并配置重试机制 (最大重试3次，针对 50x 错误自动退避)
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

# ==================== 配置部分 ====================
"""

content = content.replace("import re\nimport json\nimport requests\nfrom datetime", import_block)
content = content.replace("# ==================== 配置部分 ====================", session_init)

# 2. 将 requests.get 替换为 session.get
content = content.replace("requests.get(", "session.get(")

with open('bot_v1.py', 'w') as f:
    f.write(content)
print("Polymarket Bot Optimized!")
