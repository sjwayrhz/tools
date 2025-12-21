FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 将脚本复制进去
COPY keepalive.py .

# 设置无缓冲输出，方便看日志
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["python", "keepalive.py"]