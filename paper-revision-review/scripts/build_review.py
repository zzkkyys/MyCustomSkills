#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_review.py —— 把一份审阅稿（review spec）渲染成单文件离线审阅页。

要求 Python 3.8+。

用法：
    python3 build_review.py <review_spec.py> [输出路径.html]

review spec 是一个 Python 文件，需定义：
    TITLE     str            页面标题 / 稿纸大标题
    LOC       str            顶栏右侧的定位（如 "main.tex:294-411"）
    BRAND     str            顶栏左侧品牌文字（可选，默认取 TITLE）
    INTRO     list[str]      稿纸头部的说明段落（可选，允许有限富文本）
    SECTIONS  str            正文 HTML（含 <section> 与 .chg 标记）
    CHANGES   dict[str,dict] 每个 data-id 对应的条目

安全边界：
    SECTIONS 走正面白名单：只允许受限的排版标签与 class/data-id/data-type
    三个属性，其余标签与属性（含 on*、src、href、style、srcdoc）一律拒绝，
    因此不存在脚本、事件处理器或外部资源。
    TITLE / BRAND / LOC / before / after 一律作为纯文本处理（逐字保真）。
    INTRO 与 why 经富文本白名单过滤，只保留无属性的排版标签。
"""
import hashlib
import html
import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / 'assets' / 'template.html'

SEV = ('必改', '建议', '润色')
TYPE = ('新增', '删除', '修改', '结构')
SRC = ('mine', 'second', 'both')
REQUIRED = ('src', 'sev', 'type', 'cat', 'loc', 'before', 'after', 'why')

# 富文本白名单：只允许无属性的排版标签
ALLOWED = {'strong', 'em', 'b', 'i', 'u', 'code', 'small', 'sub', 'sup',
           'br', 'p', 'ul', 'ol', 'li', 'table', 'thead', 'tbody',
           'tr', 'td', 'th'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'}

# SECTIONS 采用正面白名单：只认审阅页真正需要的标签与属性，其余一律拒绝。
# 这样无需追着 script/svg/iframe/srcdoc/on*/@import 逐个枚举。
SEC_TAGS = {'section', 'div', 'p', 'h2', 'h3', 'h4', 'span', 'del', 'ins',
            'br', 'strong', 'em', 'b', 'i', 'u', 'code', 'small', 'sub', 'sup',
            'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'td', 'th'}
SEC_ATTRS = {'class', 'data-id', 'data-type'}
# 这三个键在 JS 对象字面量里有特殊语义，不能作为 data-id
RESERVED_IDS = {'__proto__', 'constructor', 'prototype'}


def die(msg):
    print('\n✗ ' + msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- 富文本过滤
class Sanitizer(HTMLParser):
    """保留白名单标签（一律去掉属性），其余标签丢弃、文本保留。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.open = []

    def handle_starttag(self, tag, attrs):
        if tag in ALLOWED:
            self.out.append('<%s>' % tag)
            if tag not in VOID:
                self.open.append(tag)

    def handle_endtag(self, tag):
        if tag in ALLOWED and tag not in VOID and tag in self.open:
            while self.open:
                t = self.open.pop()
                self.out.append('</%s>' % t)
                if t == tag:
                    break

    def handle_data(self, data):
        self.out.append(html.escape(data, quote=False))

    def result(self):
        while self.open:
            self.out.append('</%s>' % self.open.pop())
        return ''.join(self.out)


def clean(text):
    s = Sanitizer()
    s.feed(str(text))
    s.close()
    return s.result()


