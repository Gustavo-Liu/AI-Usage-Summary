# GitHub 设置指南

## 方法一：使用 SSH 密钥（推荐）

### 1. 运行设置脚本

```bash
./setup-github.sh
```

脚本会自动：
- 检查 Git 配置
- 检查或生成 SSH 密钥
- 显示公钥内容

### 2. 添加 SSH 公钥到 GitHub

1. 访问: https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴公钥内容
4. 点击 "Add SSH key"

### 3. 测试连接

```bash
ssh -T git@github.com
```

如果看到 "Hi username! You've successfully authenticated..." 说明成功。

## 方法二：使用 HTTPS + Personal Access Token

### 1. 创建 Personal Access Token

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `repo` (完整仓库访问)
4. 生成并复制 token

### 2. 使用 Token 推送

```bash
git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
```

或者使用 GitHub CLI:
```bash
gh auth login
```

## 初始化 Git 仓库并推送

```bash
# 1. 初始化仓库
git init
git branch -M main

# 2. 添加文件
git add .

# 3. 提交
git commit -m "Initial commit: AI Year-In-Review app"

# 4. 添加远程仓库（在 GitHub 上创建仓库后）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 5. 推送
git push -u origin main
```

## 当前 Git 配置

- 用户名: `Gustavo-Liu`
- 邮箱: `yli2932@emory.edu`

## 快速检查

```bash
# 检查 Git 配置
git config --global user.name
git config --global user.email

# 检查 SSH 密钥
ls -la ~/.ssh/id_*.pub

# 测试 GitHub 连接
ssh -T git@github.com
```

