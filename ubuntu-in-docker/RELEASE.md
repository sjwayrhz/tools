## 抖音录制视频并定时推送到youtube
镜像名称 `sjwayrhz/ubuntu:tunnel-ssha-douyin`
```
docker run -d \
  -v /usr/local/share/downloads:/root/DouyinLiveRecorder/downloads \
  sjwayrhz/ubuntu:tunnel-ssha-douyin
```
启动之后， 
```
ssh ssha
docker exec -it xxx bash
```
在容器内部执行
```
cron
!86
```
第86行历史记录是
```
nohup python3 -u main.py > output.log 2>&1 &
```
会将水水家猪蹄的抖音直播间的内容每天录制并推送到sjwayrhz的youtube频道

## 语音聊天平台 matrix synapase
镜像名称`sjwayrhz/ubuntu:tunnel-sshb-matrix`  
启动方法
```bash
docker run -d \
  --name ubuntu-tunnel \
  -e CLOUDFLARE_TUNNEL_TOKEN="eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiZmQ0NjNhNmMtMWJiOS00Nzk2LTgwZDItYWY0NjM2MmJjZDhhIiwicyI6Ik1tSmpNbU00WlRVdFpXVTJOQzAwTURjd0xUa3lZemd0Tnpaak1URmxOVGhtWldJMiJ9" \
  sjwayrhz/ubuntu:tunnel-sshb-matrix
```
进入容器
```bash
# 启动matrix-synapse
/opt/venvs/matrix-synapse/bin/synctl start /etc/matrix-synapse/homeserver.yaml

# 启动ntfy
nohup ntfy serve -c /etc/ntfy/server.yml > /var/log/ntfy.log 2>&1 &
```
然后可以使用element客户端登录了，用户`admin/admin`

启动另外两个tunnel
```bash
nohup cloudflared tunnel run --token eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiNDQ5OTY0YzAtYjhkZC00NDJlLTgzNmYtYTBjYmM4OWY0YWNjIiwicyI6IlpqaG1NREE1WVdJdE0yUXdaaTAwT0RreUxUaG1ZamN0WVdKbU5tSmlNbUkxT0dOaCJ9 > /var/log/cloudflared.log 2>&1 &
nohup cloudflared tunnel run --token eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiMmU1MDA0NmQtZDExMi00MjEwLWJlNjgtYWRmNTFmMDdiM2Y0IiwicyI6IlpUYzFNVEF6TXpjdFl6UmtOaTAwWkRobUxXSmtNVFV0T1RCbE1qVXpaakZtWXpVeiJ9 > /var/log/cloudflared.log 2>&1 &
```
检测一下
```bash
ps -ef | grep cloudfl
root          10       1  1 07:15 ?        00:00:03 cloudflared tunnel run --token eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiZmQ0NjNhNmMtMWJiOS00Nzk2LTgwZDItYWY0NjM2MmJjZDhhIiwicyI6Ik1tSmpNbU00WlRVdFpXVTJOQzAwTURjd0xUa3lZemd0Tnpaak1URmxOVGhtWldJMiJ9
root          78      65  2 07:18 pts/1    00:00:00 cloudflared tunnel run --token eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiNDQ5OTY0YzAtYjhkZC00NDJlLTgzNmYtYTBjYmM4OWY0YWNjIiwicyI6IlpqaG1NREE1WVdJdE0yUXdaaTAwT0RreUxUaG1ZamN0WVdKbU5tSmlNbUkxT0dOaCJ9
root          86      65  2 07:18 pts/1    00:00:00 cloudflared tunnel run --token eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiMmU1MDA0NmQtZDExMi00MjEwLWJlNjgtYWRmNTFmMDdiM2Y0IiwicyI6IlpUYzFNVEF6TXpjdFl6UmtOaTAwWkRobUxXSmtNVFV0T1RCbE1qVXpaakZtWXpVeiJ9
root          97      65 40 07:18 pts/1    00:00:00 grep --color=auto cloudfl
```