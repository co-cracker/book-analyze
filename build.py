# -*- coding: utf-8 -*-
"""lie_types.json 하나에서 앱·웹페이지·워드를 모두 생성한다.

    python build.py

거짓말 유형을 고칠 때는 lie_types.json만 고치고 이걸 다시 돌리면 된다.
세 곳의 정의가 어긋날 수 없다.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'lie_types.json')
APP = os.path.join(HERE, 'book_analysis_app.html')

START = '/* __LIE_DATA_START__ */'
END = '/* __LIE_DATA_END__ */'


def load():
    with open(DATA, encoding='utf-8') as f:
        return json.load(f)


# ────────────────────────────────────────────────────────────
# 1. 앱에 넣을 JS 데이터 블록
# ────────────────────────────────────────────────────────────
def js_block(d):
    payload = json.dumps(d, ensure_ascii=False, indent=2)
    return (
        START + '\n'
        '// 이 블록은 build.py가 lie_types.json에서 생성한다. 직접 고치지 마라.\n'
        'const LIE_DATA = ' + payload + ';\n'
        'const LIE_FAMILIES = LIE_DATA.families;\n'
        + END
    )


def patch_app(d):
    with open(APP, encoding='utf-8') as f:
        html = f.read()

    block = js_block(d)

    if START in html:
        html = re.sub(
            re.escape(START) + r'.*?' + re.escape(END),
            lambda m: block,
            html, flags=re.S)
    else:
        # 최초 1회: 기존 const LIE_FAMILIES = [ ... ]; 를 통째로 교체
        m = re.search(r'const LIE_FAMILIES = \[.*?\n\];\n', html, re.S)
        if not m:
            sys.exit('앱에서 LIE_FAMILIES 블록을 찾지 못했습니다.')
        html = html[:m.start()] + block + '\n' + html[m.end():]

    with open(APP, 'w', encoding='utf-8') as f:
        f.write(html)
    return len(block)


# ────────────────────────────────────────────────────────────
# 2. 멘토 배포용 웹 페이지
# ────────────────────────────────────────────────────────────
def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def web_page(d):
    fams = d['families']
    total = sum(len(f['types']) for f in fams)

    fam_vars = '\n'.join(
        '  --fam%s:%s; --fam%s-bg:%s;' % (f['id'], f['color'], f['id'], f['bg'])
        for f in fams)
    fam_vars_dark = '\n'.join(
        '    --fam%s:%s; --fam%s-bg:%s;' % (f['id'], dark_hue(f['color']), f['id'], dark_bg(f['bg']))
        for f in fams)

    # 판별 카드
    triggers = '\n'.join(
        '''      <div class="tri" style="--fc:var(--fam{id});--fc-bg:var(--fam{id}-bg)">
        <span class="tri-tag">{id}군</span>
        <span class="tri-name">{name}</span>
        <span class="tri-intent">{intent}</span>
        <span class="tri-when">{trigger}</span>
      </div>'''.format(id=f['id'], name=esc(f['name']),
                       intent=esc(f['intent']), trigger=esc(f['trigger']))
        for f in fams)

    sections = []
    for f in fams:
        cards = []
        for t in f['types']:
            where = ''.join('<span class="chip">%s</span>' % esc(w) for w in t['where'])
            cards.append('''    <article class="type">
      <div class="t-head"><span class="t-no">{no}</span><span class="t-name">{name}</span></div>
      <div class="chips">{where}</div>
      <div class="scene">
        <div class="s-row s-said"><span class="s-tag">이렇게 말한다</span><span class="s-txt">{said}</span></div>
        <div class="s-row s-real"><span class="s-tag">실제로는</span><span class="s-txt">{actual}</span></div>
      </div>
      <p class="ask"><span class="ask-k">되받아치는 질문</span>{ask}</p>
      <div class="detail">
        <p><b>왜 속나</b> {why}</p>
        <p><b>글에서는 이렇게 보인다</b> {intext}</p>
        <p class="vs">{vs}</p>
      </div>
    </article>'''.format(no=t['no'], name=esc(t['name']), where=where,
                         said=esc(t['said']), actual=esc(t['actual']),
                         ask=esc(t['ask']), why=esc(t['why']),
                         intext=esc(t['intext']), vs=esc(t['vs'])))

        sections.append('''  <section style="--fc:var(--fam{id});--fc-bg:var(--fam{id}-bg)">
    <div class="fam-head">
      <div class="fam-title"><span class="fam-tag">{id}군</span><span class="fam-name">{name}</span></div>
      <p class="fam-intent">{intent}</p>
      <p class="fam-when"><b>이럴 때 의심한다</b> {trigger}</p>
    </div>
{cards}
  </section>'''.format(id=f['id'], name=esc(f['name']), intent=esc(f['intent']),
                       trigger=esc(f['trigger']), cards='\n'.join(cards)))

    return TEMPLATE.format(
        title=esc(d['title']), subtitle=esc(d['subtitle']),
        question=esc(d['decision']['question']), note=esc(d['decision']['note']),
        total=total, fam_vars=fam_vars, fam_vars_dark=fam_vars_dark,
        triggers=triggers, sections='\n\n'.join(sections))


def dark_hue(hexcolor):
    """다크 배경에서 읽히도록 밝기를 올린다."""
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (min(255, int(c + (255 - c) * 0.55)) for c in (r, g, b))
    return '#%02X%02X%02X' % (r, g, b)


def dark_bg(hexcolor):
    """밝은 배경색을 어두운 대응색으로 낮춘다."""
    r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (int(c * 0.19) for c in (r, g, b))
    return '#%02X%02X%02X' % (r, g, b)


TEMPLATE = '''<title>{title}</title>
<style>
:root{{
  --paper:#FBFAF7; --surface:#FFFFFF; --line:#E6E2D8; --line-soft:#F1EDE4;
  --ink:#1B1A17; --ink-2:#4A4740; --ink-3:#7A766C;
  --said:#B5372B; --said-bg:#FBEDEA; --real:#2F6B4F; --real-bg:#EAF3EC;
{fam_vars}
  --sans:'Pretendard','Pretendard Variable',-apple-system,'Apple SD Gothic Neo',
         'Malgun Gothic','맑은 고딕','Noto Sans KR',system-ui,sans-serif;
}}
@media (prefers-color-scheme: dark){{
  :root:not([data-theme="light"]){{
    --paper:#141311; --surface:#1C1B18; --line:#302E29; --line-soft:#242220;
    --ink:#F0EDE5; --ink-2:#C4C0B6; --ink-3:#8E8A80;
    --said:#E98A7C; --said-bg:#31201D; --real:#8FC5A5; --real-bg:#1A2A21;
{fam_vars_dark}
  }}
}}
:root[data-theme="dark"]{{
  --paper:#141311; --surface:#1C1B18; --line:#302E29; --line-soft:#242220;
  --ink:#F0EDE5; --ink-2:#C4C0B6; --ink-3:#8E8A80;
  --said:#E98A7C; --said-bg:#31201D; --real:#8FC5A5; --real-bg:#1A2A21;
{fam_vars_dark}
}}

*{{box-sizing:border-box}}
body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
     font-size:17px;line-height:1.75;word-break:keep-all;-webkit-text-size-adjust:100%}}
.wrap{{max-width:34rem;margin:0 auto;padding:2.5rem 1.25rem 5rem;
       display:flex;flex-direction:column;gap:2.75rem}}

.masthead{{display:flex;flex-direction:column;gap:.5rem}}
.eyebrow{{font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;
         color:var(--ink-3);font-weight:700}}
h1{{margin:0;font-size:2.1rem;line-height:1.2;letter-spacing:-.02em;font-weight:800;text-wrap:balance}}
.standfirst{{margin:0;color:var(--ink-2);font-size:1rem}}

section{{display:flex;flex-direction:column;gap:1rem}}
h2{{margin:0;font-size:1.3rem;line-height:1.35;font-weight:800;text-wrap:balance}}
p{{margin:0}}
.lede{{color:var(--ink-2)}}

.qbox{{background:var(--ink);color:var(--paper);border-radius:.85rem;
      padding:1.35rem 1.3rem;display:flex;flex-direction:column;gap:.45rem}}
.qbox .qk{{font-size:.72rem;letter-spacing:.1em;font-weight:700;opacity:.65}}
.qbox .qq{{font-size:1.25rem;font-weight:800;line-height:1.45;text-wrap:balance}}
.qbox .qn{{font-size:.85rem;opacity:.72;line-height:1.6}}

.triage{{display:flex;flex-direction:column;gap:.55rem}}
.tri{{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--fc);
     border-radius:.55rem;padding:.8rem .9rem;display:grid;
     grid-template-columns:auto 1fr;gap:.15rem .55rem;align-items:baseline}}
.tri-tag{{font-size:.68rem;font-weight:800;letter-spacing:.05em;color:var(--fc);
         background:var(--fc-bg);padding:.1rem .4rem;border-radius:.25rem}}
.tri-name{{font-size:1.05rem;font-weight:800}}
.tri-intent{{grid-column:2;font-size:.92rem;color:var(--ink-2)}}
.tri-when{{grid-column:2;font-size:.82rem;color:var(--ink-3);margin-top:.15rem}}
.tri-when::before{{content:"이럴 때 — ";font-weight:700}}

.fam-head{{display:flex;flex-direction:column;gap:.35rem;
          border-top:3px solid var(--fc);padding-top:.85rem}}
.fam-title{{display:flex;align-items:baseline;gap:.5rem;flex-wrap:wrap}}
.fam-tag{{font-size:.72rem;font-weight:800;letter-spacing:.06em;color:var(--fc);
         background:var(--fc-bg);padding:.15rem .5rem;border-radius:.3rem}}
.fam-name{{font-size:1.4rem;font-weight:800;letter-spacing:-.01em}}
.fam-intent{{color:var(--ink-2);font-size:.98rem}}
.fam-when{{font-size:.88rem;color:var(--ink-3)}}
.fam-when b{{color:var(--ink-2)}}

.type{{background:var(--surface);border:1px solid var(--line);border-radius:.75rem;
      padding:1.15rem 1.2rem;display:flex;flex-direction:column;gap:.8rem}}
.t-head{{display:flex;align-items:baseline;gap:.5rem}}
.t-no{{font-size:1.15rem;font-weight:800;color:var(--fc)}}
.t-name{{font-size:1.1rem;font-weight:800;letter-spacing:-.01em}}
.chips{{display:flex;flex-wrap:wrap;gap:.3rem}}
.chip{{font-size:.74rem;color:var(--ink-3);background:var(--line-soft);
      border-radius:1rem;padding:.15rem .55rem}}

.scene{{border:1px solid var(--line);border-radius:.6rem;overflow:hidden}}
.s-row{{display:flex;gap:.7rem;padding:.75rem .85rem;align-items:flex-start}}
.s-row + .s-row{{border-top:1px solid var(--line)}}
.s-tag{{flex:0 0 auto;font-size:.66rem;font-weight:800;letter-spacing:.04em;
       padding:.15rem .45rem;border-radius:.25rem;margin-top:.3rem;white-space:nowrap}}
.s-said{{background:var(--said-bg)}}
.s-said .s-tag{{background:var(--said);color:var(--paper)}}
.s-said .s-txt{{font-weight:700}}
.s-real .s-tag{{background:var(--real-bg);color:var(--real)}}
.s-txt{{font-size:.95rem;line-height:1.7}}

.ask{{background:var(--fc-bg);border-radius:.6rem;padding:.75rem .85rem;
     font-size:1rem;font-weight:700;color:var(--fc);line-height:1.6}}
.ask-k{{display:block;font-size:.68rem;letter-spacing:.08em;font-weight:800;
       opacity:.75;margin-bottom:.15rem}}

.detail{{display:flex;flex-direction:column;gap:.5rem;font-size:.9rem;
        color:var(--ink-2);line-height:1.7}}
.detail b{{color:var(--ink);display:block;font-size:.75rem;letter-spacing:.04em}}
.detail .vs{{background:var(--line-soft);border-radius:.5rem;padding:.6rem .75rem;
            color:var(--ink-3);font-size:.86rem}}

footer{{border-top:1px solid var(--line);padding-top:1.25rem;
       color:var(--ink-3);font-size:.85rem;line-height:1.7}}
@media (max-width:400px){{h1{{font-size:1.8rem}}}}
</style>

<div class="wrap">
  <header class="masthead">
    <div class="eyebrow">책 분석 + 거짓말 사냥</div>
    <h1>{title}</h1>
    <p class="standfirst">{subtitle}. 광고에서, 단톡방에서, 어른들 말에서 실제로 마주치는 것들입니다.</p>
  </header>

  <section>
    <div class="qbox">
      <span class="qk">유형을 고르기 전에</span>
      <span class="qq">{question}</span>
      <span class="qn">{note}</span>
    </div>
    <div class="triage">
{triggers}
    </div>
  </section>

{sections}

  <footer>
    책 분석 + 거짓말 사냥 · 비판적 독해 훈련 자료<br>
    {total}종. 인쇄용 워드 파일, 앱 화면 왼쪽 도감과 같은 내용입니다.
  </footer>
</div>
'''


def write_web(d):
    out = os.path.join(HERE, 'web', '거짓말-도감.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(web_page(d))
    return out


def main():
    d = load()
    n = patch_app(d)
    web = write_web(d)
    total = sum(len(f['types']) for f in d['families'])
    print('유형 %d종 / %d군' % (total, len(d['families'])))
    print('앱 데이터 블록: %d자' % n)
    print('웹 페이지:', os.path.relpath(web, HERE))


if __name__ == '__main__':
    main()
