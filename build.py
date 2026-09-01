# -*- coding: utf-8 -*-
"""lie_types.json + cell_metaphors.json 에서 앱과 웹페이지를 생성한다.

    python build.py

내용을 고칠 때는 JSON만 고치고 이걸 다시 돌린다.
앱 사이드바 · AI 프롬프트 · 웹페이지의 정의가 어긋날 수 없다.
"""
import html as _html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(HERE, 'book_analysis_app.html')
WEB = os.path.join(HERE, 'web')

START, END = '/* __LIE_DATA_START__ */', '/* __LIE_DATA_END__ */'


def load(name):
    with open(os.path.join(HERE, name), encoding='utf-8') as f:
        return json.load(f)


def esc(s):
    return _html.escape(str(s), quote=False)


# ── 다크 테마용 색 보정 ──────────────────────────────────────
def lighten(hexcolor, amount=0.55):
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (min(255, int(c + (255 - c) * amount)) for c in (r, g, b))
    return '#%02X%02X%02X' % (r, g, b)


def darken(hexcolor, factor=0.19):
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02X%02X%02X' % tuple(int(c * factor) for c in (r, g, b))


# ── 1. 앱에 데이터 주입 ──────────────────────────────────────
def patch_app(lies, cells):
    with open(APP, encoding='utf-8') as f:
        s = f.read()

    block = (START + '\n'
             '// build.py가 lie_types.json / cell_metaphors.json에서 생성한다.\n'
             '// 직접 고치지 마라. JSON을 고치고 build.py를 다시 돌려라.\n'
             'const LIE_DATA = ' + json.dumps(lies, ensure_ascii=False, indent=2) + ';\n'
             'const LIE_FAMILIES = LIE_DATA.families;\n'
             'const CELL_DATA = ' + json.dumps(cells, ensure_ascii=False, indent=2) + ';\n'
             'const CELL_NEEDS = CELL_DATA.needs;\n'
             + END)

    if START not in s:
        sys.exit('앱에서 데이터 블록 표시를 찾지 못했습니다.')
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda m: block, s, flags=re.S)

    with open(APP, 'w', encoding='utf-8') as f:
        f.write(s)
    return len(block)


# ── 2. 공통 페이지 껍데기 ────────────────────────────────────
BASE_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
     font-size:17px;line-height:1.75;word-break:keep-all;-webkit-text-size-adjust:100%}
.wrap{max-width:34rem;margin:0 auto;padding:2.5rem 1.25rem 5rem;
      display:flex;flex-direction:column;gap:2.75rem}
.masthead{display:flex;flex-direction:column;gap:.5rem}
.eyebrow{font-size:.75rem;letter-spacing:.14em;color:var(--ink-3);font-weight:700}
h1{margin:0;font-size:2.1rem;line-height:1.2;letter-spacing:-.02em;font-weight:800;text-wrap:balance}
.standfirst{margin:0;color:var(--ink-2);font-size:1rem}
section{display:flex;flex-direction:column;gap:1rem}
h2{margin:0;font-size:1.35rem;line-height:1.35;font-weight:800;text-wrap:balance}
p{margin:0}
.lede{color:var(--ink-2)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:.75rem;
      padding:1.15rem 1.2rem;display:flex;flex-direction:column;gap:.8rem}
.chips{display:flex;flex-wrap:wrap;gap:.3rem}
.chip{font-size:.74rem;color:var(--ink-3);background:var(--line-soft);
      border-radius:1rem;padding:.15rem .55rem}
footer{border-top:1px solid var(--line);padding-top:1.25rem;
       color:var(--ink-3);font-size:.85rem;line-height:1.7}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.85rem;min-width:20rem}
th{text-align:left;font-weight:800;color:var(--ink-3);font-size:.72rem;
   letter-spacing:.04em;padding:.5rem .6rem;border-bottom:1px solid var(--line)}
