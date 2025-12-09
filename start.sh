#!/bin/bash
# 启动 FastAPI 应用

echo "🚀 启动 AI Year-In-Review 应用..."
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "请创建 .env 文件并设置 OPENAI_API_KEY 和 OPENAI_BASE_URL"
    exit 1
fi

# 检查 summary.json
if [ ! -f summary.json ]; then
    echo "⚠️  警告: summary.json 文件不存在"
    echo "请先运行: python3 analyze_conversations.py"
    echo ""
    read -p "是否继续启动? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 启动应用
PORT=${PORT:-8000}
echo "✅ 启动服务器..."
echo "📱 访问 http://localhost:$PORT 查看应用"
echo ""

python3 -m uvicorn main:app --reload --host 0.0.0.0 --port $PORT

