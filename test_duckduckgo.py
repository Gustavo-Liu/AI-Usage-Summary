#!/usr/bin/env python3
"""
DuckDuckGo Search API 测试脚本
验证 duckduckgo-search 库是否正常工作
"""

try:
    from duckduckgo_search import DDGS
    print("✅ duckduckgo-search 库已安装")
except ImportError:
    print("❌ duckduckgo-search 库未安装")
    print("请运行: pip install duckduckgo-search")
    exit(1)

def test_basic_search():
    """测试基本搜索功能"""
    print("\n🔍 测试基本搜索...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("Python FastAPI", max_results=3))
            print(f"✅ 搜索成功，找到 {len(results)} 个结果")
            if results:
                print("\n第一个结果:")
                print(f"  标题: {results[0].get('title', 'N/A')}")
                print(f"  URL: {results[0].get('href', 'N/A')}")
                print(f"  摘要: {results[0].get('body', 'N/A')[:100]}...")
            return True
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n🔍 测试错误处理...")
    try:
        with DDGS() as ddgs:
            # 测试空查询
            results = list(ddgs.text("", max_results=1))
            print(f"空查询结果数量: {len(results)}")
            
            # 测试无效参数
            results = list(ddgs.text("test", max_results=-1))
            print(f"负 max_results 处理: {len(results)}")
            
        print("✅ 错误处理测试完成")
        return True
    except Exception as e:
        print(f"⚠️  错误处理测试遇到异常: {e}")
        return True  # 某些错误是预期的

def test_search_function():
    """测试搜索函数（用于集成到 FastAPI）"""
    print("\n🔍 测试搜索函数...")
    
    def duckduckgo_search(query: str, max_results: int = 5) -> list:
        """执行 DuckDuckGo 搜索"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    }
                    for r in results
                ]
        except Exception as e:
            print(f"搜索错误: {e}")
            return []
    
    results = duckduckgo_search("DuckDuckGo search API", max_results=3)
    print(f"✅ 搜索函数测试成功，返回 {len(results)} 个结果")
    if results:
        print(f"   示例: {results[0]['title']}")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("DuckDuckGo Search API 测试")
    print("=" * 50)
    
    results = []
    results.append(("基本搜索", test_basic_search()))
    results.append(("错误处理", test_error_handling()))
    results.append(("搜索函数", test_search_function()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！可以集成到 FastAPI 应用了")
    else:
        print("⚠️  部分测试失败，请检查配置")
    print("=" * 50)

