FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口（PORT 环境变量会在运行时由 Koyeb 设置）
EXPOSE 8000

# 启动应用
# 使用 shell 形式确保环境变量正确展开
CMD sh -c "python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

