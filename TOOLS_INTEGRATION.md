# Agent 工具集成文档

## 概述

FastAPI 应用的 `/chat` 端点现在支持多个工具，让 Agent 可以访问网络信息和解析网页内容。

## 可用工具

### 1. DuckDuckGo 搜索 (`duckduckgo_search`)

使用 DuckDuckGo 搜索引擎搜索网络信息。

**使用场景：**
- 用户询问需要最新信息的问题
- 需要搜索事实、新闻或实时数据
- 查找特定主题的信息

**示例：**
```
用户: "最新的 Python 3.12 特性是什么？"
Agent: 自动调用 duckduckgo_search("Python 3.12 features")
```

### 2. URL 访问和解析 (`fetch_and_parse_url`)

访问并解析给定 URL 的网页内容。

**使用场景：**
- 用户提供 URL 并要求分析内容
- 需要从网页提取信息
- 阅读和理解网页内容

**示例：**
```
用户: "请帮我分析这个网页的内容: https://example.com/article"
Agent: 自动调用 fetch_and_parse_url("https://example.com/article")
```

## 工具功能详情

### fetch_and_parse_url 功能

**提取的内容：**
- 网页标题（title 标签或 h1 标签）
- 主要文本内容（优先提取 main/article 区域，否则提取所有段落）
- 关键链接（最多 5 个）
- HTTP 状态码

**参数：**
- `url` (必需): 完整的 URL 地址
- `max_length` (可选): 返回内容的最大字符长度（默认 5000，最大 10000）

**返回格式：**
```json
{
    "url": "https://example.com",
    "title": "网页标题",
    "content": "主要文本内容...",
    "links": [
        {
            "text": "链接文本",
            "url": "https://example.com/link"
        }
    ],
    "status_code": 200
}
```

## 最佳实践

### 1. URL 验证

✅ **正确：**
- 提供完整的 URL（包含 http:// 或 https://）
- 验证 URL 格式

❌ **错误：**
- 只提供域名或路径
- 未验证 URL 格式

### 2. 内容长度限制

- 默认限制 5000 字符，避免返回过多内容
- 可根据需要调整 `max_length` 参数
- 过长内容会被截断并添加 "..."

### 3. 错误处理

工具会返回错误信息而不是抛出异常：
```json
{
    "error": "请求失败: Connection timeout"
}
```

### 4. 请求头设置

使用浏览器 User-Agent 避免被某些网站阻止：
```python
headers = {
    "User-Agent": "Mozilla/5.0 ..."
}
```

### 5. 超时设置

设置合理的超时时间（默认 10 秒）：
```python
response = requests.get(url, timeout=10)
```

## 常见错误和解决方案

### 1. 无效 URL 格式

**错误：**
```json
{"error": "无效的 URL 格式: example.com"}
```

**解决方案：**
- 确保 URL 包含协议（http:// 或 https://）
- 使用完整的 URL：`https://example.com`

### 2. 请求超时

**错误：**
```json
{"error": "请求超时: https://example.com"}
```

**解决方案：**
- 检查网络连接
- 目标网站可能响应慢
- 考虑增加超时时间（不推荐，可能影响性能）

### 3. 连接被拒绝

**错误：**
```json
{"error": "请求失败: Connection refused"}
```

**解决方案：**
- 检查 URL 是否正确
- 目标服务器可能不可用
- 检查防火墙设置

### 4. 内容解析失败

**错误：**
```json
{"error": "解析失败: ..."}
```

**解决方案：**
- 可能是 HTML 格式异常
- 检查 BeautifulSoup 解析器设置
- 某些动态内容需要 JavaScript 执行（当前不支持）

### 5. 内容为空

**可能原因：**
- 网页主要是 JavaScript 渲染的内容
- 需要登录才能访问
- 网页结构特殊，无法提取主要内容

**解决方案：**
- 对于 JavaScript 渲染的网站，考虑使用 Selenium 或 Playwright
- 检查是否需要认证

## 技术实现

### 依赖库

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
```

### 主要内容提取策略

1. **优先策略：** 查找 `<main>` 或 `<article>` 标签
2. **备用策略：** 查找包含 "content" 或 "main" 的 div
3. **兜底策略：** 提取所有段落和标题标签

### 内容清理

自动移除以下标签：
- `<script>` - JavaScript 代码
- `<style>` - CSS 样式
- `<nav>` - 导航栏
- `<footer>` - 页脚
- `<header>` - 页眉
- `<aside>` - 侧边栏

## 测试

运行测试脚本：
```bash
python3 test_url_parser.py
```

测试包括：
- 基本 URL 访问
- 无效 URL 处理
- 最大长度限制
- 错误处理

## 性能考虑

1. **请求延迟：** 每次 URL 访问可能需要 1-5 秒
2. **内容大小：** 限制内容长度以控制 token 使用
3. **并发请求：** 当前实现是同步的，大量请求可能影响性能

## 安全注意事项

1. **URL 验证：** 验证 URL 格式，防止 SSRF 攻击
2. **内容过滤：** 考虑过滤不当内容
3. **速率限制：** 避免过于频繁的请求
4. **robots.txt：** 尊重网站的 robots.txt 规则
5. **法律合规：** 确保符合网站使用条款

## 使用示例

### 示例 1: 分析网页内容

**用户请求：**
```json
{
    "user_message": "请帮我分析这个网页的内容: https://example.com/article"
}
```

**Agent 流程：**
1. 识别需要访问 URL
2. 调用 `fetch_and_parse_url("https://example.com/article")`
3. 获取网页内容
4. 基于内容生成分析和总结

### 示例 2: 结合搜索和 URL 解析

**用户请求：**
```json
{
    "user_message": "搜索 Python 教程，然后分析第一个结果的网页内容"
}
```

**Agent 流程：**
1. 调用 `duckduckgo_search("Python tutorial")`
2. 获取搜索结果
3. 从结果中提取第一个 URL
4. 调用 `fetch_and_parse_url(url)`
5. 基于网页内容生成详细分析

## 限制

1. **JavaScript 内容：** 无法执行 JavaScript，无法获取动态渲染的内容
2. **认证网站：** 无法访问需要登录的页面
3. **反爬虫：** 某些网站可能阻止自动化访问
4. **内容长度：** 默认限制 5000 字符

## 未来改进

1. 支持 JavaScript 渲染（使用 Selenium/Playwright）
2. 支持认证和 Cookie
3. 缓存机制减少重复请求
4. 异步请求提高性能
5. 更智能的内容提取算法

## 参考资源

- [requests 文档](https://requests.readthedocs.io/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [OpenAI Tools 文档](https://platform.openai.com/docs/guides/function-calling)

