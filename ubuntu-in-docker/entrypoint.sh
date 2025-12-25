#!/bin/bash
set -e

echo "Starting SSH Daemon..."
# Start SSH in the background
/usr/sbin/sshd

echo "Starting Cloudflare Tunnel..."

# Check if CLOUDFLARE_TUNNEL_TOKEN is set
if [ -z "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
    echo "Error: CLOUDFLARE_TUNNEL_TOKEN environment variable is not set"
    echo "Please run the container with: docker run -e CLOUDFLARE_TUNNEL_TOKEN=your_token_here ..."
    exit 1
fi

# Run cloudflared directly with the token from environment variable
# This is preferred over 'service install' in Docker as we want the process to run in the foreground (or be managed here)
# and we don't have systemd in a standard container.
cloudflared tunnel run --token "$CLOUDFLARE_TUNNEL_TOKEN"