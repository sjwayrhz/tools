import time
import os
import threading
import math
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 全局变量用于状态监控 ---
STATUS = {
    "memory": "Not Allocated",
    "cpu": "Running",
    "traffic": "Idle"
}

# --- HTTP 处理类 (用于监控查看) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            # 构建返回内容，增加了 Schedule 的展示
            response_text = (
                f"Keepalive Running.\n"
                f"Memory Status: {STATUS['memory']}\n"
                f"CPU Status: {STATUS['cpu']}\n"
                f"Traffic Status: {STATUS['traffic']}\n"
                f"Schedule: Daily 00:00 - 05:00 (CST)\n"
                f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.wfile.write(response_text.encode('utf-8'))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass

# --- 流量下载任务 (凌晨保活) ---
def download_traffic_job():
    # target_url = "https://officecdn.microsoft.com/db/492350f6-3a01-4f97-b9c0-c7c6ddf67d60/media/zh-cn/ProPlus2024Retail.img" # v1.3下载Office 2024 ISO 镜像
    target_url = "https://speed.cloudflare.com/__down?bytes=5368709120"  # v1.4 下载cloudflare 5GB测试文件
    rate_limit = "2.1M" 

    print(f"[{datetime.now()}] 🚀 启动凌晨流量保活任务 (Office 2024 ISO)...")
    STATUS['traffic'] = f"Downloading at {rate_limit}..."

    try:
        # -O /dev/null 直接丢弃不占空间
        cmd = ["wget", f"--limit-rate={rate_limit}", "-O", "/dev/null", target_url]
        subprocess.run(cmd, check=True)
        print(f"[{datetime.now()}] ✅ 任务完成。")
        STATUS['traffic'] = "Last task completed successfully"
    except Exception as e:
        print(f"[{datetime.now()}] ❌ 任务失败: {e}")
        STATUS['traffic'] = f"Failed: {e}"

# --- 定时器线程逻辑 ---
def scheduler_loop():
    print("⏰ 定时任务监控线程已启动 (目标: 00:00-04:59)")
    while True:
        now = datetime.now()
        # 凌晨 0, 1, 2, 3, 4 点的 00 分触发
        if now.hour in [0, 1, 2, 3, 4] and now.minute == 0:
            download_traffic_job()
            time.sleep(65) # 避开重复触发

        time.sleep(30) # 每 30 秒核对一次时间

def start_web_server(port=65080):
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"HTTP Monitor started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start web server: {e}")

def run_keepalive():
    print("Starting Oracle Cloud Keepalive Service...")
    
    # 1. 启动 Web 监控线程
    web_thread = threading.Thread(target=start_web_server, args=(65080,))
    web_thread.daemon = True
    web_thread.start()

    # 2. 启动定时器线程
    traffic_thread = threading.Thread(target=scheduler_loop)
    traffic_thread.daemon = True
    traffic_thread.start()

    # --- 获取环境变量参数 ---
    try:
        cpu_target_env = int(os.environ.get('TARGET_CPU_PERCENT', '15'))
        global_target = cpu_target_env / 100.0
    except:
        global_target = 0.15
        cpu_target_env = 15

    try:
        memory_mb_env = int(os.environ.get('TARGET_MEMORY_MB', '150'))
    except:
        memory_mb_env = 150

    STATUS['cpu'] = f"Running (Target: {cpu_target_env}%)"

    # 3. 执行内存占用 (修复 0MB 报错逻辑)
    if memory_mb_env > 0:
        try:
            print(f"Allocating {memory_mb_env}MB Memory...")
            memory_hog = bytearray(memory_mb_env * 1024 * 1024)
            if len(memory_hog) > 0:
                memory_hog[0] = 1
            STATUS['memory'] = f"Allocated ({memory_mb_env}MB)"
            print("Memory Allocated Successfully.")
        except Exception as e:
            STATUS['memory'] = f"Failed: {e}"
            print(f"Memory Allocation Failed: {e}")
    else:
        STATUS['memory'] = "Disabled (0MB)"
        print("Memory allocation skipped.")

    # 4. CPU 周期占用 (主循环)
    print(f"Starting CPU cycle (Target: {cpu_target_env}%)...")
    import math
    cycle_total = 0.1
    
    while True:
        cycle_start = time.time()
        active_load = 0.35 + 0.15 * math.sin(cycle_start)
        work_quantum = cycle_total * global_target
        active_duration = work_quantum / active_load
        
        param_slice = 0.01
        if active_duration < param_slice:
             param_slice = active_duration
             
        elapsed_active = 0
        while elapsed_active < active_duration:
            slice_start = time.time()
            current_slice_work = param_slice * active_load
            current_slice_sleep = param_slice * (1 - active_load)
            
            t0 = time.time()
            while time.time() - t0 < current_slice_work:
                _ = 123 * 456
                
            if current_slice_sleep > 0.001:
                time.sleep(current_slice_sleep)
                
            elapsed_active = time.time() - cycle_start
            if elapsed_active >= active_duration:
                break
        
        elapsed_total = time.time() - cycle_start
        sleep_remainder = cycle_total - elapsed_total
        if sleep_remainder > 0.001:
            time.sleep(sleep_remainder)

if __name__ == "__main__":
    run_keepalive()