#!/bin/bash
# 初始化 Git 仓库并准备推送到 GitHub

set -e

echo "🚀 Git 仓库初始化向导"
echo "======================"
echo ""

# 检查是否已经是 Git 仓库
if [ -d .git ]; then
    echo "⚠️  当前目录已经是 Git 仓库"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo "1. 初始化 Git 仓库..."
    git init
    git branch -M main
    echo "✅ Git 仓库已初始化"
fi

echo ""
echo "2. 检查 .gitignore..."
if [ -f .gitignore ]; then
    echo "✅ .gitignore 文件存在"
    # 确保 .env 在 .gitignore 中
    if ! grep -q "^\.env$" .gitignore && ! grep -q "\.env" .gitignore; then
        echo ".env" >> .gitignore
        echo "✅ 已添加 .env 到 .gitignore"
    fi
else
    echo "⚠️  .gitignore 不存在，创建中..."
    cat > .gitignore <<EOF
.env
__pycache__/
*.pyc
.DS_Store
EOF
    echo "✅ .gitignore 已创建"
fi

echo ""
echo "3. 添加文件..."
git add .
echo "✅ 文件已添加到暂存区"

echo ""
echo "4. 创建初始提交..."
git commit -m "Initial commit: AI Year-In-Review application" || {
    echo "⚠️  提交失败，可能没有更改需要提交"
}

echo ""
echo "✅ Git 仓库初始化完成！"
echo ""
echo "📝 下一步:"
echo ""
echo "1. 在 GitHub 上创建新仓库:"
echo "   - 访问: https://github.com/new"
echo "   - 仓库名: ai-year-in-review (或你喜欢的名字)"
echo "   - 选择 Public"
echo "   - 不要初始化 README、.gitignore 或 license"
echo ""
echo "2. 添加 SSH 公钥到 GitHub (如果还没添加):"
echo "   - 访问: https://github.com/settings/keys"
echo "   - 点击 'New SSH key'"
echo "   - 粘贴你的公钥:"
echo ""
cat ~/.ssh/id_rsa.pub 2>/dev/null || echo "   (运行: cat ~/.ssh/id_rsa.pub)"
echo ""
echo "3. 添加远程仓库并推送:"
echo "   git remote add origin git@github.com:Gustavo-Liu/YOUR_REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "或者使用 HTTPS (如果 SSH 未配置):"
echo "   git remote add origin https://github.com/Gustavo-Liu/YOUR_REPO_NAME.git"
echo "   git push -u origin main"

