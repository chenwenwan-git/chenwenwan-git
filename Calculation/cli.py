# -*- coding: utf-8 -*-
import argparse
import sys

from .gen import generate
from .grade import grade

MAX_N = 10000


def positive_int(value: str) -> int:
    try:
        iv = int(value)
    except Exception:
        raise argparse.ArgumentTypeError("必须为自然数")
    if iv < 1:
        raise argparse.ArgumentTypeError("必须为>=1的自然数")
    return iv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Myapp",
        description=(
            "自动生成小学四则运算题目与评分统计。\n"
            "示例：Myapp.exe -r 10 -n 10 （生成题目）；\n"
            "示例：Myapp.exe -e Exercises.txt -a Answers.txt （评分）。"
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    # 生成命令
    gen_parser = subparsers.add_parser("generate", help="生成题目与答案文件")
    gen_parser.add_argument("-r", type=positive_int, required=True, help="数值范围（不含r）")
    gen_parser.add_argument("-n", type=positive_int, default=100, help="题目数量（默认100，最大10000）")

    # 评分命令
    grade_parser = subparsers.add_parser("grade", help="对题目与答案文件进行评分统计")
    grade_parser.add_argument("-e", type=str, required=True, help="题目文件路径")
    grade_parser.add_argument("-a", type=str, required=True, help="答案文件路径")

    return parser


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()

    # 无参数时打印帮助
    if not argv:
        parser.print_help()
        sys.exit(2)

    args = parser.parse_args(argv)

    if args.command == "generate":
        r = args.r
        n = args.n
        if n > MAX_N:
            print(f"题目数量最多支持 {MAX_N}，当前输入为 {n}")
            sys.exit(2)
        out_ex, out_ans = generate(r=r, n=n)
        print(f"已生成占位题目与答案：\nExercises -> {out_ex}\nAnswers   -> {out_ans}")
        sys.exit(0)

    elif args.command == "grade":
        efile = args.e
        afile = args.a
        out_grade = grade(exercise_file=efile, answer_file=afile)
        print(f"已生成评分结果：\nGrade -> {out_grade}")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(2)