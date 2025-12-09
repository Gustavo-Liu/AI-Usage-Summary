#!/bin/bash
# 部署脚本 - 部署到 AI Builders 平台

set -e

echo "🚀 AI Year-In-Review 部署脚本"
echo ""

# 检查 deploy-config.json
if [ ! -f deploy-config.json ]; then
    echo "❌ 错误: deploy-config.json 文件不存在"
    echo "请先创建并配置 deploy-config.json 文件"
    exit 1
fi

# 读取配置
REPO_URL=$(python3 -c "import json; print(json.load(open('deploy-config.json'))['repo_url'])")
SERVICE_NAME=$(python3 -c "import json; print(json.load(open('deploy-config.json'))['service_name'])")
BRANCH=$(python3 -c "import json; print(json.load(open('deploy-config.json'))['branch'])")
PORT=$(python3 -c "import json; print(json.load(open('deploy-config.json'))['port'])")

# 检查配置
if [ "$REPO_URL" == "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME" ]; then
    echo "❌ 错误: 请先更新 deploy-config.json 中的 repo_url"
    exit 1
fi

# 读取 API key
API_KEY=$(grep "SECOND_MIND_API_KEY" .env | cut -d '=' -f2)
if [ -z "$API_KEY" ]; then
    echo "❌ 错误: 未找到 SECOND_MIND_API_KEY"
    exit 1
fi

# API 端点
API_BASE="https://space.ai-builders.com/backend"
DEPLOY_ENDPOINT="$API_BASE/v1/deployments"

echo "📋 部署配置:"
echo "  仓库: $REPO_URL"
echo "  服务名: $SERVICE_NAME"
echo "  分支: $BRANCH"
echo "  端口: $PORT"
echo ""

# 检查是否有 env_vars
ENV_VARS_JSON="{}"
if python3 -c "import json; d=json.load(open('deploy-config.json')); print('env_vars' in d and d['env_vars'])" 2>/dev/null | grep -q True; then
    ENV_VARS_JSON=$(python3 -c "import json; print(json.dumps(json.load(open('deploy-config.json'))['env_vars']))")
fi

# 构建请求体
REQUEST_BODY=$(python3 <<EOF
import json
config = json.load(open('deploy-config.json'))
payload = {
    "repo_url": config["repo_url"],
    "service_name": config["service_name"],
    "branch": config["branch"],
    "port": config["port"]
}
if "env_vars" in config and config["env_vars"]:
    payload["env_vars"] = config["env_vars"]
print(json.dumps(payload))
EOF
)

echo "📤 发送部署请求..."
echo ""

# 发送部署请求
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$DEPLOY_ENDPOINT" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP 状态码: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" == "202" ]; then
    echo "✅ 部署请求已提交！"
    echo ""
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    echo ""
    echo "📝 下一步:"
    echo "  1. 等待 5-10 分钟让部署完成"
    echo "  2. 检查部署状态: curl -H \"Authorization: Bearer $API_KEY\" $API_BASE/v1/deployments/$SERVICE_NAME"
    echo "  3. 访问: https://$SERVICE_NAME.ai-builders.space"
elif [ "$HTTP_CODE" == "401" ]; then
    echo "❌ 认证失败: 请检查 API key 是否正确"
    echo "$BODY"
    exit 1
elif [ "$HTTP_CODE" == "422" ]; then
    echo "❌ 验证错误: 请检查请求参数"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
else
    echo "❌ 部署失败"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi

