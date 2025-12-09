#!/bin/bash
# 推送代码到 GitHub

set -e

echo "📤 推送到 GitHub"
echo "================"
echo ""

# 检查是否已有远程仓库
if git remote -v | grep -q origin; then
    echo "✅ 远程仓库已配置:"
    git remote -v
    echo ""
    read -p "是否直接推送? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin main
        exit 0
    fi
fi

# 获取仓库名称
echo "请输入 GitHub 仓库信息:"
read -p "仓库名称 (例如: ai-year-in-review): " REPO_NAME

if [ -z "$REPO_NAME" ]; then
    echo "❌ 仓库名称不能为空"
    exit 1
fi

# 使用 SSH URL
REMOTE_URL="git@github.com:Gustavo-Liu/$REPO_NAME.git"

echo ""
echo "📋 配置信息:"
echo "  远程 URL: $REMOTE_URL"
echo "  分支: main"
echo ""

# 检查仓库是否存在
echo "🔍 检查仓库是否存在..."
if git ls-remote "$REMOTE_URL" &>/dev/null; then
    echo "✅ 仓库已存在"
else
    echo "⚠️  仓库不存在或无法访问"
    echo ""
    echo "请先在 GitHub 上创建仓库:"
    echo "  1. 访问: https://github.com/new"
    echo "  2. 仓库名: $REPO_NAME"
    echo "  3. 选择 Public"
    echo "  4. 不要初始化 README、.gitignore 或 license"
    echo ""
    read -p "创建完成后按回车继续..." 
fi

# 添加远程仓库
if ! git remote -v | grep -q origin; then
    echo ""
    echo "添加远程仓库..."
    git remote add origin "$REMOTE_URL"
    echo "✅ 远程仓库已添加"
else
    echo ""
    echo "更新远程仓库 URL..."
    git remote set-url origin "$REMOTE_URL"
    echo "✅ 远程仓库 URL 已更新"
fi

echo ""
echo "📤 推送代码到 GitHub..."
git push -u origin main

echo ""
echo "✅ 代码已成功推送到 GitHub!"
echo ""
echo "🌐 仓库地址: https://github.com/Gustavo-Liu/$REPO_NAME"

