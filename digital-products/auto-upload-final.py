#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面包多 (mbd.pub) 全自动上传 - 无需交互
"""

import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

PRODUCT_FILE = "/Users/kelvin/.openclaw/workspace/digital-products/ai-prompts/100-ChatGPT-写作提示词.md"

TITLE = "100 个 ChatGPT 写作提示词模板 - 让 AI 帮你写出爆款内容，每天节省 2 小时"
PRICE = "49"
INTRO = """🔥 你是不是也遇到过：
❌ 面对空白文档发呆半小时，写不出第一句话？
❌ 花 3 小时写的内容，阅读量还不如别人 10 分钟写的？
❌ 知道 AI 很强大，但不知道该怎么提问才能得到好结果？

✅ 这套模板已帮助 500+ 用户：
• 从 0 到 1 写出 10w+ 爆款笔记
• 效率提升 300%
• 每天节省 2 小时

📦 包含 100 个精选提示词：
社交媒体 | 商业文案 | 创意写作 | 学习成长 | 工作效率

🎁 限时福利：提示词优化公式 + 迭代技巧 + 组合使用指南

⏰ 早鸟价 ¥49（原价¥199），仅剩 37 个名额
🛡️ 7 天无理由退款
📥 购买后自动发货"""

def run():
    print("=" * 60)
    print("🍞 面包多全自动上传 - 开始")
    print("=" * 60)
    
    with sync_playwright() as p:
        # 启动浏览器
        print("\n🌐 启动浏览器...")
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
        
        # 1. 打开网站
        print("📱 打开 mbd.pub...")
        page.goto("https://mbd.pub", wait_until='domcontentloaded')
        time.sleep(3)
        
        # 2. 检查登录
        print("🔐 检查登录状态...")
        logged_in = False
        try:
            page.wait_for_selector('a[href*="/work"], a[href*="/my"], a[href*="/creator"]', timeout=5000)
            print("✅ 已登录")
            logged_in = True
        except PlaywrightTimeout:
            print("⚠️  未登录")
        
        if not logged_in:
            print("\n" + "=" * 60)
            print("⚠️  请先在浏览器中登录")
            print("   扫码或账号密码登录")
            print("   登录后我会自动继续...")
            print("=" * 60)
            
            # 等待登录（轮询检查）
            for i in range(60):  # 最多等 3 分钟
                time.sleep(5)
                try:
                    page.wait_for_selector('a[href*="/work"], a[href*="/my"]', timeout=2000)
                    print("✅ 检测到登录成功！")
                    logged_in = True
                    break
                except:
                    if i % 12 == 0:  # 每分钟提示一次
                        print(f"   等待登录中... ({(i+1)*5}秒)")
        
        if not logged_in:
            print("❌ 登录超时，退出")
            browser.close()
            return
        
        # 3. 进入创作页面
        print("\n📝 进入创作页面...")
        page.goto("https://mbd.pub/work", wait_until='domcontentloaded')
        time.sleep(2)
        
        # 4. 点击创建
        print("➕ 点击创建作品...")
        try:
            # 找各种可能的创建按钮
            selectors = [
                'button:has-text("创建")',
                'button:has-text("发布")',
                'a:has-text("创建")',
                'a:has-text("发布")',
                'button:has-text("新建")',
                '.create-btn',
                '.publish-btn'
            ]
            
            for selector in selectors:
                try:
                    btn = page.wait_for_selector(selector, timeout=2000)
                    btn.click()
                    print("   ✅ 已点击创建按钮")
                    time.sleep(2)
                    break
                except:
                    continue
        except Exception as e:
            print(f"   ⚠️  未找到创建按钮：{e}")
        
        # 5. 填写标题
        print("\n✏️  填写标题...")
        try:
            inputs = page.query_selector_all('input[type="text"], input[name="title"], input[placeholder*="标题"]')
            if inputs:
                inputs[0].fill(TITLE)
                print(f"   ✅ {TITLE[:30]}...")
            else:
                print(f"   ⚠️  请手动填写标题：{TITLE}")
        except Exception as e:
            print(f"   ⚠️  填写标题失败：{e}")
        
        # 6. 填写价格
        print("\n💰 填写价格...")
        try:
            inputs = page.query_selector_all('input[type="number"], input[name="price"], input[placeholder*="价格"]')
            if inputs:
                inputs[0].fill(PRICE)
                print(f"   ✅ ¥{PRICE}")
            else:
                print(f"   ⚠️  请手动填写价格：{PRICE}")
        except Exception as e:
            print(f"   ⚠️  填写价格失败：{e}")
        
        # 7. 上传文件
        print("\n📎 上传产品文件...")
        if os.path.exists(PRODUCT_FILE):
            try:
                file_inputs = page.query_selector_all('input[type="file"]')
                if file_inputs:
                    file_inputs[0].set_input_files(PRODUCT_FILE)
                    print(f"   ✅ 上传：{os.path.basename(PRODUCT_FILE)}")
                    time.sleep(3)
                else:
                    print(f"   ⚠️  请手动上传：{PRODUCT_FILE}")
            except Exception as e:
                print(f"   ⚠️  上传文件失败：{e}")
        else:
            print(f"   ❌ 文件不存在：{PRODUCT_FILE}")
        
        # 8. 填写介绍
        print("\n📝 填写介绍...")
        try:
            textareas = page.query_selector_all('textarea')
            if textareas:
                textareas[0].click()
                time.sleep(0.5)
                # 尝试清空
                page.keyboard.press('Control+A')
                page.keyboard.press('Delete')
                time.sleep(0.5)
                # 输入内容
                textareas[0].fill(INTRO)
                print("   ✅ 介绍已填写")
            else:
                print("   ⚠️  请手动复制粘贴介绍内容")
        except Exception as e:
            print(f"   ⚠️  填写介绍失败：{e}")
        
        # 9. 等待用户确认
        print("\n" + "=" * 60)
        print("⚠️  请手动检查:")
        print("   1. 标题、价格是否正确")
        print("   2. 文件是否上传成功")
        print("   3. 勾选「自动发货」")
        print("   4. 上传封面图（可选）")
        print("\n   浏览器窗口已打开，请检查后手动点击「发布」")
        print("=" * 60)
        
        # 等待发布（轮询检查 URL 变化或成功提示）
        print("\n⏳ 等待发布完成...")
        original_url = page.url
        for i in range(120):  # 等 10 分钟
            time.sleep(5)
            current_url = page.url
            
            # 检查是否发布成功（URL 变化或出现成功提示）
            if "success" in current_url.lower() or "/work/" in current_url or current_url != original_url:
                print("✅ 检测到发布成功！")
                break
            
            # 检查页面内容
            content = page.content()
            if "发布成功" in content or "审核" in content:
                print("✅ 检测到发布成功提示！")
                break
            
            if i % 12 == 0:
                print(f"   等待中... ({(i+1)*5}秒)")
        
        print("\n" + "=" * 60)
        print("✅ 上传流程完成！")
        print("=" * 60)
        print("\n下一步:")
        print("  1. 在「我的作品」中查看产品状态")
        print("  2. 等待审核通过（5-10 分钟）")
        print("  3. 复制产品链接")
        print("  4. 开始发内容引流")
        print(f"\n产品文件：{PRODUCT_FILE}")
        
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    run()
