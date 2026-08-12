# Marp 预览与导出

## 目录

- [初始化项目](#初始化项目)
- [VS Code 预览](#vs-code-预览)
- [静态检查](#静态检查)
- [CLI 导出](#cli-导出)
- [安全边界](#安全边界)
- [常见问题](#常见问题)

## 初始化项目

```bash
python3 path/to/marp-ppt-theme/scripts/init_deck.py ./my-slides --deck-name talk.md
```

脚本复制 `themes/blue.css`、离线示例图和轻量 starter，并安全合并 `.vscode/settings.json`。已有文件默认不覆盖；只有明确需要时才使用 `--force`。

需要同时复制完整组件演示和 `visual-regression.md` 压力测试稿时增加 `--include-demo`。

## VS Code 预览

安装 Marp for VS Code 后打开演示稿。项目设置只注册：

```json
{
  "markdown.marp.themes": ["./themes/blue.css"]
}
```

主题依赖常规 `<div>`、`<span>` 等 HTML 组件。保持工作区可信，并避免在不可信 Markdown 上放宽 HTML 权限。

## 静态检查

```bash
python3 path/to/marp-ppt-theme/scripts/validate_deck.py ./my-slides/talk.md
```

检查前置配置、主题文件、页面分隔、页面类、长标题、图片页语法、外部图片、HTML 容器空行和缺失的本地资源。静态检查不能发现所有视觉溢出，交付前仍需实际渲染。

## CLI 导出

先安装 Marp CLI，并确保 `marp` 命令位于 `PATH`。使用随附脚本统一传入主题和 HTML 参数：

```bash
python3 path/to/marp-ppt-theme/scripts/render_deck.py ./my-slides/talk.md --format html --trusted
python3 path/to/marp-ppt-theme/scripts/render_deck.py ./my-slides/talk.md --format pdf --trusted --allow-local-files
python3 path/to/marp-ppt-theme/scripts/render_deck.py ./my-slides/talk.md --format pptx --trusted --allow-local-files
python3 path/to/marp-ppt-theme/scripts/render_deck.py ./my-slides/talk.md --format png --trusted --allow-local-files
python3 path/to/marp-ppt-theme/scripts/render_deck.py ./my-slides/talk.md --format images --trusted --allow-local-files
```

`png` 只渲染第一页；`images` 按 `talk-pages.001.png`、`talk-pages.002.png` 等生成逐页图片。逐页输出后核对页数、页码和 16:9 画布：

```bash
python3 path/to/marp-ppt-theme/scripts/validate_rendered_images.py ./my-slides/talk.md
```

已有输出默认不覆盖；确认需要替换时增加 `--force`。逐页图片的 `--force` 会覆盖同名页面，但页数减少时可能遗留旧的高页码文件，因此回归检查宜输出到空目录。若 `marp` 不在 `PATH`，可用 `--marp-command /path/to/marp` 指定可执行文件。

也可直接调用 Marp：

```bash
marp --theme-set ./themes/blue.css --html talk.md -o talk.html
marp --theme-set ./themes/blue.css --html --allow-local-files --pdf talk.md -o talk.pdf
marp --theme-set ./themes/blue.css --html --allow-local-files --pptx talk.md -o talk.pptx
marp --theme-set ./themes/blue.css --html --allow-local-files --images png talk.md -o talk-pages.png
```

从演示目录执行直接命令，或给主题、演示稿和输出文件传入绝对路径。

## 安全边界

- 只对可信的本地演示稿启用完整 HTML。
- 只有渲染本地图片、字体等资源时才传入 `--allow-local-files`。
- 不要对来自陌生来源的 Markdown 同时启用 HTML 与本地文件访问。
- 不要让脚本自动安装 Marp CLI；依赖安装需要用户明确授权。

## 常见问题

- 出现 `unknown theme`：确认 `themes/blue.css` 存在，并通过 `--theme-set` 注册。
- 多栏内容退化为纯文本：确认启用了 HTML，并检查 `<div>` 内空行。
- PDF/PPTX 缺少本地图片：确认路径相对于演示稿正确，并对可信演示稿增加 `--allow-local-files`。
- VS Code 能预览、CLI 不能导出：两者的主题注册方式不同，CLI 必须显式使用 `--theme-set` 或等效配置。
- 页面内容溢出：减少内容、降低栏数或拆页；不要把缩小字体作为首选方案。
- 图片页未铺满或标题消失：使用 `image-slide` 页面类与 `![bg contain](...)`；需要标题时再叠加 `with-title`。
- 逐页图片数量不符：先清理单独的回归输出目录，再重新渲染并运行 `validate_rendered_images.py`。
