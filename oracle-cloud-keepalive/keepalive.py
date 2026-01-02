import time
import os
import threading
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 配置参数 ---
TARGET_CPU = int(os.environ.get('TARGET_CPU_PERCENT', '15'))
TARGET_MEM_MB = int(os.environ.get('TARGET_MEMORY_MB', '150'))
MONITOR_PORT = 65080

# --- 限速下载配置 ---
LIMIT_SPEED_MB = 2.1  # 限制速度 2.1 MB/s
DURATION_MINS = 42    # 持续时间 42 分钟
# 每次任务下载总字节数 (2.1MB * 60s * 42min)
TOTAL_BYTES_TO_DOWNLOAD = int(LIMIT_SPEED_MB * 1024 * 1024 * 60 * DURATION_MINS)
CHUNK_SIZE = 1024 * 64 # 64KB 块大小，便于精准限速

STATUS = {
    "memory": "Initializing...",
    "traffic_status": "Idle",
    "last_run": "None",
    "shanghai_time": ""
}

def get_shanghai_now():
    tz_sh = timezone(timedelta(hours=8))
    return datetime.now(timezone.utc).astimezone(tz_sh)

# --- 限速下载核心逻辑 ---
def run_traffic_task():
    if STATUS['traffic_status'] != "Idle":
        return
    
    STATUS['traffic_status'] = "Running (Limited 2.1MB/s)"
    # 使用 Cloudflare 的大文件接口，反复请求直到达到目标字节数
    url = "https://speed.cloudflare.com/__down?bytes=1073741824" # 1GB 每次
    downloaded_in_task = 0
    
    try:
        start_time = time.time()
        while downloaded_in_task < TOTAL_BYTES_TO_DOWNLOAD:
            with urllib.request.urlopen(url, timeout=60) as response:
                while downloaded_in_task < TOTAL_BYTES_TO_DOWNLOAD:
                    chunk_start = time.time()
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk: break
                    
                    downloaded_in_task += len(chunk)
                    
                    # 进度更新
                    progress = (downloaded_in_task / TOTAL_BYTES_TO_DOWNLOAD) * 100
                    STATUS['traffic_status'] = f"Downloading: {progress:.1f}% (@2.1MB/s)"
                    
                    # --- 精准限速逻辑 ---
                    # 计算下载这么多数据理应花费的时间
                    expected_time = len(chunk) / (LIMIT_SPEED_MB * 1024 * 1024)
                    actual_time = time.time() - chunk_start
                    if actual_time < expected_time:
                        time.sleep(expected_time - actual_time)
            
        STATUS['last_run'] = get_shanghai_now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        STATUS['last_run'] = f"Error: {str(e)}"
    finally:
        STATUS['traffic_status'] = "Idle"

# --- 调度逻辑 ---
def scheduler_thread():
    last_hour = -1
    while True:
        sh_now = get_shanghai_now()
        STATUS['shanghai_time'] = sh_now.strftime('%H:%M:%S')
        
        # 上海时间 0-4 点触发
        if 0 <= sh_now.hour <= 4:
            if sh_now.hour != last_hour:
                threading.Thread(target=run_traffic_task, daemon=True).start()
                last_hour = sh_now.hour
        else:
            last_hour = -1
            
        time.sleep(30)

# --- CPU & Web 逻辑 (同上) ---
def cpu_stress_thread():
    period = 0.1
    work_time = period * (TARGET_CPU / 100.0)
    sleep_time = period - work_time
    while True:
        start = time.time()
        while time.time() - start < work_time:
            _ = 1024 * 1024
        time.sleep(max(0, sleep_time))

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        res = (
            f"Oracle Keepalive Monitor (2.1MB/s Limited)\n"
            f"--------------------------------------------\n"
            f"Current Shanghai Time : {STATUS['shanghai_time']}\n"
            f"Traffic Status        : {STATUS['traffic_status']}\n"
            f"Last Task Finished    : {STATUS['last_run']}\n"
            f"Target Duration       : {DURATION_MINS} mins per hour\n"
            f"Daily Total Traffic   : ~25.8 GB\n"
        )
        self.wfile.write(res.encode('utf-8'))
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    try:
        _data = bytearray(TARGET_MEM_MB * 1024 * 1024)
        STATUS['memory'] = "OK"
    except: pass

    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', MONITOR_PORT), StatusHandler).serve_forever(), daemon=True).start()
    threading.Thread(target=scheduler_thread, daemon=True).start()
    threading.Thread(target=cpu_stress_thread, daemon=True).start()
    
    print(f"脚本已启动。每天上海时间 0-5 点将执行 5 次，每次 42 分钟限速下载。")
    while True:
        time.sleep(3600)