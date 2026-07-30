# -*- coding: utf-8 -*-
"""
完整功能演示 —— 四类标记、三档严重程度、三种来源、why 里的表格、
同一 id 用于多处、snip 节选提示。用一份虚构稿件作素材。

    python3 ../scripts/build_review.py demo_review.py /tmp/demo.html
"""

TITLE = '第二章 &nbsp;Method — 修订标记（演示）'
BRAND = 'DemoPaper · 第二章'
LOC = 'paper.tex:120–186'

INTRO = [
    '这是一份<strong>演示页</strong>，用虚构稿件展示本 skill 生成的审阅页长什么样。'
    '正文中的改动以内联标记呈现，点任意一处，右侧批注栏会显示原文、改后文本与修改理由。',
    '<strong>本章问题集中在两处</strong>：一是记号系统（同一个量两个符号、用到但没定义），'
    '二是评价性措辞超出了数据支撑的范围。'
    '试试顶栏的<strong>终稿视图</strong>——它会隐藏删除内容，让你直接读改完的连贯版本。',
]

SECTIONS = r'''
  <section>
    <div class="sec-head">
      <h2>2.1 &nbsp;Problem Setup</h2>
      <span class="loc">paper.tex:120–134</span>
      <span class="sec-note">全段</span>
    </div>
    <p class="prose">
Let <span class="chg" data-id="d1"><del>D</del><ins>\mathcal{D}</ins></span> denote the observation set collected over
<span class="chg" data-id="d2"><del>T</del><ins>T</ins></span> consecutive intervals.
<span class="chg" data-id="d3"><ins> Throughout, $\mathcal{X}$ denotes the underlying data distribution from which $\mathcal{D}$ is drawn independently.</ins></span>
Each observation is mapped to a latent state by an encoder
<span class="chg" data-id="d4"><del>whose architecture we describe later</del><ins>$f_\theta$, specified in Section 2.3</ins></span>.
<span class="snip">〔中间三句无需改动〕</span>
The estimator is <span class="chg" data-id="d5"><del>obviously more stable than all prior approaches</del><ins>more stable than the three baselines we evaluate</ins></span>
under distribution shift.
    </p>

    <span class="chg brk" data-id="d6" data-type="结构"><ins>¶ 建议此处另起一段：前半是问题设定，后半已进入方法描述</ins></span>

    <p class="prose">
We estimate the transition kernel by minimizing the empirical risk over
<span class="chg" data-id="d2"><del>T</del><ins>T</ins></span> windows, where the window length is a hyperparameter
<span class="chg" data-id="d7"><del>\epsilon</del><ins>w</ins></span> fixed to 12 throughout.
    </p>
  </section>

  <section>
    <div class="sec-head">
      <h2>2.2 &nbsp;Algorithm</h2>
      <span class="loc">paper.tex:150–170</span>
      <span class="sec-note">伪代码与正文描述</span>
    </div>
    <p class="prose">
<span class="snip">〔正文，:152〕</span> To <span class="chg" data-id="d8"><del>optimally determine the window length, we design an adaptive procedure</del><ins>select a data-dependent window length, we use a heuristic stopping rule</ins></span>
that scans candidate values in increasing order.
    </p>
    <p class="prose">
<span class="snip">〔伪代码，:161–166〕</span> \For{$i \gets 1$ \textbf{to} $L$}
&nbsp;&nbsp;\If{$\eta^{(i)} &gt; \xi$} \State \textbf{break} \EndIf
\EndFor
\State \textbf{return} <span class="chg" data-id="d9"><del>$k$</del><ins>$i$（并在循环正常结束时显式 \textbf{return} $L$）</ins></span>
    </p>
  </section>

  <section>
    <div class="sec-head">
      <h2>跨小节记号</h2>
      <span class="loc">paper.tex:134 / :158 / :181</span>
      <span class="sec-note">同一符号三处不一致</span>
    </div>
    <p class="prose">
<span class="snip">〔:134〕</span> window length <span class="chg" data-id="d7"><del>\epsilon</del><ins>w</ins></span>
&nbsp;&nbsp;<span class="snip">〔:158〕</span> threshold <span class="chg" data-id="d7"><del>\epsilon</del><ins>\xi</ins></span>
&nbsp;&nbsp;<span class="snip">〔:181〕</span> tolerance <span class="chg" data-id="d7"><del>\epsilon</del><ins>\tau</ins></span>
    </p>
  </section>
'''

