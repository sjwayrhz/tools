# 0. 免费vps地址

<https://betadash.lunes.host/>

但是每15天需要登录一下面板

创建hy2用如下命令,将port替换为所指定的端口，默认是65443

```
curl -Ls https://raw.githubusercontent.com/sjwayrhz/tuic-hy2/refs/heads/main/hy2.sh | sed 's/\r$//' | bash -s -- $port
```

创建tuic用如下命令,将port替换为所指定的端口，默认是65442

```
curl -Ls https://raw.githubusercontent.com/sjwayrhz/tuic-hy2/refs/heads/main/tuic.sh | sed 's/\r$//' | bash -s -- $port
```
