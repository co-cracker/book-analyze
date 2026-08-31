# -*- coding: utf-8 -*-
r"""거짓말 10종 도감 문서용 ChatGPT 이미지 생성 바로가기를 만든다.

바탕화면 \ 클로드 문서 이미지 \ 거짓말 10종 도감 이미지 \
    ★ 전체 이미지 한번에 만들기 (여기부터).url
    프롬프트 원문 (읽기용).txt
    다시 만들기 (한 장씩) \ 01 ....url ...
"""
import os
from urllib.parse import quote

DOC_NAME = '거짓말 10종 도감'

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
        'slug': '01_amount-inflated',
        'ko': '01 수량 부풀리기 (A군 세기)',
        'en': (
            "Two children standing side by side, seen from the front. "
            "The child on the left holds a very small box with both hands, calm and matter-of-fact. "
            "The child on the right, turned slightly toward a third child off to the side, "
            "holds a box that is enormously larger, arms stretched wide around it, "
            "leaning forward eagerly as if passing the story along. "
            "The two boxes are the same shape, only the size differs, so the contrast is obvious at a glance."
        )
    },
    {
        'slug': '02_arrow-flipped',
        'ko': '02 화살표 뒤집기 (B군 이음새)',
        'en': (
            "A child kneeling on the floor beside a row of two large domino tiles. "
            "The first tile has already tipped and is leaning into the second one. "
            "Beside this row, the same child's other hand is picking up the fallen tile and "
            "setting it back so the lean would point the opposite way. "
            "The two tiles are identical in size and shape; only the direction of the lean differs between the two rows."
        )
    },
    {
        'slug': '03_fence-widened',
        'ko': '03 대상 넓히기 (C군 범위)',
        'en': (
            "One child standing inside a small low picket fence drawn as a simple loop around their feet. "
            "Another child crouches at the edge of that fence and pulls one section of it outward with both hands, "
            "stretching the loop so that it now also encircles three other children who are standing further away "
            "and were never inside it. The stretched fence line is clearly wider and looser than the original small loop."
        )
    },
    {
        'slug': '04_extra-added',
        'ko': '04 결론 얹기 (D군 없던 말)',
        'en': (
            "Three children standing in a row, each turned toward the next, passing a stack of plates hand to hand. "
            "The first child holds three plates, the second child holds the same three plates, "
            "but the third child at the end of the row holds four, having quietly added one more plate on top. "
            "The extra plate sits slightly crooked on the stack so it reads as added, not original."
        )
    },
    {
        'slug': '05_side-by-side-check',
        'ko': '05 나란히 놓고 대조하기 (찾는 순서)',
        'en': (
            "A child sitting at a low table seen from a slight angle, two blank sheets of paper laid side by side "
            "flat on the table in front of them. The child leans over the sheets and presses one index finger onto "
            "a line on the left sheet and the other index finger onto the matching line on the right sheet, "
            "eyes down and focused, comparing the two rows against each other. "
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
        "I need %d separate illustrations for a Korean reading-education handout about how a sentence "
        "can be subtly twisted. Draw them ONE AT A TIME." % len(SCENES),
        "",
        STYLE,
        "",
        "Rules: draw only ONE scene per image. Never combine two scenes into a single picture. "
        "After each image, stop and wait for me to type the next message before drawing the following one.",
        "",
        "Here are the scenes in order:",
        "",
    ]
    for i, s in enumerate(SCENES, 1):
        lines.append("%d. (save as %s.png) %s" % (i, s['slug'], s['en']))
        lines.append("")
    lines.append(
        "When all %d images are finished, rename them exactly as the filenames above "
        "and bundle all of them into a single .zip file for me to download." % len(SCENES)
    )
    return '\n'.join(lines)


def scene_prompt(s):
    return ("Draw one illustration. %s\n\n%s\n\nSave it as %s.png. "
            "Draw only this single scene." % (s['en'], STYLE, s['slug']))


def main():
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    root = os.path.join(desktop, '클로드 문서 이미지', DOC_NAME + ' 이미지')
    redo = os.path.join(root, '다시 만들기 (한 장씩)')
    os.makedirs(redo, exist_ok=True)

    mp = master_prompt()
    url_file(os.path.join(root, '★ 전체 이미지 한번에 만들기 (여기부터).url'), chatgpt_url(mp))

    with open(os.path.join(root, '프롬프트 원문 (읽기용).txt'), 'w', encoding='utf-8') as f:
        f.write('[전체 한번에 만들기 프롬프트]\n\n')
        f.write(mp)
        f.write('\n\n\n[장면별 프롬프트]\n')
        for s in SCENES:
            f.write('\n\n--- %s ---\n%s\n' % (s['ko'], scene_prompt(s)))

    for s in SCENES:
        url_file(os.path.join(redo, s['ko'] + '.url'), chatgpt_url(scene_prompt(s)))

    print('폴더:', root)
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            full = os.path.join(dirpath, fn)
            print('  %-52s %6d bytes' % (os.path.relpath(full, root), os.path.getsize(full)))


if __name__ == '__main__':
    main()