td{padding:.5rem .6rem;border-bottom:1px solid var(--line-soft);
   color:var(--ink-2);vertical-align:top}
td b{color:var(--ink)}
@media (max-width:400px){h1{font-size:1.8rem}}
"""


def page(title, palette_vars, palette_dark, body):
    return """<title>{title}</title>
<style>
:root{{
  --paper:#FBFAF7; --surface:#FFFFFF; --line:#E6E2D8; --line-soft:#F1EDE4;
  --ink:#1B1A17; --ink-2:#4A4740; --ink-3:#7A766C;
  --said:#B5372B; --said-bg:#FBEDEA; --real:#2F6B4F; --real-bg:#EAF3EC;
{pv}
  --sans:'Pretendard','Pretendard Variable',-apple-system,'Apple SD Gothic Neo',
         'Malgun Gothic','맑은 고딕','Noto Sans KR',system-ui,sans-serif;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#141311; --surface:#1C1B18; --line:#302E29; --line-soft:#242220;
    --ink:#F0EDE5; --ink-2:#C4C0B6; --ink-3:#8E8A80;
    --said:#E98A7C; --said-bg:#31201D; --real:#8FC5A5; --real-bg:#1A2A21;
{pd}
  }}
}}
:root[data-theme="dark"]{{
  --paper:#141311; --surface:#1C1B18; --line:#302E29; --line-soft:#242220;
  --ink:#F0EDE5; --ink-2:#C4C0B6; --ink-3:#8E8A80;
  --said:#E98A7C; --said-bg:#31201D; --real:#8FC5A5; --real-bg:#1A2A21;
{pd}
}}
{base}{extra}
</style>

<div class="wrap">
{body}
</div>
""".format(title=esc(title), pv=palette_vars, pd=palette_dark,
           base=BASE_CSS, extra=EXTRA_CSS, body=body)


EXTRA_CSS = """
/* 거짓말이 생기는 자리 */
.origin{background:var(--ink);color:var(--paper);border-radius:.85rem;
        padding:1.4rem 1.3rem;display:flex;flex-direction:column;gap:.75rem}
.origin .ok{font-size:.72rem;letter-spacing:.1em;font-weight:700;opacity:.6}
.origin .oq{font-size:1.15rem;font-weight:800;line-height:1.5;text-wrap:balance}
.flow{display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;font-size:.8rem}
.flow span{background:rgba(255,255,255,.12);border-radius:.35rem;padding:.25rem .55rem}
.flow span.hot{background:var(--said);color:#fff;font-weight:700}
.flow i{opacity:.45;font-style:normal}
.origin .on{font-size:.85rem;opacity:.75;line-height:1.7}

/* 네 개의 질문 */
.triage{display:flex;flex-direction:column;gap:.55rem}
.tri{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--fc);
     border-radius:.55rem;padding:.85rem .95rem;display:flex;flex-direction:column;gap:.2rem}
.tri-top{display:flex;align-items:baseline;gap:.5rem;flex-wrap:wrap}
.tri-tag{font-size:.68rem;font-weight:800;color:var(--fc);background:var(--fc-bg);
         padding:.1rem .4rem;border-radius:.25rem}
.tri-name{font-size:1.02rem;font-weight:800}
.tri-ask{font-size:.98rem;font-weight:700;color:var(--fc)}
.tri-when{font-size:.82rem;color:var(--ink-3)}

/* 거짓말이 되는 선 */
.rulebox{border:1px solid var(--line);border-radius:.75rem;padding:1.15rem 1.2rem;
         background:var(--surface);display:flex;flex-direction:column;gap:.6rem}
.rulebox .big{font-size:1.05rem;font-weight:800;line-height:1.6;
              border-left:3px solid var(--said);padding-left:.8rem}
.rulebox .sub{font-size:.9rem;color:var(--ink-3);padding-left:.8rem}