# ---------------------------------------------------------------- 结构校验
class ReviewParser(HTMLParser):
    """校验 SECTIONS：标记完整性、嵌套正确性、有无外部资源。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.used = []
        self.seen = set()
        self.errs = []
        self.chg_depth = 0

    def handle_starttag(self, tag, attrs):
        # 逐个遍历原始 attrs，不转 dict —— dict() 会丢掉重复属性，
        # 而浏览器取的是第一个、dict 取的是最后一个，可被用来绕过检查。
        seen_attrs = set()
        a = {}
        for raw_name, raw_val in attrs:
            name = raw_name.lower()
            if name in seen_attrs:
                self.errs.append('<%s> 出现重复属性 %s' % (tag, name))
            seen_attrs.add(name)
            a.setdefault(name, raw_val or '')
            if name not in SEC_ATTRS:
                self.errs.append('<%s> 不允许属性 %s（SECTIONS 只接受 %s）'
                                 % (tag, name, '/'.join(sorted(SEC_ATTRS))))

        if tag not in SEC_TAGS:
            self.errs.append('SECTIONS 不允许标签 <%s>（只接受受限的排版标签）' % tag)

        classes = set((a.get('class') or '').split())
        is_chg = 'chg' in classes

        if is_chg:
            if self.chg_depth:
                self.errs.append('不允许嵌套 .chg 标记')
            ident = a.get('data-id')
            if not ident:
                self.errs.append('.chg 缺少 data-id')
            elif ident not in self.seen:
                self.seen.add(ident)
                self.used.append(ident)
        elif a.get('data-id'):
            self.errs.append('data-id="%s" 所在元素没有 class="chg"，不会被识别为改动'
                             % a['data-id'])

        if tag in ('del', 'ins') and not self.chg_depth:
            self.errs.append('<%s> 不在 .chg 内（点不开，会变成死标记）' % tag)

        if tag not in VOID:
            self.stack.append((tag, is_chg))
            self.chg_depth += int(is_chg)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack:
            t, is_chg = self.stack.pop()
            self.chg_depth -= int(is_chg)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errs.append('多余的结束标签 </%s>' % tag)
            return
        if self.stack[-1][0] != tag:
            self.errs.append('标签嵌套错误：期望 </%s>，遇到 </%s>' % (self.stack[-1][0], tag))
            return
        _, is_chg = self.stack.pop()
        self.chg_depth -= int(is_chg)

    def finish(self):
        for tag, _ in self.stack:
            self.errs.append('标签未闭合：<%s>' % tag)
        return self.used, self.errs


# ---------------------------------------------------------------- 载入与校验
def load_spec(path):
    spec = importlib.util.spec_from_file_location('review_spec', path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        die('review spec 执行失败：%s: %s' % (type(exc).__name__, exc))

    for name, typ in (('TITLE', str), ('LOC', str), ('SECTIONS', str), ('CHANGES', dict)):
        if not hasattr(mod, name):
            die('review spec 缺少必需变量：%s' % name)
        if not isinstance(getattr(mod, name), typ):
            die('%s 类型错误：应为 %s，实际为 %s'
                % (name, typ.__name__, type(getattr(mod, name)).__name__))

    intro = getattr(mod, 'INTRO', [])
    if not isinstance(intro, list) or not all(isinstance(x, str) for x in intro):
        die('INTRO 类型错误：应为 list[str]')
    if hasattr(mod, 'BRAND') and not isinstance(mod.BRAND, str):
        die('BRAND 类型错误：应为 str')
    return mod


def validate(sections, changes):
    errs = []

    if not changes:
        errs.append('CHANGES 不能为空')

    bad_keys = [k for k in changes
                if not (isinstance(k, str)
                        and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', k))]
    if bad_keys:
        errs.append('data-id 只接受 ASCII 字母、数字、下划线与连字符（首字符不能是数字）：%s'
                    % ', '.join(map(repr, bad_keys[:5])))
    reserved = [k for k in changes if k in RESERVED_IDS]
    if reserved:
        errs.append('data-id 不能使用 %s —— 它们在 JS 对象字面量里有特殊语义'
                    % ', '.join(map(repr, reserved)))

    for k, v in changes.items():
        if not isinstance(v, dict):
            errs.append('%r 的条目必须是 dict，实际为 %s' % (k, type(v).__name__))
            continue
        for f in REQUIRED:
            val = v.get(f)
            if not isinstance(val, str) or not val.strip():
                errs.append('%s 的 %s 必须是非空字符串' % (k, f))
        for f, allowed in (('src', SRC), ('sev', SEV), ('type', TYPE)):
            if isinstance(v.get(f), str) and v[f] not in allowed:
                errs.append('%s 的 %s=%r 不合法（应为 %s）' % (k, f, v[f], '/'.join(allowed)))

    p = ReviewParser()
    p.feed(sections)
    p.close()
    used, perrs = p.finish()
    errs.extend(perrs)

    missing = [u for u in used if u not in changes]
    if missing:
        errs.append('SECTIONS 用到但 CHANGES 未定义：%s' % ', '.join(missing))
    orphan = [k for k in changes if k not in used]
    if orphan:
        errs.append('CHANGES 已定义但 SECTIONS 未用到：%s' % ', '.join(map(str, orphan)))

    if errs:
        die('校验未通过：\n  - ' + '\n  - '.join(dict.fromkeys(errs)))
    return used


# ---------------------------------------------------------------- 渲染
def js_payload(obj):
    r"""JSON 转成可安全嵌入 <script> 的字面量。

    < > & 转成 \uXXXX，防止 </script> 提前闭合脚本或注入标签；
    U+2028/U+2029 在 JS 里是行终止符，也必须转义。
    """
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    for ch, esc in (('&', '\\u0026'), ('<', '\\u003c'), ('>', '\\u003e'),
                    ('\u2028', '\\u2028'), ('\u2029', '\\u2029')):
        s = s.replace(ch, esc)
    return s


def render(mod, out_path):
    out_file = Path(out_path)
    if out_file.suffix.lower() not in ('.html', '.htm'):
        die('输出路径必须以 .html 或 .htm 结尾（否则浏览器按纯文本打开）')

    used = validate(mod.SECTIONS, mod.CHANGES)
    # before/after 必须逐字保真（前端已用 esc() 转义），只有 why 走富文本白名单
    changes = {k: {f: clean(mod.CHANGES[k][f]) if f == 'why' else mod.CHANGES[k][f]
                   for f in REQUIRED} for k in used}

    tpl = TEMPLATE.read_text(encoding='utf-8')

    counts = {s: sum(1 for v in changes.values() if v['sev'] == s) for s in SEV}
    srcs = {s: sum(1 for v in changes.values() if v['src'] == s) for s in SRC}

    intro_html = '\n'.join('    <div class="intro%s">%s</div>'
                           % (' spaced' if i else '', clean(t))
                           for i, t in enumerate(getattr(mod, 'INTRO', [])))

    head = ('  <div class="doc-head">\n    <h1>%s</h1>\n%s\n'
            '    <div class="stats">\n'
            '      <div class="stat"><b id="s-total">0</b><span>处修改</span></div>\n'
            '      <div class="stat crit"><b id="s-crit">0</b><span>必改</span></div>\n'
            '      <div class="stat"><b id="s-sug">0</b><span>建议</span></div>\n'
            '      <div class="stat"><b id="s-pol">0</b><span>润色</span></div>\n'
            '    </div>\n  </div>\n' % (html.escape(mod.TITLE), intro_html))

    stem = out_file.stem
    slug = re.sub(r'[^a-z0-9]+', '-', stem.lower()).strip('-') or 'review'
    digest = hashlib.sha256((stem + '\0' + mod.TITLE).encode('utf-8')).hexdigest()[:10]
    key = '%s-%s' % (slug, digest)

    out = (tpl.replace('@@TITLE@@', html.escape(mod.TITLE))
              .replace('@@BRAND@@', html.escape(getattr(mod, 'BRAND', mod.TITLE)))
              .replace('@@LOC@@', html.escape(mod.LOC))
              .replace('@@BODY@@', head + mod.SECTIONS)
              .replace('@@DATA@@', 'const DATA = %s;\n' % js_payload(changes))
              .replace('@@KEY@@', key))

    for ph in ('@@TITLE@@', '@@BRAND@@', '@@LOC@@', '@@BODY@@', '@@DATA@@', '@@KEY@@'):
        if ph in out:
            die('模板占位符 %s 未被替换' % ph)
    ends = re.findall(r'(?i)</script\s*>', out)
    if len(ends) != 1:
        die('产物含 %d 处脚本结束标签，脚本会提前闭合' % len(ends))
    if not out.startswith('<!DOCTYPE html>') or '<meta charset="utf-8">' not in out:
        die('产物缺 DOCTYPE 或 charset（中文会乱码）')

    try:
        out_file.write_text(out, encoding='utf-8')
    except OSError as exc:
        die('无法写入 %s：%s' % (out_file, exc))

    print('✓ %s' % out_file)
    print('  %d 处 | 必改 %d / 建议 %d / 润色 %d'
          % (len(used), counts['必改'], counts['建议'], counts['润色']))
    print('  来源: 共识 %d / 第二意见 %d / 本轮 %d' % (srcs['both'], srcs['second'], srcs['mine']))
    print('  %.1f KB | 无外部资源 | localStorage 键: %s-done' % (len(out.encode()) / 1024, key))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    spec = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else spec.with_suffix('.html')
    render(load_spec(str(spec)), out)


if __name__ == '__main__':
    main()
