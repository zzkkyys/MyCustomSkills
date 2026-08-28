#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 0 遍：全局机械审计。只用标准库，任何 python3 都能跑。

    python3 audit.py                # 审计当前目录 *.md
    python3 audit.py 本子正文/       # 审计某目录
    python3 audit.py a.md b.md      # 审计指定文件
    python3 audit.py --root 边界 等级 尺度   # 追加自定义词根

报告六类可机械发现的问题：术语漂移、跨节复读、引文编号顺序、
图表引用、体例（加粗编号/破折号/引号）、口语词与程度副词计数。
判断类问题（读不懂、主题句、逻辑矛盾）不在此列，见 references/可读性核对清单.md。
"""
import re, sys, os, glob
from collections import defaultdict, Counter

CJK = r'一-龥'

# 同义词根组：同一前缀若同时配上组内两个不同词根，几乎必是漂移
SYN_GROUPS = [
    ['边界', '范围', '界限'],
    ['等级', '尺度', '标准', '效标', '量表'],
    ['模块', '方式', '部件', '单元'],
    ['信息', '内容'],
    ['机制', '机理'],
    ['规范', '准则'],
    ['能力', '性能'],
]
# 单根多前缀也要看：同一词根挂着多个前缀，往往是同一概念的不同叫法
ROOTS = sorted({r for g in SYN_GROUPS for r in g} |
               {'条件', '关系', '模型', '指标', '分布', '表征', '结论', '身份', '内容'})

ORAL = ['需要说明','需要指出','需要特别指出','值得强调','值得注意','总体而言',
        '综上所述','在此基础上','与此同时','也就是说','换句话说','简而言之']
DEGREE = ['显著','较大','高度','实质性','核心突破','大幅','极大','充分','丰富','坚实']
REPORT = ['陆续','稳步推进','扎实','初步显现','可落地','稳妥','妥善','稳健','切实']
JARGON = ['赋能','抓手','闭环','打法','破圈','底座','链路','组合拳','护城河']


def load(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, '*.md')))
        else:
            files.append(p)
    if not files:
        files = sorted(glob.glob('*.md'))
    return [(f, open(f, encoding='utf-8').read()) for f in files if os.path.isfile(f)]


def strip_marks(t):
    """去掉引文号、行内公式、图片、markdown 标记，只留正文汉字与标点。"""
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?', '', t)
    t = re.sub(r'\\\(.*?\\\)|\\\[.*?\\\]', '', t, flags=re.S)
    t = re.sub(r'\[[0-9,\-\s]+\]', '', t)
    return re.sub(r'[#*`>|]', '', t)


def sec(title):
    print('\n' + '═' * 60 + f'\n{title}\n' + '═' * 60)


def prefixes(docs, root):
    """紧邻词根的 2 字前缀 -> 次数。只保留出现 >=2 次的，滤掉句子碎片。"""
    c = Counter()
    for f, tx in docs:
        for m in re.findall(rf'([{CJK}]{{2}}){root}', strip_marks(tx)):
            c[m] += 1
    return {k: v for k, v in c.items() if v >= 2}


def drift(docs, roots):
    sec('① 术语漂移')
    hit = False

    print('\n  A. 同一前缀配了组内不同词根（信号最强，几乎必是漂移）')
    for g in SYN_GROUPS:
        table = {r: prefixes(docs, r) for r in g}
        common = set()
        for i, r1 in enumerate(g):
            for r2 in g[i + 1:]:
                common |= set(table[r1]) & set(table[r2])
        for pre in sorted(common):
            hit = True
            print(f'     {pre}…  ' + '，'.join(
                f'{pre}{r}×{table[r][pre]}' for r in g if pre in table[r]))
    if not hit:
        print('     未发现。')

    print('\n  B. 同一词根挂了多个前缀（需人工判断是否同义）')
    for r in roots:
        pre = prefixes(docs, r)
        if len(pre) >= 2:
            items = sorted(pre.items(), key=lambda kv: -kv[1])[:6]
            print(f'     …{r}：' + '，'.join(f'{k}{r}×{v}' for k, v in items))

    print('\n  → A 组优先核查（也会误报：同前缀的两个词根未必同义，如“生成方式/生成模块”）；B 组逐组判断。'
          '\n  → 替换后必须复读每个替换点前后各一句：全局替换会在替换点制造新的搭配问题。')


def repeats(docs, n=16):
    sec(f'② 跨节复读：{n} 字以上片段重复出现')
    pos = defaultdict(list)
    for f, tx in docs:
        lines = [l for l in strip_marks(tx).split('\n')
                 if len(re.findall(r'[A-Za-z0-9]', l)) < len(l) * 0.4]  # 滤掉文献表
        s = re.sub(rf'[^{CJK}，、；：]', '', '\n'.join(lines))
        for i in range(len(s) - n + 1):
            pos[s[i:i + n]].append((f, i))
    dup = {g: v for g, v in pos.items() if len(v) > 1}
    merged, seen = [], set()
    for g in sorted(dup, key=lambda g: dup[g][0][1]):
        if g in seen:
            continue
        seg, cur = g, dup[g]
        while True:
            nxt = None
            for cand, v in dup.items():
                if cand in seen or len(v) != len(cur):
                    continue
                if all(a[0] == b[0] and a[1] == b[1] + 1 for a, b in zip(v, cur)):
                    nxt = cand
                    break
            if not nxt:
                break
            seen.add(nxt); seg += nxt[-1]; cur = dup[nxt]
        seen.add(g)
        merged.append((seg, [f for f, _ in dup[g]]))
    if not merged:
        print('  未发现。')
    for seg, fs in sorted(merged, key=lambda x: -len(x[0])):
        where = '、'.join(sorted(set(os.path.basename(f) for f in fs)))
        print(f'  ×{len(fs)}  {where}\n       {seg}')
    if merged:
        print('\n  → 先区分两种情况：'
              '\n     · 固定术语串（如三个评价维度连写）重复出现是正常的，跳过；'
              '\n     · 同一句判断在不同章节复现，是 AI 生成稿的签名，只留在证据最足的地方'
              '（需文献支撑的留在综述节）。')


def citations(docs):
    sec('③ 引文编号：是否按正文首次出现顺序排列')
    order, seen = [], set()
    for f, t in docs:
        for grp in re.findall(r'\[([0-9][0-9,\-\s]*)\]', t):
            for part in grp.split(','):
                part = part.strip()
                if not part:
                    continue
                if '-' in part:
                    a, b = part.split('-')[:2]
                    if a.strip().isdigit() and b.strip().isdigit():
                        rng = range(int(a), int(b) + 1)
                    else:
                        continue
                else:
                    rng = [int(part)] if part.isdigit() else []
                for k in rng:
                    if k not in seen:
                        seen.add(k); order.append((k, os.path.basename(f)))
    bad = [(k, f) for i, (k, f) in enumerate(order) if i and k < order[i - 1][0]]
    print('  首次出现顺序：' + '、'.join(str(k) for k, _ in order[:24]) +
          (' …' if len(order) > 24 else ''))
    if bad:
        print(f'  ⚠ {len(bad)} 处编号早于其前序：' +
              '、'.join(f'[{k}]({f})' for k, f in bad[:8]))
        print('  → 定稿前按正文首次引用顺序重排文献表。')
    else:
        print('  顺序正常。')


def figures(docs):
    sec('④ 图表：孤图与重复图题')
    for f, t in docs:
        base = os.path.basename(f)
        imgs = re.findall(r'!\[([^\]]*)\]', t)
        body = re.sub(r'!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?', '', t)
        for alt in imgs:
            m = re.search(r'图\s*(\d+)', alt)
            if not m:
                continue
            no = m.group(1)
            if not re.search(rf'图\s*{no}\s*(所示|中|：|。|、)', body):
                print(f'  ⚠ {base}：图{no} 未被正文引用（缺“如图{no}所示”一类交代）')
            if re.search(rf'^\s*图\s*{no}[^\n]*$', body, re.M):
                print(f'  ⚠ {base}：图{no} 另起一行又写了一遍图题，转 docx 会出现两个题注')
    print('  （无输出即通过）')


def style(docs):
    sec('⑤ 体例计数')
    for f, t in docs:
        b = os.path.basename(f)
        print(f'  {b}: 加粗编号小标题 {len(re.findall(r"\*\*[（(]?[一二三四五六0-9]", t))}'
              f'  破折号 {t.count("——")}'
              f'  中文引号 {t.count(chr(0x201c))} 对'
              f'  加粗段 {len(re.findall(r"\*\*[^*]+\*\*", t))}')
    print('  → 加粗应只标一句关键判断，不覆盖整块；同一文稿加粗位置（段首/段末）保持一致。')


def words(docs):
    sec('⑥ 口语词、程度副词、汇报腔、黑话')
    for name, lst in (('口语衔接', ORAL), ('程度副词', DEGREE),
                      ('汇报腔', REPORT), ('管理黑话', JARGON)):
        c = Counter()
        for f, t in docs:
            for w in lst:
                n = strip_marks(t).count(w)
                if n:
                    c[w] += n
        print(f'  {name}：' + ('、'.join(f'{k}×{v}' for k, v in c.most_common()) if c else '无'))


def main():
    args = sys.argv[1:]
    roots = list(ROOTS)
    skip = []
    if '--skip' in args:
        i = args.index('--skip')
        skip = args[i + 1:]
        args = args[:i]
    if '--root' in args:
        i = args.index('--root')
        roots += args[i + 1:]
        args = args[:i]
    docs = [(f, x) for f, x in load(args)
            if not any(s in os.path.basename(f) for s in skip)]
    if not docs:
        print('没找到 .md 文件'); return
    print(f'审计 {len(docs)} 个文件：' + '、'.join(os.path.basename(f) for f, _ in docs))
    drift(docs, roots); repeats(docs); citations(docs)
    figures(docs); style(docs); words(docs)
    print('\n以上均为机械可查项。判断类问题见 references/可读性核对清单.md。')


if __name__ == '__main__':
    main()
