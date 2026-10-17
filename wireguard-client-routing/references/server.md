# 服务器核查与最小修复

## 接入与实例绑定

先读项目本地连接指引，记录预期/实际账号、profile、认证来源、region、实例 ARN/名称、IP、接口与 checked_at。真实地址、账号和凭据路径留本地，公共 Skill 只写通用方法。同名实例按区域和 ARN 区分；实例 IP 变化先核新旧绑定。

云 API 命令显式传 profile 和 region。执行前将变量绑定到本任务实际值，核对返回的账号、ARN、location 与目标一致。

```sh
aws --profile "$WG_AWS_PROFILE" --region "$WG_AWS_REGION" sts get-caller-identity
aws --profile "$WG_AWS_PROFILE" --region "$WG_AWS_REGION" lightsail get-instance \
  --instance-name "$WG_AWS_INSTANCE" \
  --query 'instance.{name:name,arn:arn,region:location.regionName,ip:publicIpAddress,username:username,sshKeyName:sshKeyName}'
```

CLI/API、控制台和 SSH 分别记录状态。CLI 过期时，已有有效密钥与可信 host key 的 SSH 可继续获准的只读检查，云防火墙等 API 项保留 pending；离线生成继续。区分过期、AccessDenied、错 region/资源缺失、网络失败与时钟偏差。未知接管或退出原因直接记未知。

恢复入口按实际认证来源选择。console-credentials 使用 `aws login --profile …`，IAM Identity Center 使用 `aws sso login --profile …`；assume-role/credential_process 恢复其来源。沿用当前操作授权，保留其他登录会话、缓存和默认配置。仅需用户完成的真实登录步骤暂停相应入口。

Lightsail 临时 SSH 访问通过 `get-instance-access-details` 获取，显式 region/profile。响应直接存任务专用 0700 目录，私钥与证书文件 0600；禁止打印完整响应。成对保存 `privateKey`、`certKey`，核对 username/IP/instanceName 和 `expiresAt`，连接时指定私钥及 `CertificateFile`。测试和清理都预留有效期，到期恢复原入口。结束后只清理本任务临时凭据。

host key 使用既有可信记录或已认证云入口核验的指纹，记录来源与时间，保持 `StrictHostKeyChecking=yes`。`ssh-keyscan` 结果须另行核验；换 IP 沿用 HostKeyAlias 前确认同一实例。host key 不符时暂停该连接并核对，其他独立工作继续。

依据 [AWS CLI 登录](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sign-in.html)、[IAM Identity Center](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)、[Lightsail 实例查询](https://docs.aws.amazon.com/cli/latest/reference/lightsail/get-instance.html)、[临时访问字段](https://docs.aws.amazon.com/lightsail/2016-11-28/api-reference/API_InstanceAccessDetails.html)、[OpenSSH 配置](https://man.openbsd.org/OpenBSD-7.6/ssh_config.5)。

## 只读基线

按上节绑定目标并选择可用入口；浏览器场景遵守当前浏览器 Skill 的 Space、标签占用与清理要求。记录实例运行状态、静态 IP、系统与内核、WireGuard 接口、UDP 端口、云防火墙和主机防火墙。

通过既有 SSH 或浏览器终端执行安全字段查询。将 `<if>` 换成已确认接口名。

```sh
systemctl is-active wg-quick@<if>
systemctl is-enabled wg-quick@<if>
wg show <if> public-key
wg show <if> listen-port
wg show <if> peers
wg show <if> allowed-ips
wg show <if> latest-handshakes
wg show <if> transfer
ip -4 address show dev <if>
ip -4 route
ip -6 address
ip -6 route
sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding
ss -lun
```

`wg show ... dump`、`showconf`、整个服务端配置和整个客户端文件可能包含私钥，不能输出到普通日志。只读取本题需要的公钥、地址、规则、服务状态与计数；读取客户端私钥生成文件时在程序内处理，不打印。

## 核对链路

- 每台设备独立 peer，服务端 AllowedIPs 对应其唯一 IPv4 `/32`，客户端服务端公钥和 UDP 端点匹配。
- 云端 UDP 入站、主机 INPUT、WireGuard 解密流量的 FORWARD、回包规则、实际公网出接口、MASQUERADE 和计数共同核对。优先读取实际使用的 nftables 或 iptables 规则及加载脚本，考虑顺序和重复规则。
- `net.ipv4.ip_forward=1` 同时具备持久配置。客户端 DNS 若指向隧道网关，确认该地址真的监听 DNS，并有对应 INPUT 放行；否则使用已验证的隧道外/隧道内公共 DNS。
- 区分 EC2 NAT 实例和 Lightsail。只在确属 EC2 转发角色且当前检查需要时处理 source/destination check，不能机械套用其他服务命令。
- 无新握手可由设备未启动造成。需要实际请求与握手、计数变化才能判断是否连通；UDP 端口探测或服务 active 只能证明局部状态。

## 已授权修复

先保存受影响配置与规则的权限受限备份，列出最小差异、回滚命令和失联恢复路径。保留实例、IP、密钥、地址、MTU、keepalive、其他 peer 与无关规则。

修复范围由当前用户要求和已确认问题决定。常见项目包括转发、NAT、持久化或 IPv6 不一致；不清空整套防火墙。配置生成任务无需重启服务。确需重载时按当前授权执行，并立即检查接口、peer、现存连接、转发/NAT 计数及启动加载路径。

临时 peer 的添加、正式 peer 的删除重建、时间调整和运行态 `wg set` 都记录为写操作。文件哈希不变时仍需记录运行态动作、握手/endpoint 及影响。测试身份优先使用已获准的独立 peer，跨主机复用和时钟检查按 [验证合同](validation.md) 执行。

换 IP、端口或实例前，列出同机代理、Web 服务、回调和既有连接入口，核对当前授权及费用范围，保存原值、恢复入口和回滚步骤。完成后回读受影响依赖；服务的观察时间与启动时间分别记录，原因不明就保留未知。

本 Skill 的生成器采用 IPv4-only。服务端有完整双栈需求时，先另行确定 IPv6 地址、转发、云路由、出口和防火墙方案，再调整实现。不能只添加 `::/0` 让未配置的服务端承接 IPv6。

参考 [WireGuard 快速入门](https://www.wireguard.com/quickstart/)、[wg-quick 手册](https://man7.org/linux/man-pages/man8/wg-quick.8.html)、[AWS Lightsail 防火墙](https://docs.aws.amazon.com/lightsail/latest/userguide/understanding-firewall-and-port-mappings-in-amazon-lightsail.html)。
