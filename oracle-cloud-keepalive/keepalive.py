import time
import os

def run_keepalive():
    print("Starting Oracle Cloud Keepalive...")
    
    # --- 内存占用部分 ---
    # 申请 150MB 的内存 (150 * 1024 * 1024 字节)
    # 使用 bytearray 会在物理内存中实际分配，而不仅仅是虚拟内存
    try:
        print("Allocating 150MB Memory...")
        memory_hog = bytearray(150 * 1024 * 1024) 
        # 简单读写一次确保内存被操作系统实际划拨(Page Fault)
        memory_hog[0] = 1 
        print("Memory Allocated Successfully.")
    except Exception as e:
        print(f"Memory Allocation Failed: {e}")

    # --- CPU 占用部分 ---
    # 目标：15% CPU 利用率
    # 策略：总周期 0.1 秒
    # 工作：0.015 秒
    # 睡眠：0.085 秒
    print("Starting CPU cycle (Target: 15%)...")
    
    work_duration = 0.015
    sleep_duration = 0.085
    
    while True:
        start_time = time.time()
        # 持续进行简单的数学运算直到达到工作时长
        while time.time() - start_time < work_duration:
            _ = 123 * 456
        
        # 休息剩余时间
        time.sleep(sleep_duration)

if __name__ == "__main__":
    run_keepalive()