# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import random
from fractions import Fraction

from expr import Num, BinOp, Node
from numutil import (
    make_natural,
    make_proper_fraction,
    make_mixed_fraction,
    fraction_to_str,
)

OPS = ['+', '-', '*', '/']


def random_leaf(r: int) -> Node:
    """生成一个随机数叶子：自然数、真分数或带分数。"""
    choices = ['nat', 'frac', 'mixed'] if r >= 2 else ['nat']
    kind = random.choice(choices)
    if kind == 'nat':
        return Num(make_natural(r))
    elif kind == 'frac':
        f = make_proper_fraction(r)
        if f == 0:
            # 无法生成有效真分数时，退回自然数
            return Num(make_natural(r))
        return Num(f)
    else:
        return Num(make_mixed_fraction(r))


def valid_sub(left: Fraction, right: Fraction) -> bool:
    return left >= right


def valid_div(left: Fraction, right: Fraction) -> bool:
    if right == 0:
        return False
    val = left / right
    return Fraction(0, 1) < val < Fraction(1, 1)


def make_binop(op: str, l: Node, r: Node) -> BinOp:
    return BinOp(op=op, left=l, right=r)


def build_expr_with_ops(r: int, n_ops: int) -> Node:
    """随机构造一个包含 n_ops 运算符的表达式树，满足约束。"""
    assert n_ops >= 1

    # 首先构造一个合法的二元表达式
    left = random_leaf(r)
    right = random_leaf(r)
    for _ in range(100):
        op = random.choice(OPS)
        if op == '-':
            if valid_sub(left.evaluate(), right.evaluate()):
                node = make_binop(op, left, right)
                break
        elif op == '/':
            if valid_div(left.evaluate(), right.evaluate()):
                node = make_binop(op, left, right)
                break
        else:
            node = make_binop(op, left, right)
            break
        # 重试不同叶子
        left = random_leaf(r)
        right = random_leaf(r)
    else:
        # 兜底使用加法
        node = make_binop('+', left, right)

    # 继续拼接剩余的操作符，每次将当前树与一个新叶子组合
    for _ in range(n_ops - 1):
        leaf = random_leaf(r)
        built = None
        for _ in range(50):
            op = random.choice(OPS)
            if op == '-':
                if valid_sub(node.evaluate(), leaf.evaluate()):
                    built = make_binop(op, node, leaf)
                    break
                if valid_sub(leaf.evaluate(), node.evaluate()):
                    built = make_binop(op, leaf, node)
                    break
            elif op == '/':
                if valid_div(node.evaluate(), leaf.evaluate()):
                    built = make_binop(op, node, leaf)
                    break
                if valid_div(leaf.evaluate(), node.evaluate()):
                    built = make_binop(op, leaf, node)
                    break
            else:
                built = make_binop(op, node, leaf)
                break
            # 重试新的叶子
            leaf = random_leaf(r)
        if built is None:
            built = make_binop('+', node, leaf)
        node = built

    return node


def generate(r: int, n: int):
    """生成题目与答案文件，满足约束与去重。
    - -r 控制范围（不含 r）
    - -n 控制题目数量（最多 10000）
    - 运算符数不超过 3
    - e1 - e2 保证 e1 >= e2
    - e1  e2 的结果为真分数（在 0 与 1 之间）
    - 通过 + 与 * 的左右交换去重
    """
    if r < 1:
        raise ValueError("-r 范围必须 >= 1")
    if n < 1:
        raise ValueError("-n 题目数量必须 >= 1")

    cwd = os.getcwd()
    ex_path = os.path.join(cwd, "Exercises.txt")
    ans_path = os.path.join(cwd, "Answers.txt")

    seen = set()
    items = []

    attempts = 0
    target = n
    max_attempts = n * 200

    while len(items) < target and attempts < max_attempts:
        attempts += 1
        n_ops = random.randint(1, 3)
        expr = build_expr_with_ops(r, n_ops)
        k = expr.key()
        if k in seen:
            continue
        try:
            val = expr.evaluate()
        except ZeroDivisionError:
            continue
        seen.add(k)
        items.append((expr, val))

    with open(ex_path, "w", encoding="utf-8") as ex_f, open(ans_path, "w", encoding="utf-8") as ans_f:
        for expr, val in items:
            ex_line = f"{expr.to_str()} ="
            ans_line = fraction_to_str(val)
            ex_f.write(ex_line + "\n")
            ans_f.write(ans_line + "\n")

    return ex_path, ans_path
