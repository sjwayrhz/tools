# 描述

这是制作docker镜像在koyeb网站上可以搭建vmess的脚本  

## uuid

这个版本的tag是

```
sjwayrhz/xray:vmess
```

容器默认暴露的端口是8000<HTTP>

这个版本在启动的的时候如果没有设置UUID，则UUID数值是

```
de0e9792-7c33-4f1f-a586-7a8927894982
```

如果想设置自己的UUID，可以设置环境变量

```
UUID_PLACEHOLDER: your_uuid
```

## 配置

这里以不设置uuid举例子

```
别名： 任意取
地址： koyeb面板上的URL
端口： 443
ID ： de0e9792-7c33-4f1f-a586-7a8927894982
alterid： 0 
security: auto
network: ws
type: none
path: /ws
传输层安全： tls
allowinscure: false
```
