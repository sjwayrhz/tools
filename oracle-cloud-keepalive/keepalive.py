import time
import os
import threading
import urllib.request
import urllib.error
import socket  # 新增
from datetime import datetime, timedelta, timezone
# 修改点 1: 引入 ThreadingHTTPServer 实现多线程并发响应
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer

# --- 配置参数 ---
TARGET_CPU = int(os.environ.get('TARGET_CPU_PERCENT', '15')) 
TARGET_MEM_MB = int(os.environ.get('TARGET_MEMORY_MB', '150'))
MONITOR_PORT = 65080

# --- 修改点 2: 设置全局 Socket 超时，防止 urllib read() 永久卡死 ---
socket.setdefaulttimeout(60)

# --- 限速下载配置 ---
LIMIT_SPEED_MB = 2.1
DURATION_MINS = 42
TOTAL_BYTES_TO_DOWNLOAD = int(LIMIT_SPEED_MB * 1024 * 1024 * 60 * DURATION_MINS)
CHUNK_SIZE = 1024 * 512 

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
    
    STATUS['traffic_status'] = "Running"
    # 使用 Cloudflare 10GB 测试文件
    url = "https://speed.cloudflare.com/__down?bytes=10737418240"
    downloaded_in_task = 0
    start_time_global = time.time()
    
    print(f"[{get_shanghai_now()}] 任务开始: 目标 {TOTAL_BYTES_TO_DOWNLOAD/1024/1024:.2f} MB")

    while downloaded_in_task < TOTAL_BYTES_TO_DOWNLOAD:
        if time.time() - start_time_global > (DURATION_MINS * 60 + 13 * 60):
            STATUS['last_run'] = "Finished (Timeout)"
            break

        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=30) as response:
                while downloaded_in_task < TOTAL_BYTES_TO_DOWNLOAD:
                    chunk_start = time.time()
                    try:
                        # 这里的 read 会受到全局 socket.setdefaulttimeout 的保护
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk: break 
                    except Exception:
                        break 

                    downloaded_in_task += len(chunk)
                    
                    # 状态更新
                    progress = (downloaded_in_task / TOTAL_BYTES_TO_DOWNLOAD) * 100
                    elapsed = time.time() - start_time_global
                    avg_speed = (downloaded_in_task / 1024 / 1024) / elapsed if elapsed > 0 else 0
                    STATUS['traffic_status'] = f"Progress: {progress:.1f}% | Avg: {avg_speed:.2f} MB/s"

                    # 精准限速
                    expected_chunk_time = len(chunk) / (LIMIT_SPEED_MB * 1024 * 1024)
                    actual_chunk_time = time.time() - chunk_start
                    
                    if actual_chunk_time < expected_chunk_time:
                        time.sleep(expected_chunk_time - actual_chunk_time)

        except Exception as e:
            print(f"[{get_shanghai_now()}] 连接断开，5秒后重试: {str(e)}")
            time.sleep(5)
            continue
    
    STATUS['traffic_status'] = "Idle"
    STATUS['last_run'] = get_shanghai_now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{get_shanghai_now()}] 任务结束")

# --- 调度逻辑 ---
def scheduler_thread():
    last_hour = -1
    print("调度器已启动 (00:00-05:00 UTC+8)...")
    while True:
        sh_now = get_shanghai_now()
        STATUS['shanghai_time'] = sh_now.strftime('%H:%M:%S')
        
        if 0 <= sh_now.hour <= 4:
            if sh_now.hour != last_hour:
                threading.Thread(target=run_traffic_task, daemon=True).start()
                last_hour = sh_now.hour
        else:
            last_hour = -1
            
        time.sleep(30)

# --- CPU 逻辑 ---
def cpu_stress_thread():
    period = 0.1
    if TARGET_CPU <= 0: return
    
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
        try:
            res = (
                f"Oracle Keepalive Monitor (v3.1 Fix)\n"
                f"--------------------------------------------\n"
                f"Current Shanghai Time : {STATUS['shanghai_time']}\n"
                f"Traffic Status        : {STATUS['traffic_status']}\n"
                f"Last Task Finished    : {STATUS['last_run']}\n"
                f"Target Specs          : {DURATION_MINS} mins @ {LIMIT_SPEED_MB} MB/s\n"
                f"Memory Alloc          : {STATUS['memory']}\n"
            )
            self.wfile.write(res.encode('utf-8'))
        except: pass
    def log_message(self, format, *args): pass

if __name__ == "__main__":
    # 内存分配放在 try 块中更安全地处理
    try:
        if TARGET_MEM_MB > 0:
            print(f"正在分配 {TARGET_MEM_MB}MB 内存...")
            _data = bytearray(TARGET_MEM_MB * 1024 * 1024)
            STATUS['memory'] = f"Allocated {TARGET_MEM_MB}MB"
            print("内存分配完成")
    except Exception as e: 
        STATUS['memory'] = f"Alloc Error: {str(e)}"
        print(f"内存分配失败: {e}")

    # 修改点 3: 使用 ThreadingHTTPServer
    # 这样即使有一个连接卡死（比如 Keep-Alive），其他连接（如 curl）也能正常访问
    try:
        server = ThreadingHTTPServer(('0.0.0.0', MONITOR_PORT), StatusHandler)
    except NameError:
        # 兼容旧版本 Python (虽然甲骨文通常是新版)
        import socketserver
        class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer): pass
        server = ThreadingHTTPServer(('0.0.0.0', MONITOR_PORT), StatusHandler)

    threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Thread(target=scheduler_thread, daemon=True).start()
    threading.Thread(target=cpu_stress_thread, daemon=True).start()
    
    print(f"脚本已启动 (多线程模式)。Monitor Port: {MONITOR_PORT}")
    while True:
        time.sleep(3600)