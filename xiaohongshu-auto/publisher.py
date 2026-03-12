#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书全自动发布器 (Playwright 浏览器自动化)

⚠️ 风险提示:
- 可能触发平台风控
- 可能需要人工处理验证码
- 建议先用小号测试
- 本脚本仅供学习研究
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 检查依赖
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("❌ 缺少依赖：playwright")
    print("安装命令：pip install playwright")
    print("首次运行需要：playwright install")
    sys.exit(1)

# 配置
CONFIG_FILE = "config.json"
OUTPUT_DIR = "posts"
LOGIN_URL = "https://www.xiaohongshu.com/"
PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"

class XiaohongshuPublisher:
    def __init__(self, config):
        self.config = config
        self.browser = None
        self.page = None
        self.context = None
        
    def launch_browser(self, headless=False):
        """启动浏览器"""
        print("🌐 启动浏览器...")
        
        playwright = sync_playwright().start()
        
        # 使用 Chromium
        self.browser = playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # 创建上下文 (模拟真实用户)
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = self.context.new_page()
        
        # 注入反检测脚本
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh']});
        """)
        
        print("✅ 浏览器启动成功")
        
    def login(self):
        """登录小红书"""
        print("🔐 开始登录...")
        
        self.page.goto(LOGIN_URL, wait_until='domcontentloaded')
        
        # 等待页面加载
        self.page.wait_for_timeout(5000)
        
        # 检查是否已登录
        try:
            # 尝试查找发布按钮，如果存在说明已登录
            self.page.wait_for_selector('button[data-type="publish"]', timeout=10000)
            print("✅ 已登录状态")
            return True
        except PlaywrightTimeout:
            print("⚠️ 未登录，需要扫码登录")
            
        # 显示登录二维码
        print("=" * 60)
        print("📱 请使用小红书 APP 扫码登录")
        print("   二维码已在浏览器窗口中显示")
        print("   扫码后按回车继续...")
        print("=" * 60)
        
        # 等待用户扫码
        input("扫码完成后按回车继续...")
        
        # 等待登录完成
        self.page.wait_for_timeout(3000)
        
        # 验证登录
        try:
            self.page.wait_for_selector('button[data-type="publish"]', timeout=10000)
            print("✅ 登录成功")
            
            # 保存登录状态 (可选)
            # self.context.storage_state(path="xiaohongshu_storage.json")
            
            return True
        except PlaywrightTimeout:
            print("❌ 登录失败，请重试")
            return False
    
    def get_latest_post(self):
        """获取最新笔记内容"""
        if not os.path.exists(OUTPUT_DIR):
            return None
        
        files = sorted(os.listdir(OUTPUT_DIR), reverse=True)
        if not files:
            return None
        
        filepath = os.path.join(OUTPUT_DIR, files[0])
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析内容
        lines = content.split('\n')
        title = lines[0].lstrip('# ').strip() if lines else "未命名"
        
        # 提取正文 (标题和标签之间)
        body_start = 1
        body_end = len(lines)
        for i, line in enumerate(lines):
            if line.startswith('---') and i > 2:
                body_end = i
                break
        
        body = '\n'.join(lines[body_start:body_end]).strip()
        
        # 提取标签
        tags = []
        for line in lines[body_end:]:
            if line.startswith('#'):
                tags.extend(line.split())
        
        return {
            'filepath': filepath,
            'title': title,
            'body': body,
            'tags': tags
        }
    
    def publish(self, post):
        """发布笔记"""
        print(f"📝 准备发布：{post['title']}")
        
        # 跳转到发布页面
        self.page.goto(PUBLISH_URL, wait_until='domcontentloaded')
        self.page.wait_for_timeout(3000)
        
        # 1. 填写标题
        print("  1️⃣ 填写标题...")
        try:
            title_input = self.page.wait_for_selector('input[placeholder*="标题"]', timeout=5000)
            title_input.fill(post['title'])
        except PlaywrightTimeout:
            print("  ⚠️ 未找到标题输入框，尝试其他方式...")
        
        # 2. 填写正文
        print("  2️⃣ 填写正文...")
        try:
            # 查找编辑器 (小红书使用富文本编辑器)
            editor = self.page.wait_for_selector('[contenteditable="true"]', timeout=5000)
            editor.click()
            
            # 逐行输入 (模拟真实打字)
            for line in post['body'].split('\n'):
                if line.strip():
                    editor.type(line + '\n', delay=50)
        except PlaywrightTimeout:
            print("  ⚠️ 未找到编辑器")
        
        # 3. 添加标签
        print("  3️⃣ 添加标签...")
        try:
            tag_input = self.page.wait_for_selector('input[placeholder*="标签"]', timeout=5000)
            for tag in post['tags'][:5]:  # 最多 5 个标签
                tag_input.fill(tag)
                self.page.wait_for_timeout(500)
                # 按回车确认标签
                self.page.keyboard.press('Enter')
                self.page.wait_for_timeout(500)
        except PlaywrightTimeout:
            print("  ⚠️ 未找到标签输入框")
        
        # 4. 上传图片 (如果有)
        # TODO: 需要配置图片路径
        print("  4️⃣ 图片上传：跳过 (未配置)")
        
        # 5. 等待片刻后发布
        print("  5️⃣ 准备发布...")
        self.page.wait_for_timeout(2000)
        
        # 查找发布按钮
        try:
            publish_button = self.page.wait_for_selector(
                'button:has-text("发布"), button:has-text("发表")',
                timeout=5000
            )
            
            # 模拟真实点击
            publish_button.click()
            print("  ✅ 已点击发布按钮")
            
            # 等待发布完成
            self.page.wait_for_timeout(5000)
            
            # 检查是否发布成功
            if "发布成功" in self.page.content() or "publish" not in self.page.url.lower():
                print("✅ 发布成功！")
                return True
            else:
                print("⚠️ 发布状态未知，请手动检查")
                return True
                
        except PlaywrightTimeout:
            print("❌ 未找到发布按钮")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            print("🔒 关闭浏览器...")
            self.browser.close()

def load_config():
    """加载配置"""
    config_path = Path(__file__).parent / CONFIG_FILE
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"publish": {"method": "auto"}}

def main():
    print("=" * 60)
    print("📱 小红书全自动发布器")
    print("=" * 60)
    print()
    print("⚠️  风险提示:")
    print("   - 可能触发平台风控")
    print("   - 可能需要人工处理验证码")
    print("   - 建议先用小号测试")
    print()
    
    config = load_config()
    publisher = XiaohongshuPublisher(config)
    
    try:
        # 1. 启动浏览器 (headless=False 可以看到操作过程)
        publisher.launch_browser(headless=False)
        
        # 2. 登录
        if not publisher.login():
            print("❌ 登录失败，退出")
            return
        
        # 3. 获取最新笔记
        post = publisher.get_latest_post()
        if not post:
            print("❌ 没有找到笔记，请先生成内容")
            print("   运行：python3 content_generator.py")
            return
        
        print()
        print(f"📄 笔记信息:")
        print(f"   标题：{post['title']}")
        print(f"   标签：{len(post['tags'])} 个")
        print(f"   文件：{post['filepath']}")
        print()
        
        # 4. 发布前确认
        print()
        print("=" * 60)
        print("📋 发布前确认")
        print("=" * 60)
        print(f"标题：{post['title']}")
        print(f"正文：{len(post['body'])} 字")
        print(f"标签：{' '.join(post['tags'][:5])}")
        print()
        
        confirm = input("确认发布到小红书？(y/n): ")
        if confirm.lower() != 'y':
            print("❌ 取消发布")
            return
        
        print()
        print("🚀 开始发布...")
        
        success = publisher.publish(post)
        
        if success:
            print()
            print("=" * 60)
            print("✅ 发布完成！")
            print("=" * 60)
            
            # 标记已发布
            with open(post['filepath'], 'a', encoding='utf-8') as f:
                f.write(f"\n---\n📤 已发布：{datetime.now().isoformat()}\n")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        
    finally:
        publisher.close()

if __name__ == "__main__":
    main()
