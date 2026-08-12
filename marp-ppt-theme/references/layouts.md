# Blue Theme 布局组件

## 目录

- [多栏布局](#多栏布局)
- [彩色多栏](#彩色多栏)
- [图文混排](#图文混排)
- [时间轴](#时间轴)
- [大数字](#大数字)
- [提示框与标签](#提示框与标签)
- [全图页](#全图页)
- [补充结构](#补充结构)
- [紧凑与工具类](#紧凑与工具类)

HTML 容器内部必须保留空行。不要把 Markdown 标题或列表紧贴在 `<div>` 后。

## 多栏布局

### 两栏

```markdown
<div class="columns-2">
<div>

### 左栏标题

- 内容一
- 内容二

</div>
<div>

### 右栏标题

- 内容一
- 内容二

</div>
</div>
```

将外层类替换为 `columns-3` 或 `columns-4`，并分别放入三个或四个直接子 `<div>`。使用 `columns-2x2` 时放入四个直接子容器，自动排成两行两列。

## 彩色多栏

用 `columns-2-colors` 展示两种方案，用 `columns-3-colors` 展示三个阶段。结构与普通多栏相同：

```markdown
<div class="columns-3-colors">
<div>

### 输入

说明输入信息。

</div>
<div>

### 处理

说明核心方法。

</div>
<div>

### 输出

说明最终结果。

</div>
</div>
```

## 图文混排

### 左图右文

```markdown
<div class="img-left">
<div>

![width:400px](assets/architecture.svg)

</div>
<div>

### 模型架构

- 编码输入特征
- 执行核心推理
- 生成输出结果

</div>
</div>
```

将外层类改为 `img-right` 并交换两个子容器，即可得到左文右图布局。

## 时间轴

### 垂直时间轴

```markdown
<div class="timeline">
<div>
<span class="year">阶段一</span>

### 数据准备

收集、清洗并核验数据。

</div>
<div>
<span class="year">阶段二</span>

### 方法实现

完成模型与实验流程。

</div>
</div>
```

### 水平时间轴

将外层类改为 `timeline-horizontal`。水平时间轴适合三至四个短阶段，每个阶段标题控制在六个汉字左右。

当水平时间轴内容较短、需要在正文安全区内垂直居中时，给页面增加 `<!-- _class: timeline-centered -->`。

## 大数字

```markdown
<div class="big-number cards">
<div>
<span class="number">96.2<span class="unit">%</span></span>
<div class="label">准确率</div>
</div>
<div>
<span class="number accent">3.5<span class="unit">×</span></span>
<div class="label">速度提升</div>
</div>
</div>
```

删除 `cards` 可使用无边框版本；给 `.number` 添加 `accent` 可使用红色强调。每页只突出两至四个同口径指标。

## 提示框与标签

```markdown
<div class="highlight">黄色重点提示</div>
<div class="info-box">蓝色补充信息</div>
<div class="warning-box">红色风险提醒</div>
<div class="success-box">绿色完成状态</div>
<div class="insight-box">简洁的研究洞察</div>
```

```markdown
<span class="tag tag-primary">核心</span>
<span class="tag tag-accent">重要</span>
<span class="tag tag-success">完成</span>
<span class="tag tag-warning">进行中</span>
<span class="tag tag-info">待核验</span>
```

主题还保留 `tag-aug` 和 `tag-loss` 两个扩展配色，适合机器学习演示中的“数据增强”和“损失函数”。

## 全图页

```markdown
<!-- _class: image-slide -->

# 隐藏标题

![bg contain](assets/figure.png)

<div class="image-caption">图片说明文字</div>
```

使用 `<!-- _class: image-slide with-title -->` 显示带深色叠层的页标题。`image-slide` 必须与 Marp 原生背景图片语法配合：保留完整图片用 `bg contain`，接受裁剪以铺满画布时用 `bg cover`。旧类名 `full-image` 只作为兼容别名保留；不要使用无效的 `![background](...)` 语法。

图片优先使用足够清晰的本地资源，并核对缩放或裁剪效果。说明文字应放在 `image-caption` 中，保持一至两行。

## 补充结构

- 使用 `columns` 创建自由宽度的左右栏，直接子容器分别使用 `left` 和 `right`；叠加 `half` 可等宽。常规两栏优先使用约束更明确的 `columns-2`。
- 使用 `<div class="footnotes">...</div>` 将少量脚注置于底部安全区。脚注区域最多约三行，超出时会滚动；不要用脚注承载正文论证。
- 在一级标题的局部数字外包裹 `<span class="num">1</span>`，可单独控制标题数字样式。
- 给只用于屏幕演示的辅助内容加 `no-print`，打印或导出时隐藏。隐藏前确认它不包含理解结论所必需的信息。

## 紧凑与工具类

- 页面类 `h3-compact`：减小三级标题上下间距。
- 页面类 `no-indent`：取消列表整体缩进。
- 页面类 `long-title`：为三行一级标题增加顶部安全区并适度缩小字号。
- 页面类 `timeline-centered`：将短水平时间轴垂直置中。
- 页面类 `debug-layout`：显示主要容器和卡片边界，交付前移除。
- 容器类 `no-list-indent`：只影响指定容器内的列表。
- `divider`：插入渐变分隔线，例如 `<div class="divider"></div>`。
- `text-left/center/right`：文本对齐。
- `text-sm/lg/xl`：字号调整。
- `font-normal/bold`：字重调整。
- `mt-*`、`mb-*`、`p-*`：局部间距调整。
- `hidden`、`block`、`inline`、`flex`：显示方式工具类；仅在确有必要时使用。
