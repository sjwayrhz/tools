FROM alpine:latest

# 安装基础工具和 Caddy
RUN apk add --no-cache ca-certificates caddy curl

# 从官方镜像复制 Xray
COPY --from=teddysun/xray:latest /usr/bin/xray /usr/bin/xray

# 创建配置文件夹
RUN mkdir -p /etc/xray /etc/caddy

# 复制配置文件到容器
COPY config.json /etc/xray/config.json
COPY Caddyfile /etc/caddy/Caddyfile
COPY entrypoint.sh /entrypoint.sh

# 赋予脚本执行权限
RUN chmod +x /entrypoint.sh

# Koyeb 默认监听 8000 端口
EXPOSE 8000

# 启动入口
CMD ["/entrypoint.sh"]