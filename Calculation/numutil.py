# -*- coding: utf-8 -*-
from fractions import Fraction
import random

APOSTROPHE = "\u2019"  # 右单引号，用于带分数打印


def make_natural(r: int) -> Fraction:
    """返回 [0, r-1] 的自然数作为 Fraction。"""
    if r < 1:
        raise ValueError("范围 r 必须 >= 1")
    return Fraction(random.randint(0, max(0, r - 1)), 1)


def make_proper_fraction(r: int) -> Fraction:
    """生成真分数：分母在 [2, r-1]，分子在 [1, 分母-1]。"""
    if r < 2:
        # r=1 或 2 时几乎无法生成真分数；调用方应处理
        return Fraction(0, 1)
    den = random.randint(2, max(2, r - 1))
    num = random.randint(1, den - 1)
    return Fraction(num, den)


def make_mixed_fraction(r: int) -> Fraction:
    """生成带分数的值（以 Fraction 表示）：整数部分 [0, r-1]，真分数部分来源于 r。"""
    if r < 2:
        # 无法稳定生成混合分数时，退化为自然数
        return make_natural(r)
    int_part = random.randint(0, max(0, r - 1))
    frac = make_proper_fraction(r)
    return Fraction(int_part, 1) + frac


def fraction_to_str(x: Fraction) -> str:
    """将 Fraction 按规范打印为：
    - 真分数：a/b
    - 带分数：A/b （使用右单引号 \u2019）
    - 整数：A
    """
    x = Fraction(x.numerator, x.denominator)  # 规范化到最简形式
    if x.denominator == 1:
        return f"{x.numerator}"
    # 处理负数（题目生成约束避免负结果，但打印函数通用）
    sign = '-' if x < 0 else ''
    ax = abs(x)
    if ax.numerator < ax.denominator:
        return f"{sign}{ax.numerator}/{ax.denominator}"
    # 带分数
    int_part = ax.numerator // ax.denominator
    rem = ax - int_part
    if rem == 0:
        return f"{sign}{int_part}"
    return f"{sign}{int_part}{APOSTROPHE}{rem.numerator}/{rem.denominator}"


def parse_fraction_str(s: str) -> Fraction:
    """解析字符串到 Fraction，支持：
    - 整数："A"
    - 真分数："a/b"
    - 带分数："A/b" 或 "A'a/b"（兼容 ASCII 引号）
    可包含前导负号：-A, -a/b, -A/b
    """
    s = s.strip()
    if not s:
        raise ValueError("空字符串")
    # 负号处理
    neg = False
    if s.startswith('-'):
        neg = True
        s = s[1:]
    # 兼容两种引号
    if APOSTROPHE in s or "'" in s:
        sep = APOSTROPHE if APOSTROPHE in s else "'"
        ipart, frac = s.split(sep, 1)
        int_part = int(ipart)
        num, den = frac.split('/')
        f = Fraction(int(num), int(den))
        val = Fraction(int_part, 1) + f
    elif '/' in s:
        num, den = s.split('/')
        val = Fraction(int(num), int(den))
    else:
        val = Fraction(int(s), 1)
    return -val if neg else val
