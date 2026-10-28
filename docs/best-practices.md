# 采用的实践

核验日期：2026-10-28。参考结构，不复制第三方代码或素材。

- [Agent Skills specification](https://agentskills.io/specification)：使用与目录一致的 name、明确 description、必需 SKILL.md；脚本/参考/资产按需加载。
- [Anthropic skills](https://github.com/anthropics/skills)：参考技能包按用途划分与渐进披露，不把依赖环境与权限当作默认授权。
- [OpenAI skills README](https://github.com/openai/skills/blob/main/README.md)：当前仓库已提示弃用并转向新的插件路径；因此本项目不承诺旧安装命令通用于当前客户端，也不把发布与安装混称。
- [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)：最小只读权限、无凭据任务、不使用 pull_request_target 执行不可信代码、固定 action 提交、有限运行时间。

本包增加可执行配置检查、资源哈希、实际头像预览、行为测试和无私密数据的媒体 smoke test。它们验证实现边界，不用重复的标题/关键词测试冒充成片质量。
