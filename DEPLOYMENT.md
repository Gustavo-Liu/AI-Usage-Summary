# 部署指南

## 部署到 AI Builders 平台

### 前置要求

1. **GitHub 仓库**
   - 将代码推送到 GitHub 公开仓库
   - 确保所有文件都已提交

2. **API Key**
   - 使用 `SECOND_MIND_API_KEY`（已在 .env 中配置）

### 快速部署

#### 方法一：使用部署脚本（推荐）

1. **配置 deploy-config.json**
   ```json
   {
     "repo_url": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME",
     "service_name": "ai-year-in-review",
     "branch": "main",
     "port": 8000
   }
   ```

2. **运行部署脚本**
   ```bash
   ./deploy.sh
   ```

#### 方法二：手动部署

```bash
curl -X POST "https://space.ai-builders.com/backend/v1/deployments" \
  -H "Authorization: Bearer sk_612ffd16_2f4afacbc641f99b6122dc696e4715dfc2b3" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/YOUR_USERNAME/YOUR_REPO_NAME",
    "service_name": "ai-year-in-review",
    "branch": "main",
    "port": 8000
  }'
```

### 部署前检查清单

- [ ] 代码已推送到 GitHub
- [ ] 仓库是公开的
- [ ] Dockerfile 存在且正确
- [ ] requirements.txt 包含所有依赖
- [ ] .env 文件已配置（但不要提交到 Git）
- [ ] deploy-config.json 已更新

### 部署后

1. **等待 5-10 分钟**让部署完成

2. **检查部署状态**
   ```bash
   curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://space.ai-builders.com/backend/v1/deployments/YOUR_SERVICE_NAME
   ```

3. **访问网站**
   ```
   https://YOUR_SERVICE_NAME.ai-builders.space
   ```

### 重要提示

- **不要提交敏感信息**：确保 `.env` 在 `.gitignore` 中
- **环境变量**：`AI_BUILDER_TOKEN` 会自动注入，无需在 env_vars 中设置
- **端口**：应用必须使用 `PORT` 环境变量（Dockerfile 已配置）
- **单进程**：应用必须从单个端口提供所有服务

### 故障排除

如果部署失败：
1. 检查 GitHub 仓库 URL 是否正确
2. 确认分支名称正确
3. 查看部署响应中的错误信息
4. 检查 Dockerfile 是否正确

