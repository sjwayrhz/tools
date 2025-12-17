# 使用 Nginx Alpine 作为基础镜像 (体积小)
FROM nginx:alpine

# 定义版本和环境变量默认值
ENV XRAY_VERSION=1.8.4
ENV UUID=de0e9792-7c33-4f1f-a586-7a8927894982
ENV PORT=8000

# 1. 安装必要的工具 (curl, unzip)
RUN apk add --no-cache curl unzip

# 2. 下载并安装 Xray (兼容 V2Ray)
# 我们把 Xray 当作 V2Ray 用，性能更好
RUN curl -L -H "Cache-Control: no-cache" -o /tmp/xray.zip \
    https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION}/Xray-linux-64.zip && \
    unzip /tmp/xray.zip -d /usr/bin/ && \
    mv /usr/bin/xray /usr/bin/v2ray && \
    rm /tmp/xray.zip && \
    chmod +x /usr/bin/v2ray

# 3. 创建配置目录
RUN mkdir -p /etc/v2ray

# 4. 复制本地的配置文件到镜像中
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY config.json /etc/v2ray/config.json
COPY index.html /usr/share/nginx/html/index.html
COPY entrypoint.sh /entrypoint.sh

# 5. 赋予脚本执行权限
RUN chmod +x /entrypoint.sh

# 6. 暴露端口 (Koyeb 默认也是 8000)
EXPOSE $PORT

# 7. 设置启动入口
ENTRYPOINT ["/entrypoint.sh"]