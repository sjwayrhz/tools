# docker镜像
存入dockerhub的镜像是  
```
sjwayrhz/xray:vless
```
容器需要暴露端口 8000 <TCP>

# 客户端配置 (填入 v2rayN)

请在 v2rayN 中添加 VLESS 服务器，并严格按照以下信息填写：

```
Protocol: vless
Address: 01.proxy.koyeb.app
Port: 17578
UUID: 0447f7f3-64af-4da7-8d4e-dee5ba37cb15
Flow: xtls-rprx-vision
Network: tcp
TLS_Type: reality
SNI: www.apple.com
Fingerprint: chrome
PublicKey: jcdABKj-F4CRruC-5VR0Y53C2yIEdSq-bd_Ay79-3VM
ShortId: 62
SpiderX: (None/留空)
Mldsa65Verify: (None/留空)
```

其中这是x25519的私钥和公钥

```
私钥: EI78_-w1gk6SC-MgT9S5qTVO4H3r2Ly8L5_y1htD42E
公钥: jcdABKj-F4CRruC-5VR0Y53C2yIEdSq-bd_Ay79-3VM
```

举个例子

```

vless://0447f7f3-64af-4da7-8d4e-dee5ba37cb15@01.proxy.koyeb.app:17578?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.apple.com&fp=chrome&pbk=jcdABKj-F4CRruC-5VR0Y53C2yIEdSq-bd_Ay79-3VM&sid=62&type=tcp&headerType=none#Koyeb-Final

```

# 保活方案 (在 root@dynamic 机器上)

这是为了防止 Koyeb 容器因 300 秒无流量而休眠。我们使用 nc 命令，因为它最稳定且极其节省流量。

操作步骤：

- 连接到你的 Linux 机器 (root@dynamic)。

- 输入 crontab -e 进入编辑模式。

- 在文件末尾添加下面这一行（每 4 分钟执行一次）

```

*/4* ** * nc -zv 01.proxy.koyeb.app 17578 > /dev/null 2>&1

```

- 保存并退出。

效果： 只要这台 Linux 机器开着，它就会全自动帮你的 Koyeb 容器“续命”。

# 两种检测方式的区别与用途

## TCP 检测 (nc -zv ...) —— 推荐用于自动保活

命令： `nc -zv 01.proxy.koyeb.app 17578`

原理： 只进行 TCP 三次握手，确认端口通畅后立刻断开。

优点： * 忽略证书错误：不管证书对不对，只要路通了就显 succeeded!。

极速：毫秒级完成，不占用服务器处理资源。

结论： 写在 Crontab 里用这个，最稳。

## 域名访问 (浏览器/Curl) —— 用于验证伪装 (Fallback)

操作： 浏览器打开 <https://01.proxy.koyeb.app:17578>

现象：

如果配置了 Reality 且无 Fallback： 浏览器报“证书错误 (Cert Invalid)”，这是正常的。

如果配置了 Fallback 到 Caddy： 你可能会看到证书错误（因为 SNI 不匹配），但如果你忽略错误继续访问，或者通过 HTTP 访问，你应该能看到 Service is Alive! 的文字。

结论： 这是给人看的，用来测试你的回落配置是否生效。 如果你能上网，且 nc 能通，平时根本不需要去刷这个网页。
