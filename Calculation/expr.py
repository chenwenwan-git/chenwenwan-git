# -*- coding: utf-8 -*-
from __future__ import annotations
from fractions import Fraction
from dataclasses import dataclass
from typing import Union

# 操作符优先级（数值越大优先级越高）
PREC = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
}

Node = Union["Num", "BinOp"]


@dataclass(frozen=True)
class Num:
    value: Fraction

    def evaluate(self) -> Fraction:
        return Fraction(self.value.numerator, self.value.denominator)

    def op_count(self) -> int:
        return 0

    def key(self) -> str:
        v = self.evaluate()
        return f"N:{v.numerator}/{v.denominator}"

    def to_str(self) -> str:
        from numutil import fraction_to_str
        return fraction_to_str(self.evaluate())


@dataclass(frozen=True)
class BinOp:
    op: str
    left: Node
    right: Node

    def evaluate(self) -> Fraction:
        lv = self.left.evaluate()
        rv = self.right.evaluate()
        if self.op == '+':
            return lv + rv
        if self.op == '-':
            return lv - rv
        if self.op == '*':
            return lv * rv
        if self.op == '/':
            if rv == 0:
                raise ZeroDivisionError('除数为0')
            return lv / rv
        raise ValueError(f'未知操作符: {self.op}')

    def op_count(self) -> int:
        return 1 + self.left.op_count() + self.right.op_count()

    def key(self) -> str:
        lk = self.left.key()
        rk = self.right.key()
        if self.op == '+':
            a, b = sorted([lk, rk])
            return f"A:({a},{b})"
        if self.op == '*':
            a, b = sorted([lk, rk])
            return f"M:({a},{b})"
        if self.op == '-':
            return f"S:[{lk},{rk}]"
        if self.op == '/':
            return f"D:[{lk},{rk}]"
        raise ValueError(f'未知操作符: {self.op}')

    def to_str(self) -> str:
        def needs_paren(child: Node, parent_op: str, is_left: bool) -> bool:
            if isinstance(child, Num):
                return False
            cp = PREC[child.op]
            pp = PREC[parent_op]
            if cp < pp:
                return True
            if parent_op in ('-', '/') and isinstance(child, BinOp) and child.op == parent_op:
                return True
            return False

        lstr = self.left.to_str()
        rstr = self.right.to_str()
        if needs_paren(self.left, self.op, True):
            lstr = f"( {lstr} )"
        if needs_paren(self.right, self.op, False):
            rstr = f"( {rstr} )"
        symbol = {
            '+': '+',
            '-': '-',
            '*': '×',
            '/': '÷',
        }[self.op]
        return f"{lstr} {symbol} {rstr}"


