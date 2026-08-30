本文件仅用于本 Change 的 Red 阶段证据定位，待 Red 验证后删除。

预期失败：
- 已完成 Runtime disclosure Change 尚未恢复到 archive；
- skill-tests.yml 仍安装 requirements-build 并构建三平台 onefile；
- runtime-package-tests.yml 尚不存在；
- Runtime/USAGE 尚未明确宿主连接级非 daemon 生命周期。
