#!/bin/sh

# 1. 设置最终要使用的 UUID
# 如果环境变量 $UUID 有值则用它，否则使用默认的固定 ID
if [ -z "$UUID" ]; then
  FINAL_UUID="de0e9792-7c33-4f1f-a586-7a8927894982"
  echo "Warning: UUID variable is empty. Using default UUID: $FINAL_UUID"
else
  FINAL_UUID="$UUID"
  echo "Success: Using custom UUID provided via environment: $FINAL_UUID"
fi

# 2. 使用 sed 命令将模板中的 UUID_PLACEHOLDER 替换为 FINAL_UUID
# 这样无论 FINAL_UUID 是默认的还是用户自定义的，都能替换成功
sed -i "s/UUID_PLACEHOLDER/$FINAL_UUID/g" /etc/v2ray/config.json

echo "V2Ray 路径: /ws"
echo "Web 路径: /"
echo "连接端口: 443 (HTTPS)"

# 3. 启动 V2Ray (后台运行)
/usr/bin/v2ray run -c /etc/v2ray/config.json &

# 4. 启动 Nginx (前台运行，防止容器退出)
nginx -g "daemon off;"