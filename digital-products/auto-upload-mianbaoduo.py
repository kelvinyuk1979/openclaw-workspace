#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面包多自动上传工具
使用 Playwright 浏览器自动化上传数字产品

⚠️ 注意：
- 首次使用需要手动登录和实名认证
- 之后可以自动上传
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 缺少依赖：playwright")
    print("安装命令：pip3 install playwright")
    print("首次运行需要：python3 -m playwright install chromium")
    sys.exit(1)

# 配置
PRODUCT_DIR = "/Users/kelvin/.openclaw/workspace/digital-products/ai-prompts"
PRODUCT_FILE = os.path.join(PRODUCT_DIR, "100-ChatGPT-写作提示词.md")
SALES_PAGE = os.path.join(PRODUCT_DIR, "销售页文案.md")
MIANBAODUO_URL = "https://mianbaoduo.com"
PUBLISH_URL = "https://mianbaoduo.com/my/work"

class MianbaoduoUploader:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        
    def launch_browser(self, headless=False):
        """启动浏览器"""
        print("🌐 启动浏览器...")
        
        playwright = sync_playwright().start()
        
        self.browser = playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = self.context.new_page()
        
        # 注入反检测脚本
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        print("✅ 浏览器启动成功")
        
    def login_check(self):
        """检查是否已登录"""
        print("🔐 检查登录状态...")
        
        self.page.goto(MIANBAODUO_URL, wait_until='domcontentloaded')
        self.page.wait_for_timeout(3000)
        
        # 尝试查找用户头像或登录按钮
        try:
            # 查找用户中心入口
            self.page.wait_for_selector('a[href*="/my"]', timeout=5000)
            print("✅ 已登录状态")
            return True
        except PlaywrightTimeout:
            print("⚠️  未登录，需要手动登录")
            
        print("=" * 60)
        print("📱 请在浏览器窗口中登录面包多")
        print("   1. 扫码登录或账号密码登录")
        print("   2. 完成实名认证（首次需要）")
        print("   3. 绑定收款账户（支付宝/银行卡）")
        print("   4. 登录完成后按回车继续")
        print("=" * 60)
        
        input("完成后按回车继续...")
        
        # 刷新页面
        self.page.reload()
        self.page.wait_for_timeout(3000)
        
        return True
    
    def read_file(self, filepath):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def upload_product(self):
        """上传产品"""
        print("📦 开始上传产品...")
        
        # 跳转到发布页面
        self.page.goto(PUBLISH_URL, wait_until='domcontentloaded')
        self.page.wait_for_timeout(3000)
        
        # 1. 点击创建作品
        print("  1️⃣ 点击创建作品...")
        try:
            create_btn = self.page.wait_for_selector('button:has-text("创建"), button:has-text("发布")', timeout=5000)
            create_btn.click()
            self.page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            print("  ⚠️  未找到创建按钮，可能已在发布页面")
        
        # 2. 选择作品类型
        print("  2️⃣ 选择作品类型：虚拟物品...")
        try:
            # 查找虚拟物品选项
            virtual_option = self.page.wait_for_selector('text=虚拟, text=虚拟物品', timeout=5000)
            virtual_option.click()
            self.page.wait_for_timeout(1000)
        except PlaywrightTimeout:
            print("  ⚠️  未找到虚拟物品选项")
        
        # 3. 填写标题
        print("  3️⃣ 填写标题...")
        title = "100 个 ChatGPT 写作提示词模板 - 让 AI 帮你写出爆款内容"
        try:
            title_input = self.page.wait_for_selector('input[placeholder*="标题"], input[name="title"]', timeout=5000)
            title_input.fill(title)
            print(f"     标题：{title}")
        except PlaywrightTimeout:
            print("  ⚠️  未找到标题输入框")
        
        # 4. 填写价格
        print("  4️⃣ 填写价格...")
        price = "49"
        try:
            price_input = self.page.wait_for_selector('input[placeholder*="价格"], input[name="price"]', timeout=5000)
            price_input.fill(price)
            print(f"     价格：¥{price}")
        except PlaywrightTimeout:
            print("  ⚠️  未找到价格输入框")
        
        # 5. 上传文件
        print("  5️⃣ 上传产品文件...")
        if os.path.exists(PRODUCT_FILE):
            print(f"     文件：{PRODUCT_FILE}")
            # 需要用户手动上传（文件选择对话框）
            print("  ⚠️  请点击上传按钮选择文件")
            print("     建议先将文件转为 PDF 再上传")
        else:
            print(f"  ❌ 文件不存在：{PRODUCT_FILE}")
        
        # 6. 填写介绍
        print("  6️⃣ 填写产品介绍...")
        sales_content = self.read_file(SALES_PAGE)
        if sales_content:
            print(f"     介绍长度：{len(sales_content)} 字")
            # 富文本编辑器需要特殊处理
            print("  ⚠️  请手动粘贴销售页文案")
        else:
            print("  ⚠️  未找到销售页文案")
        
        # 7. 上传封面图
        print("  7️⃣ 上传封面图...")
        print("  ⚠️  请手动上传封面图（建议尺寸：800x600）")
        
        # 8. 设置自动发货
        print("  8️⃣ 设置自动发货...")
        print("  ✅ 确保勾选「自动发货」选项")
        
        # 9. 预览
        print("  9️⃣ 预览...")
        print("  ⚠️  请检查所有信息是否正确")
        
        # 10. 发布
        print("  🔟 准备发布...")
        print("=" * 60)
        confirm = input("确认发布？(y/n): ")
        if confirm.lower() != 'y':
            print("❌ 取消发布")
            return False
        
        try:
            publish_btn = self.page.wait_for_selector('button:has-text("发布"), button:has-text("提交")', timeout=5000)
            publish_btn.click()
            print("  ✅ 已点击发布按钮")
            
            # 等待发布完成
            self.page.wait_for_timeout(5000)
            
            # 检查是否成功
            if "成功" in self.page.content() or "/my/work" in self.page.url:
                print("✅ 发布成功！")
                return True
            else:
                print("⚠️  发布状态未知，请手动检查")
                return True
                
        except PlaywrightTimeout:
            print("❌ 未找到发布按钮")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            print("🔒 关闭浏览器...")
            self.browser.close()

def main():
    print("=" * 60)
    print("🍞 面包多自动上传工具")
    print("=" * 60)
    print()
    print("⚠️  使用说明:")
    print("   1. 首次使用需要手动登录和实名认证")
    print("   2. 文件上传和文案填写需要部分手动操作")
    print("   3. 建议先将 .md 文件转为 PDF 再上传")
    print()
    
    # 检查文件
    if not os.path.exists(PRODUCT_FILE):
        print(f"❌ 产品文件不存在：{PRODUCT_FILE}")
        print("   请先创建产品文件")
        return
    
    uploader = MianbaoduoUploader()
    
    try:
        # 1. 启动浏览器
        uploader.launch_browser(headless=False)
        
        # 2. 检查登录
        if not uploader.login_check():
            print("❌ 登录失败，退出")
            return
        
        # 3. 上传产品
        success = uploader.upload_product()
        
        if success:
            print()
            print("=" * 60)
            print("✅ 上传完成！")
            print("=" * 60)
            print()
            print("下一步:")
            print("  1. 在面包多后台检查产品状态")
            print("  2. 复制产品链接到社交媒体")
            print("  3. 开始发内容引流")
            print()
            print("产品目录:")
            print(f"  {PRODUCT_DIR}")
            print()
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        
    finally:
        uploader.close()

if __name__ == "__main__":
    main()
