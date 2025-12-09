"""
AI Year-In-Review FastAPI Application
提供统计可视化展示和聊天 API
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# 加载环境变量
load_dotenv()

# 初始化 FastAPI
app = FastAPI(
    title="AI Year-In-Review",
    description="AI 对话年度回顾可视化平台",
    version="1.0.0"
)

# 静态文件目录
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# OpenAI 客户端配置 - 使用 SECOND_MIND_API_KEY
SECOND_MIND_API_KEY = os.getenv("SECOND_MIND_API_KEY")
SECOND_MIND_BASE_URL = os.getenv("SECOND_MIND_BASE_URL", "https://space.ai-builders.com/backend/v1")

# 确保 base_url 格式正确（应该已经包含 /v1）
if SECOND_MIND_BASE_URL and not SECOND_MIND_BASE_URL.endswith("/v1"):
    if SECOND_MIND_BASE_URL.endswith("/"):
        SECOND_MIND_BASE_URL = SECOND_MIND_BASE_URL + "v1"
    else:
        SECOND_MIND_BASE_URL = SECOND_MIND_BASE_URL + "/v1"

if not SECOND_MIND_API_KEY:
    print("警告: SECOND_MIND_API_KEY 未在环境变量中设置")

# 初始化 OpenAI 客户端
openai_client = OpenAI(
    api_key=SECOND_MIND_API_KEY,
    base_url=SECOND_MIND_BASE_URL
) if SECOND_MIND_API_KEY else None

# 打印配置信息（用于调试）
if openai_client:
    print(f"✅ OpenAI 客户端已初始化")
    print(f"   Base URL: {SECOND_MIND_BASE_URL}")
    print(f"   API Key: {SECOND_MIND_API_KEY[:20]}...")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_message: str


class ChatResponse(BaseModel):
    """聊天响应模型"""
    content: str


# URL 访问和解析工具函数
def fetch_and_parse_url(url: str, max_length: int = 5000) -> Dict[str, Any]:
    """
    获取并解析给定 URL 的网页内容
    
    Args:
        url: 要访问的 URL
        max_length: 最大返回文本长度（默认 5000 字符）
    
    Returns:
        包含标题、主要内容、链接等的字典
    """
    try:
        # 预处理 URL：如果没有协议，尝试添加
        original_url = url
        if not url.startswith(('http://', 'https://')):
            # 检查是否是 localhost 或 127.0.0.1
            if url.startswith(('localhost', '127.0.0.1')):
                url = f"http://{url}"
            else:
                # 对于其他 URL，尝试添加 https://
                url = f"https://{url}"
        
        # 验证 URL 格式
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                "url": original_url,
                "title": None,
                "content": None,
                "score": 0.0,
                "raw_content": None,
                "active": False,
                "error": f"无效的 URL 格式: {original_url}"
            }
        
        # 处理本地 URL（localhost 或 127.0.0.1）
        # 确保本地服务使用 http 而不是 https（本地服务通常使用 http）
        is_local = (parsed.netloc in ['localhost', '127.0.0.1'] or 
                   parsed.netloc.startswith('localhost:') or 
                   parsed.netloc.startswith('127.0.0.1:'))
        
        if is_local and parsed.scheme == 'https':
            url = url.replace('https://', 'http://', 1)
            parsed = urlparse(url)
        
        # 设置请求头，模拟浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 对于本地请求，禁用 SSL 验证（如果使用 https）
        verify_ssl = not (parsed.netloc in ['localhost', '127.0.0.1'] or 
                         parsed.netloc.startswith('localhost:') or 
                         parsed.netloc.startswith('127.0.0.1:'))
        
        # 发送 GET 请求，设置超时
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True, verify=verify_ssl)
        response.raise_for_status()
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = ""
        if soup.title:
            title = soup.title.get_text().strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        
        # 移除脚本和样式标签
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # 提取主要内容
        # 优先提取 main, article, 或主要内容区域
        content = ""
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'main' in x.lower()))
        
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
        else:
            # 如果没有找到主要内容区域，提取所有段落
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # 限制内容长度
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        # 提取关键链接
        links = []
        for link in soup.find_all('a', href=True)[:10]:  # 最多提取 10 个链接
            href = link.get('href')
            text = link.get_text(strip=True)
            if href and text:
                # 处理相对链接
                absolute_url = urljoin(url, href)
                links.append({
                    "text": text[:100],  # 限制文本长度
                    "url": absolute_url
                })
        
        # 计算内容相关性分数（简单实现：基于内容长度和关键词）
        # 这里使用一个简单的分数计算，可以根据需要改进
        score = min(1.0, len(content) / 1000.0) if content else 0.0
        
        return {
            "url": url,
            "title": title,
            "content": content,
            "score": round(score, 8),
            "raw_content": None,  # 原始 HTML 内容不返回，节省空间
            "active": True,  # 表示内容已成功获取
            "links": links[:5],  # 最多返回 5 个链接
            "status_code": response.status_code
        }
    
    except requests.exceptions.Timeout:
        return {
            "url": url,
            "title": None,
            "content": None,
            "score": 0.0,
            "raw_content": None,
            "active": False,
            "error": f"请求超时: {url}"
        }
    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "score": 0.0,
            "raw_content": None,
            "active": False,
            "error": f"请求失败: {str(e)}"
        }
    except Exception as e:
        return {
            "url": url,
            "title": None,
            "content": None,
            "score": 0.0,
            "raw_content": None,
            "active": False,
            "error": f"解析失败: {str(e)}"
        }


# DuckDuckGo 搜索工具函数
def duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    执行 DuckDuckGo 网络搜索
    
    Args:
        query: 搜索查询字符串
        max_results: 最大返回结果数量（默认 5）
    
    Returns:
        搜索结果列表，每个结果包含 title, url, snippet
    """
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
        # 返回错误信息而不是抛出异常，让 agent 知道搜索失败
        return [{"error": f"搜索失败: {str(e)}"}]


