# -*- coding: utf-8 -*-
"""lie_types.json에서 인쇄용 워드 파일을 만든다.

    python make_docx.py

유형을 고칠 때는 lie_types.json만 고치고 build.py와 이걸 차례로 돌리면
앱·웹·워드가 모두 같은 내용이 된다.
"""
import json
import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = '맑은 고딕'


def rgb(hexcolor):
    return tuple(int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))


def set_kfont(run, size=10.5, bold=False, color=None):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)


def shade(cell, hexfill):
    el = OxmlElement('w:shd')
    el.set(qn('w:val'), 'clear')
    el.set(qn('w:fill'), hexfill)
    cell._tc.get_or_add_tcPr().append(el)


def para(doc, text='', size=10.5, bold=False, color=None,
         space_after=6, indent=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.4
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if text:
        set_kfont(p.add_run(text), size, bold, color)
    return p


def labelled(doc, label, text, indent=0.4, space_after=6):
    """작은 라벨 + 본문을 한 단락에 넣는다."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.4
    p.paragraph_format.left_indent = Cm(indent)
    set_kfont(p.add_run(label + '  '), 9, True, (0x7A, 0x76, 0x6C))
    set_kfont(p.add_run(text), 10)
    return p


GREY = (0x6B, 0x6A, 0x65)
INK = (0x1B, 0x1A, 0x17)


def build(data, path):
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = sec.bottom_margin = Cm(2.0)

    st = doc.styles['Normal']
    st.font.name = FONT
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

    fams = data['families']
    total = sum(len(f['types']) for f in fams)

    # ── 표지 ──
    para(doc, data['title'], 22, True, space_after=2)
    para(doc, data['subtitle'] + ' · 비판적 독해 훈련 자료', 11, False, GREY, 16)

    para(doc, '유형을 고르기 전에', 14, True, space_after=4)
    para(doc, '“' + data['decision']['question'] + '”', 15, True, INK, 4)
    para(doc, data['decision']['note'], 10.5, False, GREY, 14)

    # ── 4군 판별표 ──
    para(doc, '무엇을 건드린 말인가', 13, True, space_after=6)
    tb = doc.add_table(rows=1, cols=3)
    tb.style = 'Table Grid'
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, h in enumerate(['군', '건드리는 것', '이럴 때 의심한다']):
        cell = tb.rows[0].cells[c]
        cell.text = ''
        set_kfont(cell.paragraphs[0].add_run(h), 9.5, True, (0xFF, 0xFF, 0xFF))
        shade(cell, '2E2E2B')
    for f in fams:
        row = tb.add_row().cells
        for c, v in enumerate(['%s군 · %s' % (f['id'], f['name']), f['intent'], f['trigger']]):
            row[c].text = ''
            set_kfont(row[c].paragraphs[0].add_run(v), 9, c == 0,
                      rgb(f['color']) if c == 0 else None)
        shade(row[0], f['bg'].lstrip('#'))
    for w, col in zip([Cm(3.2), Cm(6.2), Cm(7.6)], tb.columns):
        for cell in col.cells:
            cell.width = w

    para(doc, '', space_after=4)
    para(doc, '각 군에 유형이 3개씩 있습니다. 위 표에서 군을 먼저 정하면 %d개 중에서 고르던 문제가 '
              '3개 중에서 고르는 문제로 줄어듭니다.' % total, 10, False, GREY, 6)

    # ── 군별 상세 ──
    for f in fams:
        doc.add_page_break()
        color = rgb(f['color'])
        para(doc, '%s군 · %s' % (f['id'], f['name']), 17, True, color, 2)
        para(doc, f['intent'], 11, True, GREY, 2)
        para(doc, '이럴 때 의심한다 — ' + f['trigger'], 10, False, GREY, 12)

        for t in f['types']:
            para(doc, '%s %s' % (t['no'], t['name']), 13.5, True, color, 3)
            labelled(doc, '정의', t['def'])
            labelled(doc, '알아보는 법', t['spot'])
            labelled(doc, '왜 거짓인가', t['whyLie'], space_after=8)

            # 책 예시 — 작가가 쓴 문장 / 정리에 실린 문장
            def pair_table(rows, w0=Cm(2.7), w1=Cm(14.3)):
                tb2 = doc.add_table(rows=len(rows), cols=2)
                tb2.style = 'Table Grid'
                for r, (tag, txt, tagcolor, fill, bold) in enumerate(rows):
                    c0, c1 = tb2.rows[r].cells
                    c0.text = ''
                    set_kfont(c0.paragraphs[0].add_run(tag), 8.5, True, tagcolor)
                    shade(c0, fill)
                    c0.width = w0
                    c1.text = ''
                    set_kfont(c1.paragraphs[0].add_run(txt), 10, bold)
                    c1.width = w1

            pair_table([
                ('작가', t['bookAuthor'], (0x2F, 0x6B, 0x4F), 'EAF3EC', False),
                ('정리', t['bookSummary'], (0xB5, 0x37, 0x2B), 'FBEDEA', True),
            ])
            para(doc, '', space_after=6)

            para(doc, '현실에서 같은 수법 — ' + ' · '.join(t['where']), 9, True, GREY, 4,
                 indent=0.4)
            pair_table([
                ('이렇게 말한다', t['realSaid'], (0xB5, 0x37, 0x2B), 'FBEDEA', True),
                ('실제로는', t['realActual'], (0x2F, 0x6B, 0x4F), 'EAF3EC', False),
            ])
            para(doc, '', space_after=6)

            # 되받아치는 질문 — 가장 중요한 한 줄
            q = doc.add_paragraph()
            q.paragraph_format.space_after = Pt(8)
            q.paragraph_format.left_indent = Cm(0.4)
            q.paragraph_format.line_spacing = 1.4
            set_kfont(q.add_run('되받아치는 질문   '), 8.5, True, GREY)
            set_kfont(q.add_run('“' + t['ask'] + '”'), 11.5, True, color)

            labelled(doc, '헷갈리지 않기', t['vs'], space_after=16)

    # ── 출제 규칙 ──
    doc.add_page_break()
    para(doc, '거짓말을 만들 때의 규칙', 17, True, space_after=4)
    para(doc, 'AI가 요약문에 거짓말을 심을 때 지키는 규칙입니다. 사람이 직접 문제를 낼 때도 같습니다.',
         10, False, GREY, 10)
    rules = [
        '거짓말은 정확히 3개, 서로 다른 군에서 하나씩. 같은 군 중복 금지.',
        '한 문장에서 손대는 건 딱 한 군데. 문장 전체를 반대로 만들지 않는다.',
        '바꾸지 않은 부분은 본문에 나온 표현 그대로. 새 단어·새 개념 등장 금지.',
        '극단 단어(모든/항상/절대/전혀) 금지. ② 수량 부풀리기도 “대체로/자주/흔히”까지만.',
        '거짓 문장은 참 문장과 길이·문체·어미가 구별되지 않아야 한다.',
        '참 문장 최소 2개에 “~일 수 있다”, “~할 때”, “~보다”를 미끼로 남긴다. '
        '이게 없으면 학생이 “조심스러운 표현이 없는 문장이 거짓말”이라는 요령만으로 다 찍는다.',
        '거짓말의 원래 내용은 본문 안에 실제로 있어야 한다. 없는 내용을 지어내 비틀지 않는다.',
        '힌트는 정답을 알려주지 않는다. 1단계는 무엇을 대조할지, 2단계는 위치 범위, 3단계는 스스로 던질 질문.',
        '정답 카드에는 같은 수법을 현실에서 마주치는 장면을 한 줄 함께 적는다. '
        '책 안에서만 끝나면 훈련이 되지 않는다.',
    ]
    for i, r in enumerate(rules, 1):
        para(doc, '%d. %s' % (i, r), 10.5, space_after=5, indent=0.4)

    doc.save(path)
    return path


def main():
    with open(os.path.join(HERE, 'lie_types.json'), encoding='utf-8') as f:
        data = json.load(f)
    out = os.path.join(HERE, data['title'] + '.docx')
    build(data, out)
    print('저장:', os.path.basename(out), os.path.getsize(out), 'bytes')


if __name__ == '__main__':
    main()