/* 군 헤더 */
.fam-head{display:flex;flex-direction:column;gap:.3rem;
          border-top:3px solid var(--fc);padding-top:.85rem}
.fam-title{display:flex;align-items:baseline;gap:.5rem;flex-wrap:wrap}
.fam-tag{font-size:.72rem;font-weight:800;color:var(--fc);background:var(--fc-bg);
         padding:.15rem .5rem;border-radius:.3rem}
.fam-name{font-size:1.4rem;font-weight:800;letter-spacing:-.01em}
.fam-ask{font-size:1rem;font-weight:700;color:var(--fc)}
.fam-when{font-size:.85rem;color:var(--ink-3)}
.fam-note{font-size:.88rem;color:var(--ink-2);background:var(--fc-bg);
          border-radius:.5rem;padding:.7rem .85rem;line-height:1.7}

/* 유형 카드 */
.t-head{display:flex;align-items:baseline;gap:.5rem}
.t-no{font-size:1.15rem;font-weight:800;color:var(--fc)}
.t-name{font-size:1.1rem;font-weight:800;letter-spacing:-.01em}
.spec{display:grid;grid-template-columns:auto 1fr;gap:.35rem .75rem;margin:0;
      font-size:.92rem;line-height:1.7}
.spec dt{font-size:.72rem;font-weight:800;color:var(--ink-3);
         white-space:nowrap;padding-top:.28rem}
.spec dd{margin:0;color:var(--ink-2)}
.scene{border:1px solid var(--line);border-radius:.6rem;overflow:hidden}
.s-row{display:flex;gap:.7rem;padding:.7rem .85rem;align-items:flex-start}
.s-row + .s-row{border-top:1px solid var(--line)}
.s-tag{flex:0 0 auto;font-size:.66rem;font-weight:800;padding:.15rem .45rem;
       border-radius:.25rem;margin-top:.3rem;white-space:nowrap}
.s-a{background:var(--real-bg)} .s-a .s-tag{background:var(--real-bg);color:var(--real)}
.s-b{background:var(--said-bg)} .s-b .s-tag{background:var(--said);color:#fff}
.s-b .s-txt{font-weight:700}
.s-txt{font-size:.94rem;line-height:1.7}
.variant{font-size:.86rem;color:var(--ink-3);background:var(--line-soft);
         border-radius:.5rem;padding:.65rem .8rem;line-height:1.7}
.line{border-left:3px solid var(--said);padding-left:.8rem;font-size:.92rem;
      color:var(--ink-2);line-height:1.7}
.line b{color:var(--ink);display:block;font-size:.72rem;letter-spacing:.04em;margin-bottom:.15rem}
.believe{background:var(--said-bg);border-radius:.6rem;padding:.8rem .9rem;
         font-size:.93rem;line-height:1.75;color:var(--ink-2)}
.believe b{display:block;font-size:.72rem;font-weight:800;color:var(--said);
           letter-spacing:.04em;margin-bottom:.2rem}
.places{display:flex;flex-direction:column;gap:.4rem;font-size:.88rem;
        color:var(--ink-2);line-height:1.65}
.places b{font-size:.72rem;font-weight:800;color:var(--ink-3);letter-spacing:.04em}
.places li{list-style:none;padding-left:.85rem;position:relative}
.places li::before{content:"";position:absolute;left:0;top:.62em;
                   width:.3rem;height:.3rem;border-radius:50%;background:var(--ink-3)}
.places ul{margin:0;padding:0;display:flex;flex-direction:column;gap:.35rem}
.ask{background:var(--fc-bg);border-radius:.6rem;padding:.75rem .85rem;
     font-size:1rem;font-weight:700;color:var(--fc);line-height:1.6}
.ask-k{display:block;font-size:.68rem;letter-spacing:.08em;font-weight:800;
       opacity:.75;margin-bottom:.15rem}
.vs{background:var(--line-soft);border-radius:.5rem;padding:.6rem .75rem;
    color:var(--ink-3);font-size:.85rem;line-height:1.65}

/* 규칙 목록 */
ol.steps{margin:0;padding:0;list-style:none;counter-reset:s;
         display:flex;flex-direction:column;gap:.7rem}
ol.steps li{counter-increment:s;position:relative;padding-left:1.9rem;color:var(--ink-2)}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:.15rem;
  width:1.35rem;height:1.35rem;border-radius:50%;background:var(--ink);color:var(--paper);
  font-size:.74rem;font-weight:700;display:flex;align-items:center;justify-content:center}
