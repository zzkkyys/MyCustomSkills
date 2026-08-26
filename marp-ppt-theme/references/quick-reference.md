# Blue Theme 快速参考

## 目录

- [最小前置配置](#最小前置配置)
- [推荐演示结构](#推荐演示结构)
- [页面类型](#页面类型)
- [布局选择](#布局选择)
- [文本与工具类](#文本与工具类)
- [制作检查](#制作检查)

## 最小前置配置

```yaml
---
marp: true
theme: blue
size: 16:9
paginate: true
math: katex
---
```

用单独一行 `---` 分隔幻灯片。主题 CSS 位于项目的 `themes/blue.css`。

## 推荐演示结构

1. `title` 首页
2. `toc` 目录
3. `section-divider` 章节分隔
4. 内容页若干
5. `quote` 核心观点或引文，可选
6. `tinytext` 参考文献，可选
7. `thanks` 结束页

## 页面类型

在对应页面的 Markdown 开头添加局部类指令。

### 首页

```markdown
<!-- _class: title -->

# 主标题

## 副标题

<img class="cover-illustration" src="assets/cover-illustration.png" alt="首页插图">

报告人

日期

机构或项目名称
```

首页采用非对称编辑式布局，副标题显示在主标题上方，右上角可放置一张带透明背景的轻量插图。三个普通段落依次映射为报告人、日期和机构；模板中使用功能性占位标签，不虚构姓名或机构。需要更换插图时保持方形画布、透明背景、无文字和克制配色；不需要插图时可直接删除图片行。

### 目录

```markdown
<!-- _class: toc -->

# 目录

- 第一部分
- 第二部分
- 第三部分
```

目录建议使用四至六项；六项会排成 2×3 编号列表。各项使用平行结构，以留白和细线组织层级，不在目录项中放二级说明。

### 章节分隔

```markdown
<!-- _class: section-divider -->

# 第一部分

## Background and Motivation

一句说明，可省略
```

### 引用页

```markdown
<!-- _class: quote -->

> 简短、可核实的引用或核心观点。

作者或来源
```

### 致谢页

```markdown
<!-- _class: thanks -->

# 感谢聆听

欢迎提问与交流

<div class="thanks-mark">Q&amp;A</div>
```

致谢页与首页形成首尾呼应，正文只保留一句结束语或联系方式。右侧 `.thanks-mark` 是可编辑的真实内容，可改为“问答”、联系方式或删除。

### 高密度内容

使用 `<!-- _class: small-text -->` 将正文缩小到约 18pt；使用 `tinytext` 缩小到约 16pt。优先拆页，只对参考文献、附录等确需高密度的页面使用。

### 长标题

普通内容页自动为两行一级标题预留空间。标题预计达到三行时使用 `<!-- _class: long-title -->`；超过约 54 个汉字时仍应优先缩短或拆成标题与副标题。

## 布局选择

| 内容关系 | 推荐组件 |
|---|---|
| 两组信息并列 | `columns-2` |
| 三阶段流程 | `columns-3`、`timeline-horizontal` |
| 四个要点 | `columns-4`、`columns-2x2` |
| 强调两种方案差异 | `columns-2-colors` |
| 图文说明 | `img-left`、`img-right` |
| 时间演进 | `timeline`、`timeline-horizontal` |
| 关键指标 | `big-number`，可叠加 `cards` |
| 图片页 | `image-slide` + `![bg contain](...)`，可叠加 `with-title` |

普通多栏默认使用无卡片的编辑式细线布局。只有边界本身承担分组意义时，才给多栏容器叠加 `cards`；不要把每一页都做成卡片网格。

所有组件的完整语法见 `layouts.md`。

## 文本与工具类

- `**粗体**`：钴蓝强调；`*斜体*`：同色下划线强调；`<mark>`：黄色高亮。
- `highlight`、`info-box`、`warning-box`、`success-box`、`insight-box`：语义提示框。
- `tag-group`：横向排列并自动换行的标签组；内部使用 `tag tag-primary`、`tag-accent`、`tag-success`、`tag-warning`、`tag-info`。
- `text-left`、`text-center`、`text-right`：对齐。
- `text-sm`、`text-lg`、`text-xl`：字号。
- `font-normal`、`font-bold`：字重。
- `mt-0/1/2`、`mb-0/1/2`、`p-0/1/2`：间距。
- `no-indent`、`no-list-indent`：缩小列表缩进。
- `h3-compact`：压缩三级标题间距。
- `timeline-centered`：将短水平时间轴垂直置中。
- `debug-layout`：显示主要布局边界，仅在调试稿中使用。

## 表格

- 未标记的单元格默认左对齐；使用标准 Markdown 对齐标记：文本列用 `:---` 左对齐，数值列用 `---:` 右对齐。
- 主题采用无竖线的现代三线表；隔行底色只用于辅助横向阅读。
- 只有需要突出最佳结果时，才用 `<div class="table-emphasis">` 包裹表格并加粗关键单元格；普通粗体不会触发整行强调。
- 一页建议不超过八列、六行；更密集时使用 `small-text`，仍然拥挤则拆页。

## 脚注

- 使用 `<div class="footnotes">...</div>` 放置理解本页所需的少量补充信息。
- 脚注不提供滚动隐藏；超过三行或约 180 个字符时，校验器会警告，应缩短或移到新页面。

## 制作检查

- 让标题直接表达本页结论，不只写“背景”“分析”等泛化标签。
- 保持 HTML `<div>` 后和 `</div>` 前的空行，使内部 Markdown 正确解析。
- 使用相对于演示稿文件的图片路径；离线交付时不要依赖外部占位图片。
- 为普通图片填写有意义的替代文本；背景全图页额外提供 `.sr-only` 文字说明。
- 不虚构数字、引文或来源；示例数据必须替换为真实数据。
- 按 `content-limits.md` 控制信息密度。
- 用 `scripts/validate_deck.py` 做静态检查，再用 `scripts/render_deck.py` 实际渲染；重要交付生成逐页 PNG 并运行 `scripts/validate_rendered_images.py`。
