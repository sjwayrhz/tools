import time
import os
import threading
import subprocess
import math
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 配置参数 (可以通过环境变量修改) ---
# 建议保活设置：CPU 10-15%, 内存 100-150MB 即可满足甲骨文保活要求
TARGET_CPU = int(os.environ.get('TARGET_CPU_PERCENT', '12')) 
TARGET_MEM_MB = int(os.environ.get('TARGET_MEMORY_MB', '128'))
MONITOR_PORT = 65080

STATUS = {
    "memory": "Not Allocated",
    "cpu": f"Target: {TARGET_CPU}%",
    "traffic": "Idle"
}
traffic_lock = threading.Lock()

# --- HTTP 监控 (网页查看状态) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            res = (
                f"Oracle Cloud Keepalive Monitor\n"
                f"----------------------------\n"
                f"Memory Status  : {STATUS['memory']}\n"
                f"CPU Status     : {STATUS['cpu']}\n"
                f"Traffic Status : {STATUS['traffic']}\n"
                f"Current Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            self.wfile.write(res.encode('utf-8'))
    def log_message(self, format, *args): pass

# --- 流量下载任务 (防止流量被判定为 0) ---
def download_traffic_job():
    if not traffic_lock.acquire(blocking=False):
        return
    try:
        # 限速 1.0M，防止抢占 rclone 带宽
        target_url = "https://speed.cloudflare.com/__down?bytes=104857600" 
        rate_limit = "1.0M" 
        total_segments = 10 # 约 1GB 流量
        for i in range(total_segments):
            STATUS['traffic'] = f"Downloading: {i+1}/{total_segments} (@{rate_limit})"
            cmd = ["wget", f"--limit-rate={rate_limit}", "--tries=2", "-q", "-O", "/dev/null", target_url]
            subprocess.run(cmd)
            time.sleep(10)
    finally:
        traffic_lock.release()
        STATUS['traffic'] = "Idle"

# --- 核心 CPU 占用逻辑 (修复 100% 占用问题) ---
def cpu_stress_task():
    print(f"CPU Stress started: Target {TARGET_CPU}%")
    target_fraction = TARGET_CPU / 100.0
    period = 0.1 # 每 0.1 秒为一个循环周期
    
    while True:
        start_time = time.time()
        # 工作阶段：执行计算直到达到预定时间点
        work_duration = period * target_fraction
        while (time.time() - start_time) < work_duration:
            # 轻量级计算，不产生大量内存垃圾
            _ = 1024 * 1024 
            
        # 休眠阶段：释放 CPU 给系统其他进程 (如 rclone)
        elapsed = time.time() - start_time
        sleep_time = period - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

# --- 定时器 ---
def scheduler_loop():
    while True:
        now = datetime.now()
        # 仅在凌晨执行流量任务，避开白天上传视频的高峰
        if now.hour == 2 and now.minute == 0:
            threading.Thread(target=download_traffic_job, daemon=True).start()
            time.sleep(65)
        time.sleep(30)

if __name__ == "__main__":
    print(f"Starting Oracle Cloud Keepalive Service on 1GB RAM Machine...")

    # 1. 分配内存 (一次性分配，保持稳定)
    try:
        if TARGET_MEM_MB > 0:
            dummy_data = bytearray(TARGET_MEM_MB * 1024 * 1024)
            for i in range(0, len(dummy_data), 4096): # 确保物理内存被映射
                dummy_data[i] = 1
            STATUS['memory'] = f"Allocated {TARGET_MEM_MB}MB"
    except Exception as e:
        STATUS['memory'] = f"Error: {e}"

    # 2. 启动监控
    server = threading.Thread(target=lambda: HTTPServer(('0.0.0.0', MONITOR_PORT), HealthCheckHandler).serve_forever(), daemon=True)
    server.start()

    # 3. 启动定时器
    threading.Thread(target=scheduler_loop, daemon=True).start()

    # 4. 运行 CPU 任务 (主线程运行)
    cpu_stress_task()