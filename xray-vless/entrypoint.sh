#!/bin/sh

# 后台启动 Caddy (用于保活响应)
caddy run --config /etc/caddy/Caddyfile --adapter caddyfile &

# 前台启动 Xray (主程序)
xray run -c /etc/xray/config.json