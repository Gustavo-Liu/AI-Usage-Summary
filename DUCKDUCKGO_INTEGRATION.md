# DuckDuckGo Search API 集成文档

## 概述

已成功将 DuckDuckGo 搜索功能集成到 FastAPI 应用的 `/chat` 端点中。Agent 现在可以使用 `duckduckgo_search` 工具来搜索网络信息。

## 安装

```bash
pip install duckduckgo-search
```

## 使用方法

### 基本用法

```python
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = list(ddgs.text("搜索查询", max_results=5))
```

### 在 FastAPI 中使用

Agent 会自动决定何时使用搜索工具。当用户询问需要最新信息的问题时，Agent 会调用 `duckduckgo_search` 工具。

**示例请求：**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_message": "最新的 Python 3.12 特性是什么？"}'
```

Agent 会自动：
1. 识别需要搜索的问题
2. 调用 `duckduckgo_search` 工具
3. 基于搜索结果生成回复

## 最佳实践

### 1. 使用上下文管理器

✅ **正确：**
```python
with DDGS() as ddgs:
    results = list(ddgs.text(query, max_results=5))
```

❌ **错误：**
```python
ddgs = DDGS()
results = list(ddgs.text(query))  # 没有正确关闭连接
```

### 2. 限制搜索结果数量

- 默认返回 5 个结果
- 最大建议 10 个结果
- 太多结果会增加处理时间和成本

### 3. 错误处理

```python
try:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
except Exception as e:
    # 返回错误信息而不是抛出异常
    return [{"error": f"搜索失败: {str(e)}"}]
```

### 4. 查询字符串优化

- 使用清晰、具体的查询
- 避免过于宽泛的搜索
- 包含关键信息以提高相关性

### 5. 结果格式化

返回结构化的结果：
```python
{
    "title": "结果标题",
    "url": "结果 URL",
    "snippet": "结果摘要"
}
```

## 常见错误和解决方案

### 1. RuntimeWarning: 包已重命名

**错误：**
```
RuntimeWarning: This package (`duckduckgo_search`) has been renamed to `ddgs`!
```

**解决方案：**
- 这是警告，不是错误，可以忽略
- 或者使用新包名：`pip install ddgs` 并 `from ddgs import DDGS`

### 2. 空查询错误

**错误：**
```
keywords is mandatory
```

**解决方案：**
- 确保查询字符串不为空
- 添加验证：`if not query or not query.strip(): return []`

### 3. 网络连接问题

**错误：**
```
Connection error / Timeout
```

**解决方案：**
- 检查网络连接
- 添加重试机制
- 设置合理的超时时间

### 4. 搜索结果为空

**可能原因：**
- 查询太具体或太宽泛
- 网络问题
- DuckDuckGo 服务暂时不可用

**解决方案：**
- 尝试不同的查询词
- 检查网络连接
- 添加备用搜索源

### 5. 工具调用格式错误

**错误：**
```
Invalid tool call format
```

**解决方案：**
- 确保工具定义符合 OpenAI 工具格式
- 检查参数类型和必需字段
- 验证 JSON 序列化

## 工具定义

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "duckduckgo_search",
            "description": "使用 DuckDuckGo 搜索引擎搜索网络信息...",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要搜索的查询字符串"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回的最大结果数量",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

## 测试

运行测试脚本：
```bash
python3 test_duckduckgo.py
```

## 性能考虑

1. **搜索延迟**：每次搜索可能需要 1-3 秒
2. **API 调用**：工具调用会增加一次额外的 API 请求
3. **成本**：工具调用会增加 token 使用量

## 安全注意事项

1. **查询验证**：验证用户输入的查询字符串
2. **结果过滤**：考虑过滤不当内容
3. **速率限制**：避免过于频繁的搜索请求

## 示例对话

**用户：** "最新的 AI 新闻是什么？"

**Agent 流程：**
1. 识别需要搜索
2. 调用 `duckduckgo_search("最新 AI 新闻", max_results=5)`
3. 获取搜索结果
4. 基于结果生成回复

**用户：** "你好"

**Agent 流程：**
1. 识别不需要搜索
2. 直接回复，不调用工具

## 故障排除

如果搜索功能不工作：

1. 检查库是否安装：`pip list | grep duckduckgo`
2. 测试独立脚本：`python3 test_duckduckgo.py`
3. 检查网络连接
4. 查看应用日志
5. 验证工具定义格式

## 参考资源

- [duckduckgo-search PyPI](https://pypi.org/project/duckduckgo-search/)
- [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/function-calling)

