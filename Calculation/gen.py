# -*- coding: utf-8 -*-
import os
def generate(r: int, n: int):
    if r < 1:
        raise ValueError("-r 范围必须 >= 1")
    if n < 1:
        raise ValueError("-n 题目数量必须 >= 1")

    cwd = os.getcwd()
    ex_path = os.path.join(cwd, "Exercises.txt")
    ans_path = os.path.join(cwd, "Answers.txt")

    with open(ex_path, "w", encoding="utf-8") as ex_f, open(ans_path, "w", encoding="utf-8") as ans_f:
        for i in range(1, n + 1):
            # 题目格式：表达式 + 等号
            ex_f.write(f"1 + {i} =\n")
            ans_f.write(f"{1 + i}\n")

    return ex_path, ans_path