# 定义工具（Tools）给 OpenAI API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "duckduckgo_search",
            "description": "使用 DuckDuckGo 搜索引擎搜索网络信息。当用户询问需要最新信息、事实、新闻或需要搜索网络的问题时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要搜索的查询字符串，应该清晰、具体"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回的最大结果数量，默认 5，最大 10",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_and_parse_url",
            "description": "访问并解析给定 URL 的网页内容。当用户提供 URL 链接并要求获取、阅读或分析网页内容时使用此工具。可以提取网页标题、主要文本内容和关键链接。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要访问和解析的完整 URL 地址（必须包含 http:// 或 https://）"
                    },
                    "max_length": {
                        "type": "integer",
                        "description": "返回内容的最大字符长度，默认 5000，最大 10000",
                        "default": 5000,
                        "minimum": 1000,
                        "maximum": 10000
                    }
                },
                "required": ["url"]
            }
        }
    }
]


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页面"""
    html_file = static_dir / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>AI Year-In-Review</h1><p>请创建 static/index.html</p>", status_code=200)


@app.get("/api/summary")
async def get_summary():
    """获取分析摘要数据"""
    summary_file = Path(__file__).parent / "summary.json"
    
    if not summary_file.exists():
        raise HTTPException(status_code=404, detail="summary.json 文件不存在，请先运行分析脚本")
    
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
        return JSONResponse(content=summary_data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON 解析错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件错误: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天端点 - 调用 OpenAI 兼容的聊天补全 API
    
    请求体:
    - user_message: 用户消息字符串
    
    返回:
    - content: 助手回复内容
    """
    if not openai_client:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API 未配置，请设置 SECOND_MIND_API_KEY 环境变量"
        )
    
    if not request.user_message or not request.user_message.strip():
        raise HTTPException(status_code=400, detail="user_message 不能为空")
    
    try:
        # 构建消息历史
        messages = [
            {
                "role": "user",
                "content": request.user_message
            }
        ]
        
        # 调用 OpenAI API，支持工具调用
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"  # 让模型自动决定是否使用工具
        )
        
        # 提取响应
        if not response.choices or len(response.choices) == 0:
            raise HTTPException(
                status_code=500,
                detail="API 返回了空的响应"
            )
        
        message = response.choices[0].message
        
        # 处理工具调用（支持多轮工具调用，最多 5 轮避免无限循环）
        max_tool_iterations = 5
        iteration = 0
        
        while message.tool_calls and iteration < max_tool_iterations:
            iteration += 1
            
            # 收集所有工具调用
            tool_calls_list = []
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}
                
                # 执行工具调用
                if function_name == "duckduckgo_search":
                    search_query = function_args.get("query", "")
                    max_results = function_args.get("max_results", 5)
                    tool_result = duckduckgo_search(search_query, max_results)
                
                elif function_name == "fetch_and_parse_url":
                    url = function_args.get("url", "")
                    max_length = function_args.get("max_length", 5000)
                    tool_result = fetch_and_parse_url(url, max_length)
                
                else:
                    tool_result = {"error": f"未知的工具: {function_name}"}
                
                # 添加工具调用和响应到消息历史
                tool_calls_list.append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": tool_call.function.arguments
                    }
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                })
            
            # 添加 assistant 消息（包含工具调用）
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": tool_calls_list
            })
            
            # 再次调用 API
            response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            if not response.choices or len(response.choices) == 0:
                raise HTTPException(
                    status_code=500,
                    detail="API 返回了空的响应"
                )
            
            message = response.choices[0].message
        
        # 提取最终回复内容
        assistant_content = message.content
        
        # 如果最终还有工具调用但没有内容，说明可能进入了循环
        if message.tool_calls and not assistant_content:
            raise HTTPException(
                status_code=500,
                detail="工具调用循环或无法生成最终回复"
            )
        
        if not assistant_content:
            raise HTTPException(
                status_code=500,
                detail="API 返回的内容为空"
            )
        
        return ChatResponse(content=assistant_content)
    
    except HTTPException:
        # 重新抛出 HTTPException
        raise
    except Exception as e:
        # 提供更详细的错误信息
        error_msg = str(e)
        error_type = type(e).__name__
        
        # 检查是否是认证错误
        if "401" in error_msg or "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail=f"API 认证失败: 请检查 SECOND_MIND_API_KEY 是否正确，以及 SECOND_MIND_BASE_URL 是否匹配你的 API 提供商。当前 Base URL: {SECOND_MIND_BASE_URL}"
            )
        
        # 检查是否是模型错误
        if "model" in error_msg.lower() or "gpt-5" in error_msg.lower() or "not found" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"模型错误: {error_msg}。提示: 'gpt-5' 可能不是有效的模型名称，请检查你的 API 提供商支持的模型列表。"
            )
        
        # 检查是否是连接错误
        if "connection" in error_msg.lower() or "connect" in error_msg.lower() or "refused" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail=f"无法连接到后端 API ({SECOND_MIND_BASE_URL}): {error_msg}。请检查网络连接和 API 端点配置。"
            )
        
        # 检查是否是 API 错误
        if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
            status_code = e.response.status_code
            error_msg = f"API 返回错误 (状态码: {status_code}): {error_msg}"
        
        raise HTTPException(
            status_code=500,
            detail=f"调用聊天 API 时出错 ({error_type}): {error_msg}"
        )


@app.get("/chat")
async def chat_get():
    """聊天端点说明（GET 请求）"""
    return {
        "message": "此端点仅接受 POST 请求",
        "usage": {
            "method": "POST",
            "url": "/chat",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "user_message": "你的消息内容"
            },
            "example": {
                "curl": 'curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d \'{"user_message": "Hello"}\''
            }
        }
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "openai_configured": openai_client is not None,
        "summary_exists": (Path(__file__).parent / "summary.json").exists()
    }


if __name__ == "__main__":
    import uvicorn
    # 可以通过环境变量 PORT 来设置，默认使用 8000
    # 部署时 Koyeb 会设置 PORT 环境变量
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

