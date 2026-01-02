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
```
docker run -d \
  --name ubuntu-tunnel \
  -e CLOUDFLARE_TUNNEL_TOKEN="eyJhIjoiYjE5OTY2YmVjODMzMTEyZGZjY2JjNjAyYzkyM2NmY2YiLCJ0IjoiMGNiNzBjOGItMGM1Zi00YjQ2LTk3OTYtYzU4MzJjOTBjZDZmIiwicyI6IlpUVTFPV05rTVRFdFpXWm1PQzAwWVdSa0xXSTRPRE10WlRFMVpUSm1NemMwTW1WaiJ9" \
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