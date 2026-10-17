# 客户端导入与 IPv6

## 版本与活动配置

每设备记录目标 App/壳版本、实际 core 版本/哈希/构建标签、最终合并配置哈希和核对时间。文件目录中的最新版本仅为候选；实际采用状态需设备读回，未知记 `active_device_unknown`。现有可用设备保留原配置，只处理本次受影响端。

WG 节点 `ip-stack` 控制出站用户态栈，顶层 `tun.stack` 控制流量接管，服务端 TCP 拥塞控制另属一层。核心默认和字段能力按精确版本核实，`-t` 通过后还需确认相关字段在实际构造路径生效。例如 [Mihomo v1.19.29](https://github.com/MetaCubeX/mihomo/blob/v1.19.29/adapter/outbound/wireguard.go) 与 [v1.19.32](https://github.com/MetaCubeX/mihomo/blob/v1.19.32/adapter/outbound/wireguard.go) 的 WG 栈选择不同。两版本的节点远程 DNS resolver 都有显式条件，省略 `remote-dns-resolve` 本身不足以判定重复解析。

版本能力未确认时保留兼容基线，把新参数列为待验候选。当前生成器参数和输出仍以 [生成合同](generation.md) 为准；本节不新增生成器接口。诊断中只改变有证据指向的变量，BBR3 收益记录其平台/版本/窗口，不扩为全客户端默认。

## Android

目标为 [Clash Meta for Android 官方项目](https://github.com/MetaCubeX/ClashMetaForAndroid/releases)，简称 CMFA。先核对设备和版本，从本地文件导入 `android-mihomo.yaml`、保存并选为当前配置，保持规则模式。

停止服务后检查应用的网络设置，再启动并接受 Android VPN 授权。

- 开启“路由系统流量”，访问控制选“所有应用”。
- 关闭“允许绕过”和“允许 IPv6”，保持 DNS 劫持开启。
- 记录 Android 私人 DNS 模式、解析器及实际 DNS 路径。有可复现干扰时，在已授权目标设备临时 A/B 并恢复原值；没有干扰证据就保留设置。
- 确认需要走代理的应用未在绕过名单，避免与其他 VPN 同时占用系统 VPN 槽位。

上述独立开关见官方 [NetworkSettingsDesign.kt](https://github.com/MetaCubeX/ClashMetaForAndroid/blob/main/design/src/main/java/com/github/kr328/clash/design/NetworkSettingsDesign.kt)。默认值按目标版本对应源码与应用实际值核对。[ServiceStore.kt](https://github.com/MetaCubeX/ClashMetaForAndroid/blob/main/service/src/main/java/com/github/kr328/clash/service/store/ServiceStore.kt)

Android YAML 不含桌面 `tun` 块、物理网卡名和进程路径规则。CMFA 用自己的 [VpnService](https://github.com/MetaCubeX/ClashMetaForAndroid/blob/main/service/src/main/java/com/github/kr328/clash/service/TunService.kt) 管理隧道。顶层和 DNS 的 `ipv6: false` 分别限制内核与 AAAA 响应；手机 VPN 范围还由应用设置决定。

根据当前 CMFA 源码与 [Android Builder 合同](https://developer.android.com/reference/android/net/VpnService.Builder)，禁用 IPv6 时未加入该地址族的地址/路由/DNS，且未调用 allowFamily，可推断 VPN 接管的应用会被 Android 阻断 IPv6。排除应用和允许绕过会改变覆盖范围。实际手机结果需现场验证，桌面内核测试不代替它。

## Windows 和 macOS

导入对应完整 YAML，选中配置，规则模式。核对当前混合端口、服务/TUN 权限、系统代理和配置合并脚本；检查最终运行配置，防止 GUI 或全局脚本覆盖 DNS、规则或节点。

生成器为 macOS 提供 gVisor TUN，为 Windows 提供 mixed TUN 与 strict-route。先验证环境兼容，再授权应用到当前连接。隔离内核测试时禁用 TUN、使用独立端口和临时目录，并指定真实物理出口避免套入当前 TUN。

保留用户已确认的 `ipv6: false` 与 `dns.ipv6: false`。这两个开关及首条 IPv6 REJECT 只约束客户端接管流量；系统其他出口需另看路由。不要为统一配置重新开启曾导致问题的 IPv6。

DNS 使用国内解析器处理国内域名和明确 DIRECT 例外，海外解析经 WireGuard。`direct-nameserver-follow-policy: true` 保证 LAN/local 的 system 策略有效。Windows/macOS 对局域网 DNS 的 TUN 劫持有平台限制；发现系统 DNS 是 LAN 路由器时，按实际文档核查，不擅改全机 DNS。[DNS](https://wiki.metacubex.one/config/dns/)、[TUN](https://wiki.metacubex.one/config/inbound/tun/)

## iPhone

按目标 Shadowrocket 实际版本核对导入能力；记录获取、解析、保存和启用各阶段的时间、错误及配置哈希。HTTPS 下载完成和手机原生导入分别验收。

在 Shadowrocket 中本地导入完整 `.conf`，全局路由选择“配置”，核对 WireGuard 节点参数并启动。需要手工建节点时用私密字段文件核对；节点单独导入不包含分流规则。

`ipv6=false`、`prefer-ipv6=false`、原始参数参考副本去除 `::/0`，并加 IP-CIDR6 REJECT。域名/IP 规则与应用 VPN 实际覆盖仍需手机验收。WG 的 `ip` 本生成器使用 `/32` 形式；公开社区文档只写“子网IP”，缺少开发者 schema 对照，应在目标版本确认实际解析结果。

Shadowrocket 的 DNS 参数与原生 WG 节点字段目前依赖 [LOWERTOP 社区维护文档](https://github.com/LOWERTOP/Shadowrocket)；标记为社区来源。WG 节点自身 DNS 在隧道内处理，不能把本地 DoH 设置写成所有 DNS 均已实测加密。

## 规则覆盖与交付载体

当前生成器输出完整内联规则。用户要求完整覆盖时，保留固定规则快照、集合/优先级、DIRECT 例外及末尾策略。主配置较大且导入失败时，先区分下载不完整、解析失败与启用失败，再比较目标版本实际支持的载体。

小主配置加完整外部规则属于待验证方案，需核目标版本语法、集合等价、首次获取、缓存、更新失败和规则未就绪行为；当前生成器尚未实现该路线。常用域名加 GeoIP 的轻量版标记 `coverage=partial` 并列明覆盖变化，用户选择后才作为轻量交付；保留原完整版本。规则行数或文件体积不能单独表示业务覆盖比例。

逐设备说明 App、协议、分流/全隧道用途、主导入文件和参数参考副本，列出版本 ID、adopted/candidate/rejected、supersedes 与实际活动状态。节点 URL、旧协议订阅和完整分流文件分别标注，替代关系明确后再交付。含秘密配置仍走原私密渠道。
