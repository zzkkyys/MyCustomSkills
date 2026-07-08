# 出稿：Markdown → docx 与格式设置

## 先问清格式要求

**动手写之前就要问清导出 docx 的格式要求**，不要等出稿才发现字体字号不符、返工重排。逐项向用户确认：一级/二级/三级标题的字体、字号、是否加粗；正文字体、字号；行距（固定磅值还是倍数）；对齐方式；首行缩进；页边距/页码等。有申报通知或模板的，让用户直接提供原文或模板文件，按其规定设置。确认到的参数记进计划文件，出稿时用 `format_docx.py` 的 CLI 参数传入（`--body-font/--size/--line-spacing/--indent` 等），不必改脚本。若模板本身已带样式，优先保留模板样式。下面是**常见默认值**，仅在用户未给明确要求、也无模板时用。

## 常见中文公文格式默认值

申报书 docx 的一种常见约定（以实际通知/模板为准，不同学科与主管单位差异较大）：

| 元素 | 字体 | 字号 | 其他 |
|---|---|---|---|
| 一级标题 | 黑体 | 三号（16pt） | 加粗、黑色 |
| 二级标题 | 楷体_GB2312 | 三号（16pt） | 加粗、黑色 |
| 三级及以下标题 | 楷体_GB2312 | 三号（16pt） | 黑色 |
| 正文 | 仿宋_GB2312 | 三号（16pt） | 行距 28 磅 EXACTLY、两端对齐、首行缩进 2 字、黑色 |

要点：
- **三号 = 16pt**。
- **行距 28 磅**用 `WD_LINE_SPACING.EXACTLY` + `Pt(28)`，不是"1.5倍"。
- **两端对齐** `WD_ALIGN_PARAGRAPH.JUSTIFY`（不是左对齐）。
- **首行缩进 2 字**：三号字下 `Pt(32)`（约等于 2 个 16pt 字）。**列表段（numPr）不加缩进**，判断 `pPr/numPr` 是否存在。
- 字体名四个属性都要设：`w:ascii / w:hAnsi / w:eastAsia / w:cs`，否则中英文可能用不同字体。
- 颜色统一 `RGBColor(0,0,0)`，防止标题被主题色染蓝。

## 完整流程

### 0. 依赖检查与兜底

```bash
pandoc --version                    # 缺 pandoc 则无法转 docx
python -c "import docx"             # 缺 python-docx: pip install python-docx
```

若环境缺 pandoc，只能交付 Markdown、由用户本地转换；若缺 python-docx，可先出未套格式的 docx 并提示用户安装后再跑 `format_docx.py`。

### 1. 合稿

把各节文件合并为一个总 md，加主标题，节间**不留 `---`**（`---` 在 pandoc 里会变成分节/水平线）：

下面命令里 `$SKILL` 指本 skill 所在目录（即 `.../chinese-formal-writing`），`$WORK` 指文稿工作目录（各节 md 所在处）。脚本用绝对路径调用，不依赖当前所在目录，`cd` 到工作目录只是为了让通配符匹配到分节文件。

```bash
cd "$WORK"   # 申报书工作目录（各节 md 所在处）
{ echo "# 〔课题标题〕"; echo; \
  for f in [0-9][0-9]-*.md; do tail -n +1 "$f"; echo; done; } > 合稿.md
```

### 2. 引号修复（关键，务必在转换前做）

pandoc 的 smart 扩展会把中文语境里的 ASCII 直引号 `"` 全部渲染成右引号 `”`，导致**引号不成对**。先用状态机把成对的直引号转成成对中文引号：

```bash
python "$SKILL/scripts/fix_quotes.py" 合稿.md
```

脚本会跳过代码块与简单行内代码，遇引号不成对（奇数）时默认不写出并报错。它对反引号的保护是简单奇偶匹配，含双/三反引号等复杂 Markdown 代码跨度时需人工核对。申报书正文极少含代码，一般无碍。

### 3. pandoc 转 docx

```bash
pandoc 合稿.md -f markdown-smart -o 合稿.docx
```

（可选增强：若当前环境装有 `pandoc-docx-template` skill，可复用其模板与 Lua 过滤器走 md→html→docx 路径，保留更多 HTML 语义；未装则用这里的基础流程即可。）

### 4. python-docx 套格式

默认写到 `合稿.formatted.docx`（不覆盖原件）；格式参数按本课题要求传入：

```bash
python "$SKILL/scripts/format_docx.py" 合稿.docx \
  --body-font 仿宋_GB2312 --h1-font 黑体 --h2-font 楷体_GB2312 \
  --size 16 --line-spacing 28 --indent 32
```

脚本按参数设置字体/字号/行距/对齐/缩进/颜色，标题与正文分别处理，列表段不加首行缩进。加 `--in-place` 才原地覆盖。

## 验证

- 打开 docx 抽查：标题字体是否正确、正文字体字号、行距是否为设定的固定值、段首是否缩进、引号是否成对。
- 用 python-docx 自动抽查关键属性：

```bash
python - <<'PY'
from docx import Document; from docx.oxml.ns import qn
d = Document("合稿.formatted.docx")
for p in d.paragraphs[:12]:
    if not p.runs: continue
    r = p.runs[0]; rf = r._element.rPr.find(qn('w:rFonts'))
    font = rf.get(qn('w:eastAsia')) if rf is not None else None
    pf = p.paragraph_format
    print(p.style.name, font, r.font.size, "行距", pf.line_spacing, "缩进", pf.first_line_indent)
PY
```
- 引号成对核对：`grep -c '“' 合稿.md` 与 `grep -c '”' 合稿.md` 应相等。
- 模板主要在 Windows Word 下测试，WPS / macOS Word 渲染可能略有差异，终稿建议在 Windows Word 里核对。
