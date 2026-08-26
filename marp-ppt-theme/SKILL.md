---
name: marp-ppt-theme
description: "使用内置的通用 blue.css 学术蓝色主题创建、改写、排版、检查和导出 Marp Markdown 幻灯片，支持标题页、目录、章节页、多栏、图文、时间轴、大数字、引用、表格、公式、图片页及 PDF/PPTX/HTML/PNG 输出。适用于用户要求制作 Marp PPT、生成 .md 演示稿、套用通用蓝色学术主题、使用主题组件排版、检查页面容量，或通过 Marp CLI 导出演示文稿时。"
---

# Marp PPT 通用蓝色主题

使用随附模板生成品牌中性的 16:9 编辑式学术演示稿。视觉语言采用暖灰纸面、墨色文字和单一钴蓝强调，以排版、留白和真实图表建立层级。优先使用初始化、校验和渲染脚本，避免遗漏隐藏配置、主题参数或本地资源。

## 工作流程

1. 确认主题、受众、页数、输出格式和目标目录。信息不完整时，基于用户材料作保守假设，不虚构事实。
2. 初始化新项目：

   ```bash
   python3 scripts/init_deck.py <目标目录> --deck-name <演示稿.md>
   ```

   需要完整组件演示和视觉压力测试稿时增加 `--include-demo`。已有目标文件默认不覆盖；只有用户明确允许覆盖时才使用 `--force`。
3. 从生成的轻量 starter 写作。先读 `references/quick-reference.md`；需要复杂组件时再读 `references/layouts.md`，不要默认加载全部参考文件。
4. 按 `references/content-limits.md` 控制每页信息密度。优先删减、拆页或降低栏数，只在参考文献等页面使用小字体。
5. 运行静态检查。校验器同时检查资源、组件类、长标题和脚注安全容量：

   ```bash
   python3 scripts/validate_deck.py <演示稿.md>
   ```

6. 阅读 `references/cli-and-export.md` 后实际渲染。对可信演示稿使用：

   ```bash
   python3 scripts/render_deck.py <演示稿.md> --format pdf --trusted --allow-local-files
   ```

7. 重要交付还应渲染逐页 PNG，并用 `scripts/validate_rendered_images.py` 核对页数、编号和尺寸；最后逐页检查溢出、图片裁剪、字体替换、表格可读性和引用来源。静态检查通过不等于视觉检查完成。

## 内容与版式选择

- 用 `title`、`toc`、`section-divider`、`thanks` 组织整体结构。
- 用默认无卡片的 `columns-2/3/4`、`columns-2x2` 表达并列、对比与流程；只有边界承担分组意义时才叠加 `cards`。
- 用 `img-left/right` 处理图文混排；图片页使用 `image-slide` 页面类和 Marp 原生 `![bg contain](...)` 语法。
- 用 `timeline` 或 `timeline-horizontal` 表达时间演进。
- 用 `big-number` 突出少量同口径指标，用 `quote` 展示有来源的引文或核心判断。
- 用标准 Markdown 表格和 KaTeX 公式，不使用图片代替可编辑的文字与公式；只有需要突出结果行时才用 `table-emphasis` 包裹表格。

## 关键约束

- 保持 `theme: blue` 和 `size: 16:9`，并让项目中的 `themes/blue.css` 可访问。
- 普通内容页标题默认预留两行；需要三行标题时增加 `long-title`，并优先考虑缩短标题。
- 在 HTML 容器的开始标签之后和闭合标签之前保留空行，使内部 Markdown 正确解析。
- 使用相对于演示稿文件的本地资源路径；离线交付时不要依赖远程占位图片。
- 普通图片填写有意义的替代文本；背景全图页增加 `.sr-only` 文字说明。
- 首页可使用 `.cover-illustration` 图片作为右上视觉锚点；优先选择透明背景、无文字、与主题同色的轻量插图，不使用像占位框一样的无语义矩形。
- 只对可信 Markdown 启用完整 HTML；只有需要读取可信本地资源时才启用本地文件访问。
- 不自动安装 Marp CLI，不擅自覆盖用户现有文件或 VS Code 配置。
- 不虚构数字、引文、机构、作者或来源；模板中的示例数据必须替换或删除。
- 致谢页右栏使用可编辑的 `.thanks-mark` 实体内容；脚注保持三行以内，不依赖滚动隐藏。

## 资源路由

- `assets/project-template/slides.md`：六页轻量 starter。
- `assets/project-template/demo.md`：完整组件演示，按需查看或通过 `--include-demo` 复制。
- `assets/project-template/visual-regression.md`：长标题、高密度组件、图片页和脚注的渲染压力测试稿。
- `assets/project-template/themes/blue.css`：品牌中性的编辑式学术主题。
- `references/quick-reference.md`：常用页面、布局选择和制作检查；每次优先读取。
- `references/layouts.md`：全部组件语法；使用复杂布局时读取。
- `references/content-limits.md`：页面容量和写作约束；内容较多时读取。
- `references/cli-and-export.md`：VS Code、CLI、安全和故障排查；预览或导出时读取。
- `scripts/init_deck.py`：安全复制模板并合并 VS Code 设置。
- `scripts/validate_deck.py`：静态检查演示稿与资源。
- `scripts/render_deck.py`：用明确的主题、HTML 和本地资源参数调用 Marp CLI。
- `scripts/validate_rendered_images.py`：核对逐页 PNG 的数量、页码连续性和画布尺寸。
