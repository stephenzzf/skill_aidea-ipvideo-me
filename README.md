# aidea-ipvideo-me · 觅跃科技 IP 视频

面向出海 AI 运营增长、数字化转型与交付解读的中文竖屏视频 Skill。保持经过测试的信息卡形式，仅按明确请求修改人物和品牌区域；优先使用可核验来源，保护已批准声音。

## 包含什么

- [Skill 入口](skills/aidea-ipvideo-me/SKILL.md)：核验、脚本、配音、制作、局部修订和交付流程。
- [可配置品牌基线](skills/aidea-ipvideo-me/assets/brand.json)及生成式人物资源。
- 独立品牌区预览、配置验证和 FFmpeg 技术 QA 工具。
- 分开的来源/媒体/复用状态与真实验收限制。

这是操作型 Skill 和辅助工具，不是托管视频平台，也不是一个命令自动完成选题、配音、剪辑、发布的程序。不包含凭据、付费服务授权、原始私人肖像或音频。Rami 和具体模型需按当次服务可用性核验。

## 使用与安装

仓库发布不等于已安装到 ChatGPT、Codex 或任何会话。支持 Agent Skills 的宿主可按其当前官方机制导入 `skills/aidea-ipvideo-me/` 目录；需要支持相应工具才能执行完整视频工作流。只想使用说明时，直接读取 SKILL.md 及其引用。

- [Agent Skills 标准](https://agentskills.io/specification)
- [OpenAI 当前插件开发说明](https://github.com/openai/plugins)

不要仅凭旧版 openai/skills 安装脚本声称所有客户端兼容。确认目标宿主的导入路径、发现机制及启用状态后，再按其官方指引操作。本次仓库不修改用户的本机或个人技能目录。

## 本地辅助工具

要求 Python 3.10+。按 `requirements.txt` 安装 Python 依赖；媒体 QA 另需系统 `ffmpeg`、`ffprobe`。预览需要用户提供可用且许可适用的中文字体文件（本仓库不捆绑字体）。

```bash
python -m pip install -r requirements.txt
python skills/aidea-ipvideo-me/scripts/validate.py
python -m unittest discover -s tests -v
python skills/aidea-ipvideo-me/scripts/preview.py --font /path/to/chinese-font.ttf --output preview.png
python skills/aidea-ipvideo-me/scripts/media_qa.py your-video.mp4 --compare-audio previous-video.mp4
```

预览输出是一张实际 1080×1920 静态版式检查图，不是成片。FFmpeg 工具输出 JSON，技术成功也不能代替完整试听、字幕准确率或平台 UI 验证。

## 示例请求

- “用 aidea-ipvideo-me 核验这四条新闻，按现有信息卡形式试做科技简报。”
- “只换人物 IP 和品牌字，保留旧片内容、时间线、声音和其他版式。”
- “检查这条 YouTube 是否支持我的观点，暂不制作视频。”

## 版本与权利

1.0.0 是从 aidea-ipvideo v2.4 工作流派生的独立品牌包，不覆盖原项目。默认标签为“觅跃科技”，195px 右下圆头像，帽侧 Logo；小圆中的英文仍可能不可读，独立中文标签是主要品牌识别。

见 [资源来源和权利边界](ASSET_PROVENANCE.md) 与 [许可说明](LICENSE)。公开存放不等于授予品牌/商标或第三方内容的通用使用权。

## 验证

CI 检查结构、引用、品牌配置、透明图像、哈希及辅助工具的行为。媒体 smoke test 使用程序生成的中性测试音视频，不包含私人声音。完整真实项目仍需逐条验收。参考项目与采用理由见 [最佳实践](docs/best-practices.md)。