CHANGES = {
    'd1': dict(
        src='mine', sev='润色', type='修改', cat='记号风格',
        loc='paper.tex:120',
        before='Let D denote the observation set …',
        after=r'Let $\mathcal{D}$ denote the observation set …',
        why='全文其他集合都用花体（$\\mathcal{X}$、$\\mathcal{Y}$），只有观测集用了正体 D。'
            '不影响理解，但在一篇记号密集的稿子里，风格摇摆会削弱严谨印象。',
    ),
    'd2': dict(
        src='mine', sev='润色', type='修改', cat='首次出现未说明',
        loc='paper.tex:121（另见 :148）',
        before='over T consecutive intervals … over T windows',
        after='首次出现处补一句说明 $T$ 是什么（区间总数？时间跨度？）',
        why='$T$ 在两处出现，含义看起来一致，但从未定义。'
            '<br><br>这条演示了<strong>同一个 <code>data-id</code> 用在多个位置</strong>：'
            '点任意一处，两处会同时高亮，编号也相同。'
            '适合「同一个词要在三处统一」这类改动。',
    ),
    'd3': dict(
        src='both', sev='必改', type='新增', cat='符号未定义',
        loc='paper.tex:122',
        before='（原文无此内容）后文的 $\\mathcal{X}$ 直接出现在定理陈述里，从未定义。',
        after=r'Throughout, $\mathcal{X}$ denotes the underlying data distribution from which $\mathcal{D}$ is drawn independently.',
        why='<strong>$\\mathcal{X}$ 是理论部分所有概率的取值空间，却从未定义。</strong>'
            '读者只能靠符号形状猜。<br><br>'
            '理论审稿人对未定义的概率空间尤其敏感——不知道概率对什么取，'
            '定理里的 $\\Pr(\\cdot)\\geq 1-\\rho$ 就无法判断强弱。<br><br>'
            '补一个从句即可，零成本。同时点明是<strong>独立同分布抽样</strong>，'
            '这是后面用经验量估计总体量的前提。',
    ),
    'd4': dict(
        src='mine', sev='建议', type='修改', cat='前向指代不明',
        loc='paper.tex:126',
        before='… by an encoder whose architecture we describe later.',
        after=r'… by an encoder $f_\theta$, specified in Section 2.3.',
        why='「we describe later」没说是哪一节，读者要往后翻着找。'
            '同时这里就该给编码器一个符号——后文的损失函数要用到它，'
            '否则到那时又得临时引入。',
    ),
    'd5': dict(
        src='second', sev='必改', type='修改', cat='overclaim',
        loc='paper.tex:131',
        before='The estimator is obviously more stable than all prior approaches under distribution shift.',
        after='The estimator is more stable than the three baselines we evaluate under distribution shift.',
        why='<strong>两个问题叠在一起。</strong><br><br>'
            '<strong>其一，<em>all prior approaches</em> 是全称判断</strong>，'
            '需要穷尽文献才站得住，一个反例就能推翻——而这句话恰恰是本文卖点的支点。<br><br>'
            '<strong>其二，<em>obviously</em> 在实验科学写作里是危险词</strong>：'
            '它暗示「不证自明」，而审稿人的第一反应恰恰是「凭什么」。<br><br>'
            '改成陈述实际测了什么，声称更小但站得住。'
            '<br><br><em>（这条由第二意见提出，本轮初审漏掉了。）</em>',
    ),
    'd6': dict(
        src='mine', sev='建议', type='结构', cat='段落切分',
        loc='paper.tex:120–134',
        before='问题设定与方法描述写在同一段，约 240 词。',
        after='在 “under distribution shift.” 之后断开，“We estimate the transition kernel…” 起新段。',
        why='双栏排版下 240 词是一整栏的密集文字，读者难以定位重点。'
            '<br><br>按内容切分刚好是两件事：<strong>前段＝问题设定</strong>（有哪些对象、什么记号），'
            '<strong>后段＝方法</strong>（怎么估计）。切开后每段各有一个明确的主题句。'
            '<br><br>这条演示的是<strong>结构类标记</strong>：独占一行、紫色，用于段落级调整。',
    ),
    'd7': dict(
        src='both', sev='必改', type='修改', cat='符号冲突',
        loc='paper.tex:134 / :158 / :181（3 处）',
        before='$\\epsilon$ 在三处分别表示窗口长度、判定阈值、容差。',
        after='分别改为 $w$（窗口长度）、$\\xi$（阈值）、$\\tau$（容差）。',
        why='<strong>同一个符号 $\\epsilon$ 在全文有三个互不相干的含义：</strong>'
            '<table>'
            '<tr><th>位置</th><th>含义</th><th>取值</th></tr>'
            '<tr><td>:134</td><td>窗口长度</td><td>12</td></tr>'
            '<tr><td>:158</td><td>判定阈值</td><td>0.6</td></tr>'
            '<tr><td>:181</td><td>数值容差</td><td>1e-6</td></tr>'
            '</table>'
            '三者取值相差好几个数量级，读者在章节之间对照时极易张冠李戴——'
            '尤其 :158 和 :181 都出现在算法描述附近。<br><br>'
            '<em>（这条演示 <code>why</code> 里可以用小表格做对照。'
            '表格样式由模板提供，不需要写内联 style——属性会被过滤掉。）</em>',
    ),
    'd8': dict(
        src='second', sev='必改', type='修改', cat='措辞与算法不符',
        loc='paper.tex:152',
        before='To optimally determine the window length, we design an adaptive procedure that scans candidate values in increasing order.',
        after='To select a data-dependent window length, we use a heuristic stopping rule that scans candidate values in increasing order.',
        why='算法返回的是<strong>第一个</strong>越过阈值的候选值，这是个停止规则，'
            '不是任何优化问题的解。但正文用了 <em>optimally</em>。<br><br>'
            '审稿人会追问：相对什么目标最优？有没有与固定取值的对照实验？'
            '——而这恰恰会引出一个本文没做的消融。<br><br>'
            '<strong>把措辞降级反而省事</strong>：降级后就不需要那个消融了。',
    ),
    'd9': dict(
        src='mine', sev='必改', type='修改', cat='伪代码缺陷',
        loc='paper.tex:161–166',
        before='循环内 break 后 \\textbf{return} $k$；若所有候选都不越阈值，返回值靠循环变量终值隐式决定。',
        after='命中时 \\textbf{return} $i$；循环正常结束后显式 \\textbf{return} $L$。',
        why='<strong>边界情形没写明。</strong>如果没有任何候选越过阈值，'
            '循环正常结束，此时返回什么？现在靠的是循环变量的终值——'
            '读者必须自己推演才能知道。<br><br>'
            '而这恰恰是最该说清楚的情形：它对应「输入本身不具备该性质」，'
            '正是方法要正确处理的边界。<br><br>'
            '把两个返回点都写显式，行数还更少。',
    ),
}
