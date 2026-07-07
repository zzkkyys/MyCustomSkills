# ClaudeSkills

自建的 [Claude Skills](https://docs.claude.com/en/docs/claude-code/skills) 仓库。**每个子文件夹是一个独立 skill**，含 `SKILL.md`（带 YAML frontmatter 的 `name` 与 `description`）以及可选的 `references/`、`scripts/` 等资源。

## 安装 / 使用

把某个 skill 软链或复制到 Claude Code 的 skills 目录：

```bash
ln -s "$PWD/grant-proposal-writing" ~/.claude/skills/grant-proposal-writing
```

之后在会话中用 `/grant-proposal-writing` 触发，或让 Claude 按 `description` 自动匹配。

## Skills 列表

| Skill | 用途 |
|---|---|
| [grant-proposal-writing](grant-proposal-writing/) | 撰写/重构/润色中文课题申报书：去AI味与口语味、主线重心排布、去列表化、篇幅控制、docx 公文格式、分遍过稿清单、逐段审阅 prompt |

## 约定

- 目录名即 skill 名，用小写连字符（kebab-case），与 `SKILL.md` 的 `name` 一致。
- `description` 要写清"何时使用"和触发关键词，Claude 靠它决定是否加载。
- 大段细节放 `references/`，可执行辅助放 `scripts/`，保持 `SKILL.md` 精简（渐进式披露）。
