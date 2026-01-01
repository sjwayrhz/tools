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