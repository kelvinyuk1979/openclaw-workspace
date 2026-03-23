#!/usr/bin/env python3
"""
统一交易检查脚本
同时执行 OKX 量化检查 + Polymarket 自动交易
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def print_header(text: str):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def run_okx_check():
    """执行 OKX 量化检查"""
    print_header("📈 OKX 量化交易检查")
    
    okx_dir = Path.home() / '.openclaw' / 'workspace' / 'skills' / 'stock-market-pro' / 'quant-trading-system'
    
    try:
        # 调用 OKX 检查脚本
        result = subprocess.run(
            ['python3', 'okx_check.py'],
            cwd=okx_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ OKX 检查失败：{e}")
        return False


def run_polymarket_check():
    """执行 Polymarket 自动交易"""
    print_header("🎲 Polymarket 自动交易")
    
    poly_dir = Path.home() / '.openclaw' / 'workspace' / 'polymarket-trading-system'
    
    try:
        result = subprocess.run(
            ['python3', 'main.py'],
            cwd=poly_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Polymarket 检查失败：{e}")
        return False


def main():
    """主函数"""
    print_header("🚀 统一交易检查 - OKX + Polymarket")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    okx_success = run_okx_check()
    poly_success = run_polymarket_check()
    
    print_header("✅ 统一检查完成")
    print(f"OKX: {'✅ 成功' if okx_success else '❌ 失败'}")
    print(f"Polymarket: {'✅ 成功' if poly_success else '❌ 失败'}")
    
    if okx_success and poly_success:
        print("\n🎉 所有系统运行正常！")
        return 0
    else:
        print("\n⚠️ 部分系统失败，请检查日志")
        return 1


if __name__ == '__main__':
    sys.exit(main())
