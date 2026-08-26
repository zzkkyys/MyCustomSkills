# ClaudeSkills

自建的 [Claude Skills](https://docs.claude.com/en/docs/claude-code/skills) 仓库。**每个子文件夹是一个独立 skill**，含 `SKILL.md`（带 YAML frontmatter 的 `name` 与 `description`）以及可选的 `references/`、`scripts/` 等资源。

## 安装 / 使用

把某个 skill 软链或复制到 Claude Code 的 skills 目录：

```bash
ln -s "$PWD/chinese-formal-writing" ~/.claude/skills/chinese-formal-writing
ln -s "$PWD/grant-proposal-writing" ~/.claude/skills/grant-proposal-writing
ln -s "$PWD/postdoc-fund-proposal"  ~/.claude/skills/postdoc-fund-proposal
ln -s "$PWD/paper-revision-review"  ~/.claude/skills/paper-revision-review
ln -s "$PWD/marp-ppt-theme"          ~/.claude/skills/marp-ppt-theme
```

之后在会话中用 `/grant-proposal-writing` 等触发，或让 Claude 按 `description` 自动匹配。

## Skills 列表

### 中文写作（分层）

`chinese-formal-writing` 是通用写作打磨层，`grant-proposal-writing` 与 `postdoc-fund-proposal` 是文体层、复用前者。**写申报书时建议把用到的文体 skill 与 `chinese-formal-writing` 一起安装。**

| Skill | 层 | 用途 |
|---|---|---|
| [chinese-formal-writing](chinese-formal-writing/) | 通用 | 中文学术/公文文稿打磨：去AI味与口语味、去列表化、学术化分遍过稿+术语表、导出公文 docx（pandoc+python-docx、修中文引号）、逐段/分批审阅 prompt。不含任何特定文体的结构规范 |
| [grant-proposal-writing](grant-proposal-writing/) | 文体 | 中文课题申报书特有的结构：主线重心排布、章节骨架、篇幅/页数分配、拟题、涉密边界；通用工序复用 chinese-formal-writing |
| [postdoc-fund-proposal](postdoc-fund-proposal/) | 文体 | 《中国博士后科学基金面上资助申请书》"项目信息"六栏正文：固定栏目与字数上限（1000/2000/2000/1000/500/1000）、匿名评审红线（除研究基础外泄露身份可判 0 分）、分节写作要点、卡字数精炼；通用工序复用 chinese-formal-writing |

### 审阅与交付

| Skill | 用途 |
|---|---|
| [paper-revision-review](paper-revision-review/) | 把修改建议做成可交互的**离线审阅网页**：改动处内联标记（新增/删除/改写/结构调整），点击在批注栏显示原文／改后／**为什么改**；支持标记与终稿视图切换、按严重程度突出、逐条浏览、勾选已处理。含模板、渲染脚本与结构/类型/离线性校验器（拦标记无条目、标签嵌套错误、脚本注入、外部资源），产物为单文件零依赖 HTML。附**分章审阅清单**（摘要引言/相关工作/理论/方法/实验/结论各自的高频问题）与**第二意见协作流程**（让另一模型独立复审再三方对照，含「核实后再采信」纪律）。渲染器不限语言与学科；内置清单面向计算机与机器学习实验论文，其他学科需替换为本学科标准 |

### 演示文稿

| Skill | 用途 |
|---|---|
| [marp-ppt-theme](marp-ppt-theme/) | 使用品牌中性的编辑式学术主题创建、排版、检查并导出 Marp Markdown 演示稿。采用暖灰纸面、墨色文字和单一钴蓝强调，提供非对称首页、单路径目录、浅色章节页、无卡片多栏和现代三线表，包含 16:9 starter、完整组件 demo、视觉回归压力测试，以及 HTML/PDF/PPTX/PNG 渲染脚本 |

## 约定

- 目录名即 skill 名，用小写连字符（kebab-case），与 `SKILL.md` 的 `name` 一致。
- `description` 要写清"何时使用"和触发关键词，Claude 靠它决定是否加载。
- 大段细节放 `references/`，可执行辅助放 `scripts/`，保持 `SKILL.md` 精简（渐进式披露）。