ol.steps b{color:var(--ink)}
.pairlist{display:flex;flex-direction:column;gap:.7rem}
.pair{display:flex;flex-direction:column;gap:.15rem}
.pair b{font-size:.85rem;color:var(--ink)}
.pair span{font-size:.88rem;color:var(--ink-2);line-height:1.65}

/* 마지막 질문 */
.closing{background:var(--ink);color:var(--paper);border-radius:.85rem;
         padding:1.4rem 1.3rem;display:flex;flex-direction:column;gap:.6rem}
.closing .ck{font-size:.72rem;letter-spacing:.1em;font-weight:700;opacity:.6}
.closing .cq{font-size:1.2rem;font-weight:800;line-height:1.5;text-wrap:balance}
.closing .cb{font-size:.9rem;opacity:.78;line-height:1.7}

/* 세포 사전 */
.need{background:var(--surface);border:1px solid var(--line);border-radius:.75rem;
      overflow:hidden}
.need-head{background:var(--fc-bg);padding:.9rem 1.1rem;display:flex;
           align-items:baseline;gap:.6rem;flex-wrap:wrap;border-bottom:1px solid var(--line)}
.need-no{font-size:.75rem;font-weight:800;color:#fff;background:var(--fc);
         padding:.15rem .5rem;border-radius:.3rem}
.need-name{font-size:1.15rem;font-weight:800}
.need-beh{font-size:.85rem;color:var(--ink-3);width:100%}
.need-cell{padding:.75rem 1.1rem;border-bottom:1px solid var(--line);
           font-size:1rem;font-weight:800;color:var(--fc);line-height:1.5}
.need-cell small{display:block;font-size:.68rem;font-weight:700;color:var(--ink-3);
                 letter-spacing:.06em;margin-bottom:.2rem}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:0}
.col{padding:.95rem 1.1rem;display:flex;flex-direction:column;gap:.45rem}
.col + .col{border-left:1px solid var(--line)}
.col-k{font-size:.72rem;font-weight:800;color:var(--ink-3);letter-spacing:.04em}
.col p{font-size:.88rem;color:var(--ink-2);line-height:1.7}
.need-why{padding:.85rem 1.1rem;background:var(--fc-bg);font-size:.88rem;
          line-height:1.7;color:var(--ink-2)}
.need-why b{color:var(--fc);font-size:.72rem;font-weight:800;letter-spacing:.04em;
            display:block;margin-bottom:.2rem}
