#!/bin/bash
# =========================================
# TUIC v1.4.5 over QUIC 部署脚本 (Generated)
# SNI Domain: www.cctv.com
# Default Port: 65442
# =========================================
set -euo pipefail
export LC_ALL=C
IFS=$'\n\t'

MASQ_DOMAIN="www.cctv.com"
SERVER_TOML="server.toml"
CERT_PEM="tuic-cert.pem"
KEY_PEM="tuic-key.pem"
LINK_TXT="tuic_link.txt"
TUIC_BIN="./tuic-server"

# ========== 默认设置 ==========
DEFAULT_PORT=65442

# ========== 端口处理逻辑 ==========
read_port() {
  TUIC_PORT="$DEFAULT_PORT"

  # 处理传入参数
  # 兼容: bash script.sh 8080
  # 兼容: bash script.sh -s -- 8080
  # 兼容: bash script.sh --port 8080
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -s|--set-port|--port)
        if [[ -n "${2:-}" && "${2:-}" != -* ]]; then
          TUIC_PORT="$2"
          shift 2
        else
          shift
        fi
        ;;
      [0-9]*)
        # 如果参数纯数字，视为端口
        TUIC_PORT="$1"
        shift
        ;;
      *)
        shift
        ;;
    esac
  done

  echo "✅ Port configured: $TUIC_PORT"
}

# ========== 检查已有配置 ==========
load_existing_config() {
  if [[ -f "$SERVER_TOML" ]]; then
    TUIC_PORT=$(grep '^server' "$SERVER_TOML" | grep -Eo '[0-9]+')
    TUIC_UUID=$(grep '^\[users\]' -A1 "$SERVER_TOML" | tail -n1 | awk '{print $1}')
    TUIC_PASSWORD=$(grep '^\[users\]' -A1 "$SERVER_TOML" | tail -n1 | awk -F'"' '{print $2}')
    echo "📂 Existing config detected. Loading..."
    return 0
  fi
  return 1
}

# ========== 生成证书 ==========
generate_cert() {
  if [[ -f "$CERT_PEM" && -f "$KEY_PEM" ]]; then
    echo "🔐 Certificate exists, skipping."
    return
  fi
  echo "🔐 Generating self-signed certificate for ${MASQ_DOMAIN}..."
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1     -keyout "$KEY_PEM" -out "$CERT_PEM" -subj "/CN=${MASQ_DOMAIN}" -days 365 -nodes >/dev/null 2>&1
  chmod 600 "$KEY_PEM"
  chmod 644 "$CERT_PEM"
}

# ========== 下载 tuic-server ==========
check_tuic_server() {
  if [[ -x "$TUIC_BIN" ]]; then
    echo "✅ tuic-server already exists."
    return
  fi
  echo "📥 Downloading tuic-server..."
  curl -L -o "$TUIC_BIN" "https://github.com/Itsusinn/tuic/releases/download/v1.4.5/tuic-server-x86_64-linux"
  chmod +x "$TUIC_BIN"
}

# ========== 生成配置 ==========
generate_config() {
  # 若未定义UUID或密码（覆盖安装情况），使用脚本顶部默认值或随机生成
  LOCAL_UUID="${TUIC_UUID:-a09b3bb7-09b9-4b69-9244-63574837a8b8}"
  LOCAL_PASS="${TUIC_PASSWORD:-b2a92e1a76076287ecf487f9f921c016}"

cat > "$SERVER_TOML" <<EOF
log_level = "warn"
server = "0.0.0.0:${TUIC_PORT}"

udp_relay_ipv6 = false
zero_rtt_handshake = true
dual_stack = false
auth_timeout = "8s"
task_negotiation_timeout = "4s"
gc_interval = "8s"
gc_lifetime = "8s"
max_external_packet_size = 8192

[users]
${LOCAL_UUID} = "${LOCAL_PASS}"

[tls]
certificate = "$CERT_PEM"
private_key = "$KEY_PEM"
alpn = ["h3"]

[restful]
addr = "127.0.0.1:${TUIC_PORT}"
secret = "$(openssl rand -hex 16)"
maximum_clients_per_user = 999999999

[quic]
initial_mtu = $((1200 + RANDOM % 200))
min_mtu = 1200
gso = true
pmtu = true
send_window = 33554432
receive_window = 16777216
max_idle_time = "25s"

[quic.congestion_control]
controller = "bbr"
initial_window = 6291456
EOF
  
  # 导出变量供后续生成链接使用
  TUIC_UUID="$LOCAL_UUID"
  TUIC_PASSWORD="$LOCAL_PASS"
}

# ========== 获取公网IP ==========
get_server_ip() {
  curl -s --connect-timeout 3 https://api64.ipify.org || echo "127.0.0.1"
}

# ========== 生成TUIC链接 ==========
generate_link() {
  local ip="$1"
  # 节点输出链接
  cat > "$LINK_TXT" <<EOF
tuic://${TUIC_UUID}:${TUIC_PASSWORD}@${ip}:${TUIC_PORT}?congestion_control=bbr&alpn=h3&allowInsecure=1&sni=${MASQ_DOMAIN}&udp_relay_mode=native&disable_sni=0&reduce_rtt=1&max_udp_relay_packet_size=8192#TUIC-${ip}
EOF
  echo "🔗 TUIC link generated successfully:"
  cat "$LINK_TXT"
}

# ========== 守护进程 ==========
run_background_loop() {
  echo "🚀 Starting TUIC server..."
  while true; do
    "$TUIC_BIN" -c "$SERVER_TOML" >/dev/null 2>&1 || true
    echo "⚠️ TUIC crashed. Restarting in 5s..."
    sleep 5
  done
}

# ========== 主流程 ==========
main() {
  # 优先处理传入参数以确定端口
  read_port "$@"
  
  if ! load_existing_config; then
    # 如果没有现有配置，使用生成的UUID和密码
    generate_cert
    check_tuic_server
    generate_config
  else
    # 有配置则复用
    generate_cert
    check_tuic_server
  fi

  ip="$(get_server_ip)"
  generate_link "$ip"
  run_background_loop
}

main "$@"
