# 基于 Ubuntu 22.04 的模拟服务器环境
FROM ubuntu:22.04

# 设置环境变量，避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 更新软件源并安装基础工具
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip3 install --no-cache-dir \
    flask \
    gunicorn

# 创建工作目录
WORKDIR /app

# 创建测试用的 Flask 应用（用于验证环境）
RUN echo 'from flask import Flask\napp = Flask(__name__)\n\n@app.route("/")\ndef hello():\n    return "Hello from Docker server!"\n\nif __name__ == "__main__":\n    app.run(host="0.0.0.0", port=5000)' > /app/app.py

# 暴露端口
EXPOSE 80 5000 8000

# 默认启动命令：gunicorn 运行 Flask 应用
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]