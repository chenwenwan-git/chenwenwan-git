# -*- coding: utf-8 -*-
import os


def grade(exercise_file: str, answer_file: str):
    # 简单存在性检查
    if not os.path.exists(exercise_file):
        raise FileNotFoundError(f"题目文件不存在：{exercise_file}")
    if not os.path.exists(answer_file):
        raise FileNotFoundError(f"答案文件不存在：{answer_file}")

    # 目前不做真实比对，仅输出格式化的占位结果
    out_path = os.path.join(os.getcwd(), "Grade.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("Correct: 0 ()\n")
        f.write("Wrong: 0 ()\n")
    return out_path