import re
import sys

SEMI = r'[;；]{2,}'
LETTER = r'[A-DＡ-Ｄ]'

START_RE = re.compile(rf'^[ \t]*{SEMI}[ \t]*$')
ANS_RE = re.compile(rf'^[ \t]*{SEMI}[ \t]*({LETTER}+)[ \t]*$')
CARD_SEP_RE = re.compile(r'^[ \t]*\+\+\+[ \t]*$')
FRONT_BACK_RE = re.compile(r'^[ \t]*\*\*\*[ \t]*$')


def normalize_letters(s):
    return s.translate(str.maketrans('ＡＢＣＤ', 'ABCD'))

def transform_body(text):
    # 全角字母 A-D 转半角
    text = text.translate(str.maketrans('ＡＢＣＤ', 'ABCD'))
    # 选项标号统一：A．/A、 -> A.
    text = re.sub(r'([A-D])[．、]', r'\1.', text)
    # 把所有空白（换行/空行/制表符）压成单空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 关键：用消费式正则，把 A. / B. / C. / D. 连同前面的空白一起替换成 \nX.
    text = re.sub(r'\s*([A-D])\.', r'\n\1.', text)
    return text.strip('\n')

def process_choices(lines):
    out = []
    i = 0
    total = 0
    filled = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if START_RE.match(line):
            j = i + 1
            body_lines = []
            answer = None
            while j < n:
                cur = lines[j]
                m = ANS_RE.match(cur)
                if m:
                    answer = m.group(1)
                    j += 1
                    break
                if START_RE.match(cur):
                    break
                # 关键：不再遇到空行就 break，继续收集直到 ;;; 或 ;;;答案
                body_lines.append(cur)
                j += 1

            body_text = ''.join(body_lines)
            if not body_text.strip() and not answer:
                i = j
                continue

            total += 1
            body_text = transform_body(body_text)
            out.append(';;;\n')
            if body_text:
                out.append(body_text + '\n')
            if answer:
                out.append(f';;;{normalize_letters(answer)}\n')
                filled += 1
            else:
                out.append(';;;\n')

            while j < n and lines[j].strip() == '':
                j += 1
            if j < n:
                out.append('\n')
            i = j
        else:
            out.append(line)
            i += 1

    return out, total, filled


def fix_card_separators(text):
    """每个 +++ 卡片内若无 ***，则在卡片内容末尾补一个 ***。
    无论后面有没有下一个 +++，都生效。"""
    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)

    while i < n:
        if CARD_SEP_RE.match(lines[i]):
            out.append(lines[i])
            i += 1
            card_lines = []
            has_sep = False
            while i < n and not CARD_SEP_RE.match(lines[i]):
                if FRONT_BACK_RE.match(lines[i]):
                    has_sep = True
                card_lines.append(lines[i])
                i += 1
            if not has_sep:
                while card_lines and card_lines[-1].strip() == '':
                    card_lines.pop()
                if card_lines:
                    card_lines.append('')
                    card_lines.append('***')
            out.extend(card_lines)
        else:
            out.append(lines[i])
            i += 1

    return '\n'.join(out)


def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines, total, filled = process_choices(lines)
    text = ''.join(out_lines)
    text = fix_card_separators(text)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(
        f'已处理 {path}：共 {total} 道题，其中 {filled} 道含答案，{total - filled} 道待补答案。'
    )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: py format.py a.md')
        sys.exit(1)
    for path in sys.argv[1:]:
        process_file(path)