@media (max-width:520px){.cols{grid-template-columns:1fr}.col + .col{border-left:none;border-top:1px solid var(--line)}}
"""


# ── 3. 거짓말 도감 페이지 ────────────────────────────────────
def lie_page(d):
    fams = d['families']
    pv = '\n'.join('  --f%s:%s; --f%s-bg:%s;' % (f['id'], f['color'], f['id'], f['bg']) for f in fams)
    pd = '\n'.join('    --f%s:%s; --f%s-bg:%s;' % (f['id'], lighten(f['color']), f['id'], darken(f['bg']))
                   for f in fams)

    o = d['origin']
    flow = '<i>→</i>'.join(
        '<span%s>%s</span>' % (' class="hot"' if x == '옮긴다' else '', esc(x)) for x in o['flow'])

    triage = '\n'.join(
        '''      <div class="tri" style="--fc:var(--f{i});--fc-bg:var(--f{i}-bg)">
        <div class="tri-top"><span class="tri-tag">{i}군</span><span class="tri-name">{n}</span></div>
        <div class="tri-ask">{a}</div>
        <div class="tri-when">이럴 때 걸린다 — {w}</div>
      </div>'''.format(i=f['id'], n=esc(f['name']), a=esc(f['ask']), w=esc(f['trigger']))
        for f in fams)

    th = d['threshold']
    sections = []
    for f in fams:
        cards = []
        for t in f['types']:
            rows = ['<div class="s-row s-a"><span class="s-tag">작가</span><span class="s-txt">%s</span></div>'
                    % esc(t['bookAuthor']),
                    '<div class="s-row s-b"><span class="s-tag">정리</span><span class="s-txt">%s</span></div>'
                    % esc(t['bookSummary'])]
            if t.get('bookAuthor2'):
                rows.append('<div class="s-row s-a"><span class="s-tag">작가</span><span class="s-txt">%s</span></div>'
                            % esc(t['bookAuthor2']))
                rows.append('<div class="s-row s-b"><span class="s-tag">%s</span><span class="s-txt">%s</span></div>'
                            % (esc(t.get('summaryLabel2', '정리')), esc(t['bookSummary2'])))
            variant = ('<div class="variant">%s</div>' % esc(t['variant'])) if t.get('variant') else ''
            places = ''.join('<li>%s</li>' % esc(p) for p in t['places'])
            vs = ('<p class="vs">%s</p>' % esc(t['vs'])) if t.get('vs') else ''
            cards.append("""    <article class="card">
      <div class="t-head"><span class="t-no">{no}</span><span class="t-name">{name}</span></div>
      <dl class="spec"><dt>정의</dt><dd>{deff}</dd><dt>알아보는 법</dt><dd>{spot}</dd></dl>
      <div class="scene">{rows}</div>
      {variant}
      <div class="line"><b>거짓말이 되는 선</b>{line}</div>
      <div class="believe"><b>믿으면 벌어지는 일</b>{believe}</div>
      <div class="places"><b>글 읽을 때 만나는 자리</b><ul>{places}</ul></div>
      <p class="ask"><span class="ask-k">되받아치는 질문</span>{ask}</p>
      {vs}
    </article>""".format(no=t['no'], name=esc(t['name']), deff=esc(t['def']), spot=esc(t['spot']),
                         rows=''.join(rows), variant=variant, line=esc(t['line']),
                         believe=esc(t['believe']), places=places, ask=esc(t['ask']), vs=vs))

        note = ('<p class="fam-note">%s</p>' % esc(f['note'])) if f.get('note') else ''
        sections.append("""  <section style="--fc:var(--f{i});--fc-bg:var(--f{i}-bg)">
    <div class="fam-head">
      <div class="fam-title"><span class="fam-tag">{i}군</span><span class="fam-name">{n}</span></div>
      <div class="fam-ask">{a}</div>
      <div class="fam-when">이럴 때 걸린다 — {w}</div>
    </div>
    {note}
{cards}
  </section>""".format(i=f['id'], n=esc(f['name']), a=esc(f['ask']), w=esc(f['trigger']),
                       note=note, cards='\n'.join(cards)))

    qt = d['quickTable']
    qrows = ''.join('<tr>%s</tr>' % ''.join(
        '<td>%s%s%s</td>' % ('<b>' if c == 1 and cell else '', esc(cell), '</b>' if c == 1 and cell else '')
        for c, cell in enumerate(r)) for r in qt['rows'])

    ru = d['rules']
    pass_items = ''.join('<div class="pair"><b>%s</b><span>%s</span></div>' % (esc(a), esc(b))
                         for a, b in ru['pass'])
    make_items = ''.join('<li>%s</li>' % esc(x) for x in ru['make'])
    hint_items = ''.join('<div class="pair"><b>%s</b><span>%s</span></div>' % (esc(a), esc(b))
                         for a, b in ru['hints'])
    card_items = ''.join('<div class="pair"><b>%s</b><span>%s</span></div>' % (esc(a), esc(b))
                         for a, b in ru['card'])
    cl = d['closing']

    body = """  <header class="masthead">
    <div class="eyebrow">책 분석 + 거짓말 사냥</div>
    <h1>{title}</h1>
    <p class="standfirst">{subtitle}</p>
  </header>

  <section>
    <div class="origin">
      <span class="ok">{ok}</span>
      <span class="oq">{olead}</span>
      <div class="flow">{flow}</div>
      <span class="on">↑ {fnote}</span>
      <span class="on">{obody}</span>
    </div>
  </section>

  <section>
    <h2>유형을 고르기 전에 — 네 개의 질문</h2>
    <p class="lede">{dq} {dn}</p>
    <div class="triage">
{triage}
    </div>
  </section>

  <section>
    <h2>{thtitle}</h2>
    <p class="lede">{thlead}</p>
    <div class="rulebox">
      <div class="big">{thrule}</div>
      <div class="sub">{thsub}</div>
    </div>
  </section>

