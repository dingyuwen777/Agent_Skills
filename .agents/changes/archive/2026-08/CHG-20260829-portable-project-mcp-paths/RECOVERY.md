# Archive Delivery Recovery

本文件仅记录 `CHG-20260829-portable-project-mcp-paths` 归档交付时的一次 GitHub 外部状态异常，不修改该 Change 的需求、实现、验证或 `status: done` 结论。

## 已确认事实

- Feature PR `#36` 正常合并，merge commit：`c581643bfa9214c835da7b4533791d67bc1b275e`。
- Feature main CI：run `33237519731`，Skill Tests、Runtime Windows Package、Runtime macOS Package 全部 success。
- Archive PR `#37` head：`642a7765e38c94a989c05b5567a5c8d5b24972fb`。
- Archive PR CI：run `33237734545`，三个 Job 全部 success。
- 第一次调用 GitHub merge action 时客户端 `ReadTimeout`；随后 GitHub 报 `Merge already in progress`。
- 只读 Git 图确认 `main` 已生成 merge commit `511faf38eb67af35fe5d98359fa1110b466abb3b`，父提交分别为 feature main `c581643bfa9214c835da7b4533791d67bc1b275e` 和 archive head `642a7765e38c94a989c05b5567a5c8d5b24972fb`。
- compare `642a7765... → 511faf38...` 无文件差异，证明归档内容实际已经进入 main Git 历史。
- 但 GitHub PR `#37` 元数据没有同步为 merged，官方 merged-status GET 返回 404，且该异常 main 更新没有产生对应 push CI。
- 为避免把外部元数据不一致伪报为正常归档交付，`#37` 已明确关闭并记录原因。

## 恢复目标

通过独立非 Draft 治理 PR 提交本记录，并要求：

1. 该恢复 PR 自身永久 CI 全绿；
2. 正常合并到 main；
3. 合并后的 main 获得新鲜 push CI；
4. Active Change 继续不存在；
5. archive `CHANGE.md` 继续保持 `status: done`；
6. 不修改 Runtime、installer、测试、VERSION、Release 或产品 Contract。

恢复成功后，功能正确性仍由 Feature PR #36 和 main run `33237519731` 证明；本恢复链只补齐归档后的 GitHub/CI 交付证据。
