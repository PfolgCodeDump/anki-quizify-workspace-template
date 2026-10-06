import re
import sys
import string

SEMI = r'[;；]{2,}'
# 字母范围：半角 A-Z a-z 和全角 Ａ-Ｚ ａ-ｚ
LETTER_PATTERN = r'[A-Za-zＡ-Ｚａ-ｚ]'

START_RE = re.compile(rf'^[ \t]*{SEMI}[ \t]*$')
# 答案行：分号后包含至少一个字母
ANS_RE = re.compile(rf'^[ \t]*{SEMI}[ \t]*(?=.*{LETTER_PATTERN})(.*?)[ \t]*$')
CARD_SEP_RE = re.compile(r'^[ \ts]*\+\+\+[ \t]*$')
FRONT_BACK_RE = re.compile(r'^[ \t]*\*\*\*[ \t]*$')

# 全角字母转半角映射表
FULL_UPPER = ''.join(chr(ord('Ａ') + i) for i in range(26))
FULL_LOWER = ''.join(chr(ord('ａ') + i) for i in range(26))
TRANS_TABLE = str.maketrans(
    FULL_UPPER + FULL_LOWER, string.ascii_uppercase + string.ascii_lowercase
)


def normalize_letters(s):
    """提取字符串中的所有字母，全角转半角，统一转大写。"""

    s = s.translate(TRANS_TABLE)
    s = s.upper()
    return ''.join(re.findall(r'[A-Z]', s))


def transform_body(text):
    """处理题目正文：全角字母转半角、压缩空白、选项标号统一并转大写。"""

    # 全角字母转半角
    text = text.translate(TRANS_TABLE)
    # 把所有空白（换行/空行/制表符）压成单空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 选项标号统一：匹配 空白 + 字母 + [．、.]，替换为 \n大写字母.
    text = re.sub(
        r'\s*([A-Za-z])[．、.]', lambda m: '\n' + m.group(1).upper() + '.', text
    )
    return text.strip('\n')


def normalize_separators(lines):
    """将整行仅由 2 个及以上 + 或 * 组成的行统一为恰好 3 个。"""
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped and set(stripped) == {'+'} and len(stripped) >= 2:
            out.append('+++\n')
        elif stripped and set(stripped) == {'*'} and len(stripped) >= 2:
            out.append('***\n')
        else:
            out.append(line)
    return out


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
                    answer = normalize_letters(m.group(1))
                    j += 1
                    break
                if START_RE.match(cur):
                    break
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
                out.append(f';;;{answer}\n')
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

    # 先规范化 +++ / *** 的数量
    lines = normalize_separators(lines)

    out_lines, total, filled = process_choices(lines)
    text = ''.join(out_lines)
    text = fix_card_separators(text)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(
        f'Processed {path}: {total} question(s) total, '
        f'{filled} with answer(s), {total - filled} missing answer(s).'
    )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: py format.py a.md')
        sys.exit(1)
    for path in sys.argv[1:]:
        process_file(path)
