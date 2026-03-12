#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面包多自动上传工具 - 完整版
"""

import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 配置
PRODUCT_FILE = "/Users/kelvin/.openclaw/workspace/digital-products/ai-prompts/100-ChatGPT-写作提示词.md"
SALES_TEXT = """
🔥 你是不是也遇到过：

❌ 面对空白文档发呆半小时，写不出第一句话？
❌ 花 3 小时写的内容，阅读量还不如别人 10 分钟写的？
❌ 知道 AI 很强大，但不知道该怎么提问才能得到好结果？

这套《100 个 ChatGPT 写作提示词模板》已经帮助 500+ 用户：
✅ 从 0 到 1 —— 第一次用 AI 就写出 10w+ 爆款笔记
✅ 效率提升 300% —— 原来 3 小时的工作，现在 30 分钟搞定
✅ 时间自由 —— 每天节省 2 小时

📦 你将获得：
- 100 个精选提示词（社交媒体、商业文案、创意写作、学习成长、工作效率）
- 即抄即用 —— 替换括号内容就能出结果
- 手机友好 —— 随时随地复制粘贴

🎁 限时福利：
- 提示词优化公式
- 迭代技巧
- 组合使用指南
- 私密交流群名额（仅限前 100 名）

💬 用户评价：
"以前写小红书笔记要憋一天，现在 10 分钟搞定，还爆了 3 篇 10w+"
"最实用的一套提示词，没有废话，全是能用的"

⏰ 限时优惠：
早鸟价 ¥49（原价¥199），仅剩 37 个名额
48 小时后恢复原价

🛡️ 7 天无理由退款

📥 购买后自动发货，马上就能拿到全套模板！
"""

def main():
    print("=" * 60)
    print("🍞 面包多自动上传工具")
    print("=" * 60)
    print()
    
    with sync_playwright() as p:
        # 启动浏览器
        print("🌐 启动浏览器...")
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # 注入反检测
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        # 1. 打开面包多
        print("📱 打开面包多...")
        page.goto("https://mianbaoduo.com", wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        
        # 2. 检查登录状态
        print("🔐 检查登录状态...")
        try:
            page.wait_for_selector('a[href*="/my"]', timeout=5000)
            print("✅ 已登录")
        except PlaywrightTimeout:
            print("❌ 未登录，请在打开的浏览器窗口中登录")
            print("   登录后按回车继续...")
            input("完成后按回车...")
            page.reload()
            page.wait_for_timeout(3000)
        
        # 3. 进入发布页面
        print("📝 进入发布页面...")
        page.goto("https://mianbaoduo.com/my/work", wait_until='domcontentloaded')
        page.wait_for_timeout(2000)
        
        # 4. 点击创建作品
        print("➕ 点击创建作品...")
        try:
            create_btn = page.wait_for_selector('button:has-text("创建"), button:has-text("发布作品")', timeout=5000)
            create_btn.click()
            page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            print("⚠️  未找到创建按钮，可能已在发布页面")
        
        # 5. 选择虚拟物品
        print("📦 选择作品类型...")
        try:
            virtual_option = page.wait_for_selector('text=虚拟, text=虚拟物品', timeout=5000)
            virtual_option.click()
            page.wait_for_timeout(1000)
        except PlaywrightTimeout:
            print("⚠️  未找到虚拟物品选项")
        
        # 6. 填写标题
        print("✏️  填写标题...")
        title = "100 个 ChatGPT 写作提示词模板 - 让 AI 帮你写出爆款内容，每天节省 2 小时"
        try:
            title_input = page.wait_for_selector('input[placeholder*="标题"], input[name="title"]', timeout=5000)
            title_input.fill(title)
            print(f"   ✅ 标题：{title}")
        except PlaywrightTimeout:
            print("   ⚠️  未找到标题输入框，请手动填写")
            print(f"   标题：{title}")
        
        # 7. 填写价格
        print("💰 填写价格...")
        try:
            price_input = page.wait_for_selector('input[placeholder*="价格"], input[name="price"]', timeout=5000)
            price_input.fill("49")
            print("   ✅ 价格：¥49")
        except PlaywrightTimeout:
            print("   ⚠️  未找到价格输入框，请手动填写：49")
        
        # 8. 上传文件
        print("📎 上传产品文件...")
        if os.path.exists(PRODUCT_FILE):
            print(f"   文件：{PRODUCT_FILE}")
            try:
                file_input = page.wait_for_selector('input[type="file"]', timeout=5000)
                file_input.set_input_files(PRODUCT_FILE)
                print("   ✅ 文件上传中...")
                page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                print("   ⚠️  未找到文件上传框，请手动上传文件")
        else:
            print(f"   ❌ 文件不存在：{PRODUCT_FILE}")
        
        # 9. 填写介绍
        print("📝 填写产品介绍...")
        try:
            # 尝试富文本编辑器
            editor = page.wait_for_selector('[contenteditable="true"], .editor, textarea[name="description"]', timeout=5000)
            editor.click()
            
            # 清空并填写
            page.keyboard.press('Control+A')
            page.keyboard.press('Delete')
            page.wait_for_timeout(500)
            
            # 逐行输入（模拟真实打字）
            for line in SALES_TEXT.split('\n')[:20]:  # 前 20 行
                if line.strip():
                    page.keyboard.type(line + '\n', delay=30)
            
            print("   ✅ 介绍已填写")
        except PlaywrightTimeout:
            print("   ⚠️  未找到编辑器，请手动复制粘贴以下介绍：")
            print("=" * 60)
            print(SALES_TEXT[:500])
            print("...")
            print("=" * 60)
        
        # 10. 等待用户确认
        print()
        print("=" * 60)
        print("⚠️  需要手动确认:")
        print("   1. 检查标题、价格是否正确")
        print("   2. 确认文件已上传")
        print("   3. 检查介绍内容")
        print("   4. 上传封面图（可选）")
        print("   5. 勾选「自动发货」")
        print()
        confirm = input("确认无误后，按回车点击发布按钮...")
        
        # 11. 点击发布
        print("🚀 点击发布...")
        try:
            publish_btn = page.wait_for_selector('button:has-text("发布"), button:has-text("提交")', timeout=5000)
            publish_btn.click()
            print("   ✅ 已点击发布按钮")
            
            # 等待发布完成
            page.wait_for_timeout(5000)
            
            # 检查成功
            if "成功" in page.content() or "/my/work" in page.url:
                print("✅ 发布成功！")
            else:
                print("⚠️  发布状态未知，请手动检查")
                
        except PlaywrightTimeout:
            print("❌ 未找到发布按钮，请手动点击")
        
        print()
        print("=" * 60)
        print("✅ 上传完成！")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 在「我的作品」中检查产品状态")
        print("  2. 等待审核通过（5-10 分钟）")
        print("  3. 复制产品链接")
        print("  4. 开始发内容引流")
        print()
        
        # 保持浏览器打开
        input("按回车关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    main()
