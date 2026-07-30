# -*- coding: utf-8 -*-
"""
最小可运行示例 —— 复制这个文件改内容即可。

    python3 ../scripts/build_review.py example_review.py /tmp/demo.html
"""

TITLE = '示例章节 · 修订标记'
BRAND = 'DemoPaper · 示例章'
LOC = 'main.tex:100-120'

INTRO = [
    '本页面演示四种标记类型与点击查看理由。'
    '<strong>标记视图</strong>同时显示原文与改写；<strong>终稿视图</strong>只读改完的连贯版本。',
    '<strong>这里放一句判断</strong>——把本章问题的性质先讲清楚，而不是罗列数量。',
]

# ---------------------------------------------------------------- 正文标记
# 约定：
#   修改 → <span class="chg" data-id="x"><del>旧</del><ins>新</ins></span>
#   新增 → <span class="chg" data-id="x"><ins>新</ins></span>
#   删除 → <span class="chg" data-id="x"><del>旧</del></span>
#   结构 → <span class="chg brk" data-id="x" data-type="结构"><ins>¶ 说明</ins></span>
#   同一 data-id 可用于多个 span（点击时会一起高亮）
#   <span class="snip">〔节选提示〕</span> 用于标出被省略的上下文

SECTIONS = r'''
  <section>
    <div class="sec-head">
      <h2>示例小节</h2>
      <span class="loc">main.tex:100-110</span>
      <span class="sec-note">全段</span>
    </div>
    <p class="prose">
<span class="snip">〔节选〕</span> Training <span class="chg" data-id="d1"><del>DNNs</del><ins>deep neural networks (DNNs)</ins></span>
from scratch is costly<span class="chg" data-id="d2"><ins>, which motivates the widespread reuse of pretrained checkpoints</ins></span>.
The method is <span class="chg" data-id="d3"><del>obviously superior to all prior work</del></span> effective.
    </p>

    <span class="chg brk" data-id="d4" data-type="结构"><ins>¶ 建议此处另起一段</ins></span>

    <p class="prose">
Motivated by this, we propose a detector that needs only forward passes.
    </p>
  </section>
'''

# ---------------------------------------------------------------- 条目
# src: mine | second | both     （本轮提出 / 第二意见提出 / 双方共识）
# sev: 必改 | 建议 | 润色
# type: 修改 | 新增 | 删除 | 结构
# why 支持行内 HTML：<strong> <em> <br> <table>

CHANGES = {
    'd1': dict(
        src='mine', sev='必改', type='修改', cat='缩写未定义',
        loc='main.tex:101',
        before='Training DNNs from scratch is costly.',
        after='Training deep neural networks (DNNs) from scratch is costly.',
        why='DNNs 是全文首次出现却直接用了缩写，正文再未展开过。'
            '这是最容易被审稿人挑的形式问题之一，首次出现处必须给全称。',
    ),
    'd2': dict(
        src='both', sev='建议', type='新增', cat='动机链条',
        loc='main.tex:101',
        before='（原文无此内容）',
        after='…, which motivates the widespread reuse of pretrained checkpoints.',
        why='从“训练贵”到“所以复用”的因果没有写出来，读者要自己补。'
            '<br><br>补半句话即可闭合，成本几乎为零。',
    ),
    'd3': dict(
        src='second', sev='必改', type='删除', cat='overclaim',
        loc='main.tex:103',
        before='The method is obviously superior to all prior work effective.',
        after='The method is effective.',
        why='<strong>两个问题叠在一起。</strong><br><br>'
             '<strong>其一</strong>，<em>obviously superior to all prior work</em> 是全称判断，'
             '需要穷尽文献才站得住，一个反例就能推翻。<br><br>'
             '<strong>其二</strong>，删掉后句子才通顺——原句 '
             '<em>is obviously superior … effective</em> 语法本身就不成立。',
    ),
    'd4': dict(
        src='mine', sev='润色', type='结构', cat='段落切分',
        loc='main.tex:103',
        before='现象与方法写在同一段，约 250 词。',
        after='在 “effective.” 之后断开，“Motivated by this…” 起新段。',
        why='双栏排版下 250 词是一整栏的密集文字，审稿人难以定位重点。'
            '按内容切分刚好是两件事：<strong>前段＝观察</strong>，<strong>后段＝方法</strong>。',
    ),
}
