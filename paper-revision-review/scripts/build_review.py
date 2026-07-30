#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_review.py —— 把一份审阅稿（review spec）渲染成单文件离线审阅页。

用法：
    python3 build_review.py <review_spec.py> [输出路径.html]

review spec 是一个 Python 文件，需定义：
    TITLE     str            页面标题 / 稿纸大标题
    LOC       str            顶栏右侧的定位（如 "main.tex:294-411"）
    BRAND     str            顶栏左侧品牌文字（可选，默认由 TITLE 推导）
    INTRO     list[str]      稿纸头部的说明段落（HTML 片段，不含 <p>）
    SECTIONS  str            正文 HTML（含 <section> 与 .chg 标记）
    CHANGES   dict           每个 data-id 对应的条目

CHANGES 每项必需字段：src / sev / type / cat / loc / before / after / why

校验（任何一项失败即报错退出，不会写出半成品）：
    1. SECTIONS 里每个 data-id 都有 CHANGES 条目
    2. 每个 CHANGES 键都在 SECTIONS 里被用到
    3. 字段完整且 src/sev/type 取值合法
    4. 标签成对闭合
    5. <del>/<ins> 必须包在 .chg 里
    6. 产物零外部引用（离线可用）
"""
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, os.pardir, 'assets', 'template.html')

SEV = ('必改', '建议', '润色')
TYPE = ('新增', '删除', '修改', '结构')
SRC = ('mine', 'codex', 'both')
REQUIRED = ('src', 'sev', 'type', 'cat', 'loc', 'before', 'after', 'why')


def die(msg):
    print('\n✗ ' + msg, file=sys.stderr)
    sys.exit(1)


def load_spec(path):
    spec = importlib.util.spec_from_file_location('review_spec', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for attr in ('TITLE', 'LOC', 'SECTIONS', 'CHANGES'):
        if not hasattr(mod, attr):
            die('review spec 缺少必需变量: %s' % attr)
    return mod


def validate(sections, changes):
    errs = []

    used = list(dict.fromkeys(re.findall(r'data-id="([^"]+)"', sections)))
    keys = list(changes.keys())

    missing = [u for u in used if u not in changes]
    if missing:
        errs.append('SECTIONS 用到但 CHANGES 未定义: %s' % ', '.join(missing))

    orphan = [k for k in keys if k not in used]
    if orphan:
        errs.append('CHANGES 已定义但 SECTIONS 未用到: %s' % ', '.join(orphan))

    for k, v in changes.items():
        for f in REQUIRED:
            if f not in v or v[f] in (None, ''):
                errs.append('%s 缺字段 %s' % (k, f))
        if v.get('src') not in SRC:
            errs.append('%s 的 src=%r 不合法（应为 %s）' % (k, v.get('src'), '/'.join(SRC)))
        if v.get('sev') not in SEV:
            errs.append('%s 的 sev=%r 不合法（应为 %s）' % (k, v.get('sev'), '/'.join(SEV)))
        if v.get('type') not in TYPE:
            errs.append('%s 的 type=%r 不合法（应为 %s）' % (k, v.get('type'), '/'.join(TYPE)))

    for tag in ('span', 'del', 'ins', 'p', 'section', 'div', 'table', 'tr', 'td'):
        o = len(re.findall(r'<%s[ >]' % tag, sections))
        c = len(re.findall(r'</%s>' % tag, sections))
        if o != c:
            errs.append('标签未闭合: <%s> 开 %d 闭 %d' % (tag, o, c))

    # every del/ins must sit inside a .chg span
    stripped = re.sub(r'<span class="chg[^"]*"[^>]*>.*?</span>', '', sections, flags=re.S)
    for tag in ('del', 'ins'):
        stray = len(re.findall(r'<%s[ >]' % tag, stripped))
        if stray:
            errs.append('有 %d 个 <%s> 不在 .chg 标记内（点不开，会变成死标记）' % (stray, tag))

    if errs:
        die('校验未通过：\n  - ' + '\n  - '.join(errs))

    return used


def render(mod, out_path):
    sections = mod.SECTIONS
    changes = mod.CHANGES
    used = validate(sections, changes)

    tpl = open(TEMPLATE, encoding='utf-8').read()

    counts = {s: sum(1 for v in changes.values() if v['sev'] == s) for s in SEV}
    srcs = {s: sum(1 for v in changes.values() if v['src'] == s) for s in SRC}

    intro = getattr(mod, 'INTRO', [])
    intro_html = '\n'.join('    <p%s>%s</p>' % (' style="margin-top:.6rem"' if i else '', t)
                           for i, t in enumerate(intro))

    head = (
        '  <div class="doc-head">\n'
        '    <h1>%s</h1>\n%s\n'
        '    <div class="stats">\n'
        '      <div class="stat"><b id="s-total">0</b><span>处修改</span></div>\n'
        '      <div class="stat crit"><b id="s-crit">0</b><span>必改</span></div>\n'
        '      <div class="stat"><b id="s-sug">0</b><span>建议</span></div>\n'
        '      <div class="stat"><b id="s-pol">0</b><span>润色</span></div>\n'
        '    </div>\n'
        '  </div>\n' % (mod.TITLE, intro_html)
    )

    # DATA literal: json is safe for the rich HTML in `why`
    items = ',\n'.join('  %s: %s' % (k, json.dumps(changes[k], ensure_ascii=False))
                       for k in used)
    data = 'const DATA = {\n%s\n};\n' % items

    key = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(os.path.basename(out_path))[0].lower()).strip('-')

    out = (tpl.replace('@@TITLE@@', mod.TITLE)
              .replace('@@BRAND@@', getattr(mod, 'BRAND', mod.TITLE))
              .replace('@@LOC@@', mod.LOC)
              .replace('@@BODY@@', head + sections)
              .replace('@@DATA@@', data)
              .replace('@@KEY@@', key or 'review'))

    ext = out.count('http://') + out.count('https://') + out.count('<link') + out.count('src=')
    if ext:
        die('产物含 %d 处外部引用，破坏离线可用性' % ext)
    if not out.startswith('<!DOCTYPE html>') or '<meta charset="utf-8">' not in out:
        die('产物缺 DOCTYPE 或 charset（中文会乱码）')

    open(out_path, 'w', encoding='utf-8').write(out)

    print('✓ %s' % out_path)
    print('  %d 处 | 必改 %d / 建议 %d / 润色 %d' %
          (len(used), counts['必改'], counts['建议'], counts['润色']))
    print('  来源: 共识 %d / Codex %d / 本轮 %d' % (srcs['both'], srcs['codex'], srcs['mine']))
    print('  %.1f KB | 零外部引用 | localStorage 键: %s-done' % (len(out.encode()) / 1024, key))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    spec_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else \
        os.path.splitext(spec_path)[0] + '.html'
    render(load_spec(spec_path), out_path)


if __name__ == '__main__':
    main()
