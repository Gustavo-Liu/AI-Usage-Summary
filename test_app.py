#!/usr/bin/env python3
"""
快速测试脚本 - 验证应用配置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_env_config():
    """测试环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    if api_key:
        print(f"✅ OPENAI_API_KEY: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("❌ OPENAI_API_KEY: 未设置")
    
    print(f"✅ OPENAI_BASE_URL: {base_url}")
    
    return api_key is not None

def test_imports():
    """测试依赖导入"""
    print("\n🔍 检查依赖导入...")
    
    try:
        import fastapi
        print(f"✅ fastapi: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ uvicorn: {e}")
        return False
    
    try:
        from openai import OpenAI
        print("✅ openai: 已安装")
    except ImportError as e:
        print(f"❌ openai: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("✅ pydantic: 已安装")
    except ImportError as e:
        print(f"❌ pydantic: {e}")
        return False
    
    return True

def test_main_app():
    """测试主应用导入"""
    print("\n🔍 检查主应用...")
    
    try:
        from main import app, openai_client
        print("✅ main.py: 导入成功")
        
        if openai_client:
            print("✅ OpenAI 客户端: 已初始化")
        else:
            print("⚠️  OpenAI 客户端: 未初始化（API key 未设置）")
        
        return True
    except Exception as e:
        print(f"❌ main.py: {e}")
        return False

def test_summary_file():
    """测试 summary.json 文件"""
    print("\n🔍 检查数据文件...")
    
    import json
    from pathlib import Path
    
    summary_file = Path("summary.json")
    
    if summary_file.exists():
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ summary.json: 存在 ({len(data)} 个顶级键)")
            return True
        except Exception as e:
            print(f"❌ summary.json: 解析错误 - {e}")
            return False
    else:
        print("⚠️  summary.json: 不存在（需要先运行分析脚本）")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI Year-In-Review - 应用测试")
    print("=" * 50)
    
    results = []
    results.append(("环境变量", test_env_config()))
    results.append(("依赖导入", test_imports()))
    results.append(("主应用", test_main_app()))
    results.append(("数据文件", test_summary_file()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！可以启动应用了")
        print("\n启动命令: python3 -m uvicorn main:app --reload")
        print("或使用: ./start.sh")
    else:
        print("⚠️  部分测试失败，请检查配置")
    print("=" * 50)