{sections}

  <section>
    <h2>{qtitle}</h2>
    <div class="tablewrap"><table>
      <thead><tr>{qhead}</tr></thead><tbody>{qrows}</tbody>
    </table></div>
  </section>

  <section>
    <h2>문제를 만드는 규칙</h2>
    <div class="card">
      <div class="col-k">{ptitle} — {pnote}</div>
      <div class="pairlist">{pass_items}</div>
    </div>
    <div class="card">
      <div class="col-k">{mtitle}</div>
      <ol class="steps">{make_items}</ol>
    </div>
    <div class="card">
      <div class="col-k">{htitle}</div>
      <div class="pairlist">{hint_items}</div>
    </div>
    <div class="card">
      <div class="col-k">{ctitle}</div>
      <div class="pairlist">{card_items}</div>
    </div>
  </section>

  <section>
    <div class="closing">
      <span class="ck">{cltitle}</span>
      <span class="cb">{cllead}</span>
      <span class="cq">“{clq}”</span>
      <span class="cb">{clbody}</span>
    </div>
  </section>

  <footer>
    책 분석 + 거짓말 사냥 · 비판적 독해 훈련 자료<br>
    앱 화면 왼쪽 도감, 인쇄용 워드와 같은 내용입니다.
  </footer>""".format(
        title=esc(d['title']), subtitle=esc(d['subtitle']),
        ok=esc(o['title']), olead=esc(o['lead']), flow=flow,
        fnote=esc(o['flowNote']), obody=esc(o['body']),
        dq=esc(d['decision']['question']), dn=esc(d['decision']['note']),
        triage=triage, thtitle=esc(th['title']), thlead=esc(th['lead']),
        thrule=esc(th['rule']), thsub=esc(th['sub']),
        sections='\n\n'.join(sections),
        qtitle=esc(qt['title']),
        qhead=''.join('<th>%s</th>' % esc(h) for h in qt['head']), qrows=qrows,
        ptitle=esc(ru['passTitle']), pnote=esc(ru['passNote']), pass_items=pass_items,
        mtitle=esc(ru['makeTitle']), make_items=make_items,
        htitle=esc(ru['hintTitle']), hint_items=hint_items,
        ctitle=esc(ru['cardTitle']), card_items=card_items,
        cltitle=esc(cl['title']), cllead=esc(cl['lead']),
        clq=esc(cl['question']), clbody=esc(cl['body']))

    return page(d['title'], pv, pd, body)


# ── 4. 세포 비유 사전 페이지 ────────────────────────────────
CELL_HUES = ['#2C4A8A', '#1F6B5B', '#6B3A8F', '#8A5A12', '#A03A2E']
CELL_BGS = ['#EAF0FB', '#E4F4EF', '#F2ECFA', '#FAF0DC', '#FBECEA']


def cell_page(d):
    pv = '\n'.join('  --c%d:%s; --c%d-bg:%s;' % (i, CELL_HUES[i], i, CELL_BGS[i]) for i in range(5))
    pd = '\n'.join('    --c%d:%s; --c%d-bg:%s;' % (i, lighten(CELL_HUES[i]), i, darken(CELL_BGS[i]))
                   for i in range(5))

    rows = ''.join(
        '<tr><td><b>{n}</b></td><td><b>{name}</b></td><td>{beh}</td><td>{cell}</td></tr>'.format(
            n=x['no'], name=esc(x['name']), beh=esc(x['behavior']), cell=esc(x['cell']))
        for x in d['needs'])

    cards = []
    for x in d['needs']:
        k = (x['no'] - 1) // 3
        easy = ''.join('<p>%s</p>' % esc(t) for t in x['easy'])
        story = ''.join('<p>%s</p>' % esc(t) for t in x['story'])
        cards.append("""  <div class="need" style="--fc:var(--c{k});--fc-bg:var(--c{k}-bg)">
    <div class="need-head">
      <span class="need-no">#{no}</span><span class="need-name">{name}</span>
      <span class="need-beh">핵심 행동 유형 | {beh}</span>
    </div>
    <div class="need-cell"><small>세포·면역계 비유</small>{cell}</div>
    <div class="cols">
      <div class="col"><span class="col-k">쉬운 비유</span>{easy}</div>
      <div class="col"><span class="col-k">세포 이야기</span>{story}</div>
    </div>
    <div class="need-why"><b>이 욕구와 같은 이유</b>{why}</div>
  </div>""".format(k=k, no=x['no'], name=esc(x['name']), beh=esc(x['behavior']),
                   cell=esc(x['cell']), easy=easy, story=story, why=esc(x['why'])))

    body = """  <header class="masthead">
    <div class="eyebrow">책 분석 + 거짓말 사냥</div>
    <h1>{title}</h1>
    <p class="standfirst">{subtitle}. {note}</p>
  </header>

  <section>
    <h2>15가지 욕구 — 한눈에 보기</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>#</th><th>욕구</th><th>핵심 행동 유형</th><th>세포·면역계 비유</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p class="lede">챕터를 분석할 때는 이 표에서 <b>그 챕터가 켜는 욕구</b>를 먼저 고르고,
    그 줄의 세포 비유를 이야기의 뼈대로 삼습니다. 세포를 새로 지어내지 않습니다.</p>
  </section>

  <section>
{cards}
  </section>

  <footer>
    욕구별 세포·면역계 비유 사전 · 15가지 욕구 완전 해설<br>
    앱은 이 사전에서 세포를 고른 뒤, 모든 설명이 그 세포로 돌아오도록 씁니다.
  </footer>""".format(title=esc(d['title']), subtitle=esc(d['subtitle']),
                      note=esc(d['note']), rows=rows, cards='\n\n'.join(cards))

    return page(d['title'], pv, pd, body)


def write(name, content):
    os.makedirs(WEB, exist_ok=True)
    p = os.path.join(WEB, name)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    return p


def main():
    lies, cells = load('lie_types.json'), load('cell_metaphors.json')
    n = patch_app(lies, cells)
    a = write('거짓말-도감.html', lie_page(lies))
    b = write('세포-비유-사전.html', cell_page(cells))
    total = sum(len(f['types']) for f in lies['families'])
    print('거짓말 %d종 / %d군, 욕구 %d개' % (total, len(lies['families']), len(cells['needs'])))
    print('앱 데이터 블록 %d자' % n)
    for p in (a, b):
        print('  ', os.path.relpath(p, HERE), os.path.getsize(p), 'bytes')


if __name__ == '__main__':
    main()
