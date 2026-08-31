# -*- coding: utf-8 -*-
r"""문서용 ChatGPT 이미지 생성 바로가기를 만든다.

    python make_shortcuts.py

바탕화면 \ 클로드 문서 이미지 \ <문서이름> 이미지 \
    ★ 전체 이미지 한번에 만들기 (여기부터).url
    프롬프트 원문 (읽기용).txt
    다시 만들기 (한 장씩) \ 01 ....url ...

장면은 4군 각각을 글자 없이 그림만으로 보여주는 일상 상황이다.
"""
import json
import os
import shutil
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))

STYLE = (
    "Style for every image: hand-drawn black ink line art, slightly wobbly linework, "
    "hair and clothing filled solid black, faces and background left plain, "
    "dot eyes and a short curved mouth with no nose, coral-pink cheek blush as the only colour, "
    "warm off-white cream ground, a few tiny four-point sparkle doodles, "
    "no shading, no gradients, 16:9 aspect ratio. "
    "Absolutely no text, letters, numbers or symbols anywhere in the image."
)

SCENES = [
    {
        'slug': '01_made-bigger',
        'ko': '01 부풀리기 (1군)',
        'en': (
            "Two children standing side by side facing the viewer. "
            "The child on the left holds a very small box with both hands, calm and matter-of-fact. "
            "The child on the right, turned toward a third child off to the side, "
            "holds a box that is enormously larger, arms stretched wide around it, "
            "leaning forward eagerly as if passing the story along. "
            "The two boxes are the same shape; only the size differs, so the contrast reads at a glance."
        )
    },
    {
        'slug': '02_only-the-good-shown',
        'ko': '02 골라 보여주기 (2군)',
        'en': (
            "A child standing proudly beside a wall, gesturing up at three certificates pinned neatly on it. "
            "On the floor behind the child, out of the way and partly under a low table, "
            "sits a large untidy heap of the same sheets of paper lying face down, far more of them than on the wall. "
            "The child's body blocks part of the heap from the viewer's line to the wall. "
            "All sheets are completely blank."
        )
    },
    {
        'slug': '03_arrow-flipped',
        'ko': '03 엮기 (3군)',
        'en': (
            "A child kneeling on the floor between two separate rows of large domino tiles. "
            "In the left row, the first tile has already tipped and leans into the second. "
            "With their other hand the child is setting the tile of the right row back upright "
            "so that its lean would point the opposite way. "
            "The tiles are identical in size and shape; only the direction of the lean differs between the rows."
        )
    },
    {
        'slug': '04_extra-added',
        'ko': '04 빌리고 얹기 (4군)',
        'en': (
            "Three children standing in a row, each turned toward the next, passing a stack of plates hand to hand. "
            "The first child holds three plates, the second child holds the same three, "
            "but the third child at the end of the row holds four, having quietly set one more plate on top. "
            "The extra plate sits slightly crooked on the stack so it reads as added rather than original."
        )
    },
    {
        'slug': '05_asking-back',
        'ko': '05 되받아치는 질문',
        'en': (
            "A child sitting at a low table with one hand raised in a clear questioning gesture, "
            "palm open and head tilted slightly up, looking directly ahead with a curious, unafraid expression. "
            "On the table in front of them lie two blank sheets of paper side by side, "
            "with the child's other index finger resting on one of them. "
            "The sheets stay completely blank with only faint horizontal ruling lines suggested."
        )
    },
]


def url_file(path, url):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('[InternetShortcut]\n')
        f.write('URL=%s\n' % url)
        f.write('IconIndex=0\n')


def chatgpt_url(prompt):
    return 'https://chatgpt.com/?q=' + quote(prompt, safe='')


def master_prompt():
    lines = [
        "I need %d separate illustrations for a Korean reading-education handout about the ways "
        "a claim gets twisted in everyday life. Draw them ONE AT A TIME." % len(SCENES),
        "", STYLE, "",
        "Rules: draw only ONE scene per image. Never combine two scenes into a single picture. "
        "After each image, stop and wait for me to type the next message before drawing the following one.",
        "", "Here are the scenes in order:", "",
    ]
    for i, s in enumerate(SCENES, 1):
        lines.append("%d. (save as %s.png) %s" % (i, s['slug'], s['en']))
        lines.append("")
    lines.append(
        "When all %d images are finished, rename them exactly as the filenames above "
        "and bundle all of them into a single .zip file for me to download." % len(SCENES))
    return '\n'.join(lines)


def scene_prompt(s):
    return ("Draw one illustration. %s\n\n%s\n\nSave it as %s.png. "
            "Draw only this single scene." % (s['en'], STYLE, s['slug']))


def main():
    with open(os.path.join(HERE, 'lie_types.json'), encoding='utf-8') as f:
        doc_name = json.load(f)['title']

    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    base = os.path.join(desktop, '클로드 문서 이미지')
    root = os.path.join(base, doc_name + ' 이미지')

    # 유형 수가 바뀌면 폴더 이름도 바뀐다. 옛 폴더는 지우고 새로 만든다.
    for old in os.listdir(base) if os.path.isdir(base) else []:
        if old.startswith('거짓말') and old.endswith('이미지') and old != os.path.basename(root):
            shutil.rmtree(os.path.join(base, old))
            print('옛 폴더 삭제:', old)

    redo = os.path.join(root, '다시 만들기 (한 장씩)')
    os.makedirs(redo, exist_ok=True)

    mp = master_prompt()
    url_file(os.path.join(root, '★ 전체 이미지 한번에 만들기 (여기부터).url'), chatgpt_url(mp))

    with open(os.path.join(root, '프롬프트 원문 (읽기용).txt'), 'w', encoding='utf-8') as f:
        f.write('[전체 한번에 만들기 프롬프트]\n\n' + mp + '\n\n\n[장면별 프롬프트]\n')
        for s in SCENES:
            f.write('\n\n--- %s ---\n%s\n' % (s['ko'], scene_prompt(s)))

    for s in SCENES:
        url_file(os.path.join(redo, s['ko'] + '.url'), chatgpt_url(scene_prompt(s)))

    print('폴더:', root)
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            full = os.path.join(dirpath, fn)
            print('  %-46s %6d bytes' % (os.path.relpath(full, root), os.path.getsize(full)))


if __name__ == '__main__':
    main()
