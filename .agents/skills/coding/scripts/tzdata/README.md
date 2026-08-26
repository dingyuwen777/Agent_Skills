# 最小 `Asia/Shanghai` 时区资源

Python 标准库 `zoneinfo` 在 Linux/macOS 通常可以读取系统 IANA tzdb，但部分 Windows Python 环境没有系统时区数据库，也没有额外安装 PyPI `tzdata`。Coding CLI 在模块加载时需要 `ZoneInfo("Asia/Shanghai")` 来保证 Agent 自有时间使用北京时间；如果完全依赖宿主 tzdb，`bootstrap`、`discover`、`status`、`new-change` 等入口会在这类 Windows 环境中尚未执行命令前就失败。

本目录因此只携带一个最小的 IANA TZif 资源：

```text
tzdata/zoneinfo/Asia/Shanghai
```

它只作为 Python `zoneinfo` 的标准 fallback resource package。系统已经有 IANA tzdb 时仍由标准库优先使用系统数据；系统没有 tzdb 时才从这个本地 package 读取 `Asia/Shanghai`。它不是完整 `tzdata` 发行版，也不能作为其他时区的通用数据库。

维护要求：

- 不通过运行时网络下载时区数据；
- 不要求目标项目为了使用 Agent_Skills 修改自己的 Python 依赖；
- 更新该 TZif 资源时必须在无系统 `TZPATH` 的隔离测试中证明 `ZoneInfo("Asia/Shanghai")` 可解析且当前时间偏移为 `+08:00`；
- 该资源只解决 Coding CLI 自身的北京时间硬规则，不改变目标项目对业务时间、外部协议或历史时区数据的定义。
