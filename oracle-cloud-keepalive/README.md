# 0. 快速启动
```
docker run -d -p 65080:65080 --name oracle-keepalive --restart always sjwayrhz/oracle-alive:latest
```
# 1. 构建镜像（命名为 oracle-alive）

```
docker build -t sjwayrhz/oracle-alive:latest .
```

# 2. 删除旧容器（如果有）并启动新容器

```
docker rm -f oracle-keepalive 2>/dev/null
docker run -d --name oracle-keepalive --restart always sjwayrhz/oracle-alive:latest
```

# 验证方法

容器启动后，等待 10 秒钟，然后检查：

1. 确认进程在跑：

```
docker logs oracle-keepalive
```

2. 查看资源占用：

```
docker stats
```

CPU %: 应该在 14% - 16% 之间跳动。  
MEM USAGE: 应该稳定在 150MiB - 160MiB。  
这个脚本非常温和，内存只占坑不干活（不耗 CPU），CPU 循环非常短（0.1秒），所以在 top 里看起来会非常平稳，不会出现之前 stress-ng 那种暴涨暴跌的情况。
