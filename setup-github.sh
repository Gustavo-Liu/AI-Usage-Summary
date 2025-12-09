#!/bin/bash
# GitHub 设置脚本

echo "🔐 GitHub 设置向导"
echo "=================="
echo ""

# 检查 Git 配置
echo "1. 检查 Git 配置..."
USER_NAME=$(git config --global user.name)
USER_EMAIL=$(git config --global user.email)

if [ -z "$USER_NAME" ] || [ -z "$USER_EMAIL" ]; then
    echo "⚠️  Git 用户信息未配置"
    read -p "请输入你的 GitHub 用户名: " GITHUB_USERNAME
    read -p "请输入你的 GitHub 邮箱: " GITHUB_EMAIL
    
    git config --global user.name "$GITHUB_USERNAME"
    git config --global user.email "$GITHUB_EMAIL"
    echo "✅ Git 用户信息已配置"
else
    echo "✅ Git 用户信息已配置:"
    echo "   用户名: $USER_NAME"
    echo "   邮箱: $USER_EMAIL"
fi

echo ""
echo "2. 检查 SSH 密钥..."

# 检查是否已有 SSH 密钥
if [ -f ~/.ssh/id_ed25519.pub ]; then
    SSH_KEY_FILE=~/.ssh/id_ed25519.pub
    KEY_TYPE="ed25519"
elif [ -f ~/.ssh/id_rsa.pub ]; then
    SSH_KEY_FILE=~/.ssh/id_rsa.pub
    KEY_TYPE="RSA"
else
    echo "❌ 未找到 SSH 密钥"
    echo ""
    read -p "是否生成新的 SSH 密钥? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入你的 GitHub 邮箱: " GITHUB_EMAIL
        ssh-keygen -t ed25519 -C "$GITHUB_EMAIL" -f ~/.ssh/id_ed25519 -N ""
        SSH_KEY_FILE=~/.ssh/id_ed25519.pub
        KEY_TYPE="ed25519"
        echo "✅ SSH 密钥已生成"
    else
        echo "跳过 SSH 密钥生成"
        exit 0
    fi
fi

if [ -f "$SSH_KEY_FILE" ]; then
    echo "✅ 找到 SSH 公钥: $SSH_KEY_FILE"
    echo ""
    echo "📋 请将以下公钥添加到 GitHub:"
    echo "   1. 访问: https://github.com/settings/keys"
    echo "   2. 点击 'New SSH key'"
    echo "   3. 复制下面的公钥内容:"
    echo ""
    echo "--- 公钥开始 ---"
    cat "$SSH_KEY_FILE"
    echo "--- 公钥结束 ---"
    echo ""
    
    # 尝试复制到剪贴板（macOS）
    if command -v pbcopy &> /dev/null; then
        cat "$SSH_KEY_FILE" | pbcopy
        echo "✅ 公钥已复制到剪贴板（macOS）"
    fi
    
    echo ""
    read -p "按回车键继续测试 SSH 连接..." 
    
    echo ""
    echo "🔍 测试 SSH 连接..."
    ssh -T git@github.com 2>&1 | head -3
    
    echo ""
    echo "✅ 设置完成！"
    echo ""
    echo "下一步:"
    echo "  1. 如果 SSH 连接成功，可以使用 SSH URL 推送代码"
    echo "  2. 如果失败，可以使用 HTTPS + Personal Access Token"
fi

