# 生成输入合同

Python 3.10+，仅标准库。生成主机须为 POSIX，输出文件系统须支持 POSIX 权限；原生 Windows 会在读取输入前停止。四端配置均可在合适的生成主机准备。JSON manifest 和生成文件属于私密材料，使用绝对路径。输出目录必须是尚不存在的新目录；源配置不变，禁止覆盖现有交付。

输入校验失败时不会建立输出目录。磁盘满、权限变化等写盘异常可能留下权限受限的部分输出；记录失败后改用新的输出目录重试，未完成目录不要交付。

生成器先确认输出目录实际权限为 0700，再写配置，并逐一回读文件的 0600 权限。目录权限检查失败时只可能留下空目录，不写入密钥。

| 字段 | 合同 |
| --- | --- |
| targets | 显式设备列表，不能有重复项 |
| client_configs | key 与 targets 完全相同；value 是各自原始单 Peer WireGuard 配置绝对路径 |
| output_dir | 用户授权的新私密目录绝对路径 |
| ipv6_policy | 必须明确为 ipv4-only |
| cn_domains | 完整域名快照，每行 `+.example.cn`；忽略注释空行，大小写归一并去重 |
| cn_networks | 完整 CIDR 快照；取 IPv4、合并相邻/重叠网段 |
| expected_rule_counts | 归一化后的 domains 与 ipv4_networks 数量；不得根据报错自动改为实测数掩盖缺表 |
| rules_as_of | 快照日期与版本标识，必填 |
| custom_direct_rules | 可选纯文本，每行一条既有 DIRECT 规则；导出时保留完整例外与来源 |
| mixed_ports | 可选各 Mihomo 设备端口映射；桌面默认7897，Android默认7890，须对照目标当前设置 |
| node_name | 可选 URL 安全 ASCII 节点名，默认 WG-OUT |

原始配置需有 Interface 的 PrivateKey、IPv4 Address `/32` 与已确认 MTU，Peer 的 PublicKey、字面 IPv4 Endpoint。PSK 和 PersistentKeepalive 按原值保留；缺 keepalive 表示 0。当前 iPhone 生成器未核实 Shadowrocket PSK 字段，源文件含 PSK 会显式停止该批，须先完成目标 schema 核验再支持。

示例只说明结构，输入路径和数量须替换为当前实际值。

```json
{
  "targets": ["iphone", "android", "windows", "macos"],
  "client_configs": {
    "iphone": "/absolute/private/source/iphone.conf",
    "android": "/absolute/private/source/android.conf",
    "windows": "/absolute/private/source/windows.conf",
    "macos": "/absolute/private/source/macos.conf"
  },
  "output_dir": "/absolute/private/new-delivery",
  "ipv6_policy": "ipv4-only",
  "cn_domains": "/absolute/private/rules/cn-domain.list",
  "cn_networks": "/absolute/private/rules/cn-ipv4.list",
  "expected_rule_counts": {"domains": 123, "ipv4_networks": 456},
  "rules_as_of": "YYYY-MM-DD; upstream commit/hash recorded separately",
  "custom_direct_rules": "/absolute/private/rules/custom-direct.list"
}
```

国内快照可从当前可信规则项目取得，例如 [MetaCubeX meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat/tree/meta/geo/geosite)、[国内 IPv4 路由快照](https://github.com/17mon/china_ip_list)。记录精确来源、获取日期和输入哈希，核对全量与计数，再生成；更新规则属于显式步骤。生成器本身不下载数据。

主导入文件包含完整内联规则，避免用户先导入后等待远程规则下载。移动端过滤桌面 PROCESS 例外，并在 build-receipt.json 记录保留与过滤数量。桌面保留进程例外。IPv4 参数参考副本仅将 AllowedIPs 统一成 IPv4 全段，不充当主要分流客户端配置。
