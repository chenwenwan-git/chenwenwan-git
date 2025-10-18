# -*- coding: utf-8 -*-
import os
from fractions import Fraction
from typing import List

from numutil import parse_fraction_str

# 运算符优先级（数值越大优先级越高）
PREC = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
}


def _normalize_tokens(raw_tokens: List[str]) -> List[str]:
    """将原始token标准化：
    - 将“×”映射为“*”，将“÷”映射为“/”
    - 保持括号与数字不变
    """
    norm = []
    for t in raw_tokens:
        t = t.strip()
        if not t:
            continue
        if t == '×':
            norm.append('*')
        elif t == '÷':
            norm.append('/')
        else:
            norm.append(t)
    return norm


def _to_tokens(expr_line: str) -> List[str]:
    """将题目一行去掉等号并分词。题目中运算符与括号已被空格分隔。"""
    s = expr_line.strip()
    # 去掉末尾的等号及其前后的空格
    if s.endswith('='):
        s = s[:-1].strip()
    # 直接按空格分隔（生成器已保证空格）
    raw_tokens = s.split()
    return _normalize_tokens(raw_tokens)


def _shunting_yard(tokens: List[str]) -> List[str]:
    """将中缀表达式tokens转换为RPN（逆波兰表达式）。"""
    output: List[str] = []
    ops: List[str] = []

    def is_number(tok: str) -> bool:
        try:
            parse_fraction_str(tok)
            return True
        except Exception:
            return False

    for tok in tokens:
        if is_number(tok):
            output.append(tok)
        elif tok in PREC:
            while ops and ops[-1] in PREC and PREC[ops[-1]] >= PREC[tok]:
                output.append(ops.pop())
            ops.append(tok)
        elif tok == '(':
            ops.append(tok)
        elif tok == ')':
            while ops and ops[-1] != '(':
                output.append(ops.pop())
            if not ops:
                raise ValueError('括号不匹配')
            ops.pop()  # 弹出'('
        else:
            raise ValueError(f'未知token: {tok}')

    while ops:
        if ops[-1] in ('(', ')'):
            raise ValueError('括号不匹配')
        output.append(ops.pop())

    return output


def _eval_rpn(rpn: List[str]) -> Fraction:
    """用Fraction计算RPN值。"""
    st: List[Fraction] = []
    for tok in rpn:
        if tok in ('+', '-', '*', '/'):
            if len(st) < 2:
                raise ValueError('表达式有误：操作数不足')
            b = st.pop()
            a = st.pop()
            if tok == '+':
                st.append(a + b)
            elif tok == '-':
                st.append(a - b)
            elif tok == '*':
                st.append(a * b)
            elif tok == '/':
                if b == 0:
                    raise ZeroDivisionError('除数为0')
                st.append(a / b)
        else:
            st.append(parse_fraction_str(tok))
    if len(st) != 1:
        raise ValueError('表达式有误：剩余栈元素不为1')
    return st[0]


def _eval_expr_line(expr_line: str) -> Fraction:
    tokens = _to_tokens(expr_line)
    rpn = _shunting_yard(tokens)
    return _eval_rpn(rpn)


def grade(exercise_file: str, answer_file: str):
    # 存在性检查
    if not os.path.exists(exercise_file):
        raise FileNotFoundError(f"题目文件不存在：{exercise_file}")
    if not os.path.exists(answer_file):
        raise FileNotFoundError(f"答案文件不存在：{answer_file}")

    # 读取题目与答案（跳过空行），保持编号为非空行的顺序（从1开始）
    with open(exercise_file, 'r', encoding='utf-8') as ef:
        exercise_lines = [line.strip() for line in ef if line.strip()]
    with open(answer_file, 'r', encoding='utf-8') as af:
        answer_lines = [line.strip() for line in af if line.strip()]

    # 计算标准答案
    expected: List[Fraction] = []
    for line in exercise_lines:
        val = _eval_expr_line(line)
        expected.append(val)

    # 对用户答案进行比对
    correct_ids: List[int] = []
    wrong_ids: List[int] = []

    # 若答案数量与题目数量不一致，按较小数量进行比对，剩余视为错误
    m = min(len(expected), len(answer_lines))
    for i in range(m):
        try:
            ans = parse_fraction_str(answer_lines[i])
        except Exception:
            wrong_ids.append(i + 1)
            continue
        if ans == expected[i]:
            correct_ids.append(i + 1)
        else:
            wrong_ids.append(i + 1)
    # 多余的题目或答案视为错误
    if len(expected) > m:
        wrong_ids.extend(range(m + 1, len(expected) + 1))
    # 如果答案多于题目，忽略多余答案（不计入错误）

    out_path = os.path.join(os.getcwd(), 'Grade.txt')
    def fmt_ids(ids: List[int]) -> str:
        return '(' + ', '.join(str(i) for i in ids) + ')' if ids else '()'

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"Correct: {len(correct_ids)} {fmt_ids(correct_ids)}\n")
        f.write(f"Wrong: {len(wrong_ids)} {fmt_ids(wrong_ids)}\n")

    return out_path