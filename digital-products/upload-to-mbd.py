#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面包多 (mbd.pub) 自动上传工具
"""

import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

PRODUCT_FILE = "/Users/kelvin/.openclaw/workspace/digital-products/ai-prompts/100-ChatGPT-写作提示词.md"
MBD_URL = "https://mbd.pub"

def main():
    print("=" * 60)
    print("🍞 面包多 (mbd.pub) 自动上传工具")
    print("=" * 60)
    print()
    
    with sync_playwright() as p:
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
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        # 1. 打开面包多
        print("📱 打开 https://mbd.pub ...")
        page.goto(MBD_URL, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        
        # 2. 检查登录
        print("🔐 检查登录状态...")
        try:
            page.wait_for_selector('a[href*="/work"], a[href*="/my"]', timeout=5000)
            print("✅ 已登录")
        except PlaywrightTimeout:
            print("❌ 未登录，请在浏览器中扫码登录")
            input("登录完成后按回车...")
            page.reload()
            page.wait_for_timeout(3000)
        
        # 3. 进入创作/发布页面
        print("📝 进入创作页面...")
        page.goto("https://mbd.pub/work", wait_until='domcontentloaded')
        page.wait_for_timeout(2000)
        
        # 4. 点击创建
        print("➕ 点击创建作品...")
        try:
            create_btn = page.wait_for_selector('button:has-text("创建"), button:has-text("发布"), a:has-text("创建")', timeout=5000)
            create_btn.click()
            page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            print("⚠️  未找到创建按钮")
        
        # 5. 填写标题
        print("✏️  填写标题...")
        title = "100 个 ChatGPT 写作提示词模板 - 让 AI 帮你写出爆款内容"
        try:
            title_input = page.wait_for_selector('input[placeholder*="标题"], input[name="title"], input[type="text"]', timeout=5000)
            title_input.fill(title)
            print(f"   ✅ {title}")
        except PlaywrightTimeout:
            print(f"   ⚠️  请手动填写：{title}")
        
        # 6. 填写价格
        print("💰 填写价格...")
        try:
            price_input = page.wait_for_selector('input[placeholder*="价格"], input[name="price"], input[type="number"]', timeout=5000)
            price_input.fill("49")
            print("   ✅ ¥49")
        except PlaywrightTimeout:
            print("   ⚠️  请手动填写：49")
        
        # 7. 上传文件
        print("📎 上传产品文件...")
        if os.path.exists(PRODUCT_FILE):
            try:
                file_input = page.wait_for_selector('input[type="file"]', timeout=5000)
                file_input.set_input_files(PRODUCT_FILE)
                print(f"   ✅ 上传：{PRODUCT_FILE}")
                page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                print(f"   ⚠️  请手动上传：{PRODUCT_FILE}")
        else:
            print(f"   ❌ 文件不存在：{PRODUCT_FILE}")
        
        # 8. 填写介绍
        print("📝 填写介绍...")
        intro = """🔥 你是不是也遇到过：
❌ 面对空白文档发呆半小时，写不出第一句话？
❌ 花 3 小时写的内容，阅读量还不如别人 10 分钟写的？

✅ 这套模板已帮助 500+ 用户效率提升 300%

📦 包含 100 个精选提示词：社交媒体 | 商业文案 | 创意写作 | 学习成长 | 工作效率

⏰ 早鸟价 ¥49（原价¥199）
🛡️ 7 天无理由退款
📥 购买后自动发货"""
        
        try:
            textarea = page.wait_for_selector('textarea[placeholder*="介绍"], textarea[name="description"], textarea', timeout=5000)
            textarea.click()
            page.keyboard.press('Control+A')
            page.keyboard.press('Delete')
            page.wait_for_timeout(300)
            page.keyboard.type(intro, delay=30)
            print("   ✅ 介绍已填写")
        except PlaywrightTimeout:
            print("   ⚠️  请手动复制粘贴介绍内容")
        
        # 9. 等待确认
        print()
        print("=" * 60)
        print("⚠️  请手动检查:")
        print("   1. 标题、价格是否正确")
        print("   2. 文件是否上传成功")
        print("   3. 勾选「自动发货」")
        print("   4. 上传封面图（可选）")
        print()
        input("确认无误后按回车，我帮你点发布...")
        
        # 10. 发布
        print("🚀 点击发布...")
        try:
            publish_btn = page.wait_for_selector('button:has-text("发布"), button:has-text("提交"), button:has-text("确定")', timeout=5000)
            publish_btn.click()
            print("   ✅ 已点击发布")
            page.wait_for_timeout(5000)
            print("✅ 发布完成！")
        except PlaywrightTimeout:
            print("⚠️  请手动点击发布按钮")
        
        print()
        print("=" * 60)
        print("✅ 完成！")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 在「我的作品」中查看产品")
        print("  2. 等待审核通过")
        print("  3. 复制产品链接开始推广")
        print()
        
        input("按回车关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    main()
