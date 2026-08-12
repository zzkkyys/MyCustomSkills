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

报告人

日期

机构或项目名称
```

首页采用左对齐书封式布局，副标题显示在主标题上方，右侧深蓝区域只作视觉锚点。三个普通段落依次映射为报告人、日期和机构。

### 目录

```markdown
<!-- _class: toc -->

# 目录

- 第一部分
- 第二部分
- 第三部分
```

目录建议使用四至六项；六项会排成 2×3 编号卡片。各项使用平行结构，避免在卡片中放二级说明。

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
```

致谢页与首页形成首尾呼应，右侧固定显示 `Q&A`，正文只保留一句结束语或联系方式。

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

所有组件的完整语法见 `layouts.md`。

## 文本与工具类

- `**粗体**`：主色强调；`*斜体*`：红色强调；`<mark>`：黄色高亮。
- `highlight`、`info-box`、`warning-box`、`success-box`、`insight-box`：语义提示框。
- `tag tag-primary`、`tag-accent`、`tag-success`、`tag-warning`、`tag-info`：标签。
- `text-left`、`text-center`、`text-right`：对齐。
- `text-sm`、`text-lg`、`text-xl`：字号。
- `font-normal`、`font-bold`：字重。
- `mt-0/1/2`、`mb-0/1/2`、`p-0/1/2`：间距。
- `no-indent`、`no-list-indent`：缩小列表缩进。
- `h3-compact`：压缩三级标题间距。
- `timeline-centered`：将短水平时间轴垂直置中。
- `debug-layout`：显示主要布局边界，仅在调试稿中使用。

## 表格

- 使用标准 Markdown 对齐标记：首列用 `:---` 左对齐，数值列用 `---:` 右对齐。
- 主题采用无竖线的现代三线表；隔行底色只用于辅助横向阅读。
- 将最佳结果所在行的关键单元格加粗，主题会自动给该行添加浅蓝强调底和红色引导线。
- 一页建议不超过八列、六行；更密集时使用 `small-text`，仍然拥挤则拆页。

## 制作检查

- 让标题直接表达本页结论，不只写“背景”“分析”等泛化标签。
- 保持 HTML `<div>` 后和 `</div>` 前的空行，使内部 Markdown 正确解析。
- 使用相对于演示稿文件的图片路径；离线交付时不要依赖外部占位图片。
- 不虚构数字、引文或来源；示例数据必须替换为真实数据。
- 按 `content-limits.md` 控制信息密度。
- 用 `scripts/validate_deck.py` 做静态检查，再用 `scripts/render_deck.py` 实际渲染；重要交付生成逐页 PNG 并运行 `scripts/validate_rendered_images.py`。
