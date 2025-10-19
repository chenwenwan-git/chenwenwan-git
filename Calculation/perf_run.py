# -*- coding: utf-8 -*-
"""
批量性能测试脚本：运行多组(r, n)生成，收集Perf.txt数据，写入perf_data.csv。
"""
import os
import re
import csv
from typing import Tuple, Dict, List

import gen

TEST_CASES: List[Tuple[int, int]] = [
    (10, 100),
    (10, 1000),
    (20, 1000),
    (20, 5000),
    (10, 10000),
    (20, 10000),
]

PERF_FILE = os.path.join(os.getcwd(), 'Perf.txt')
CSV_FILE = os.path.join(os.getcwd(), 'perf_data.csv')

# 解析Perf.txt内容到字典
PERF_PATTERNS = {
    'Range r': re.compile(r'^Range r:\s*(\d+)'),
    'Target n': re.compile(r'^Target n:\s*(\d+)'),
    'Generated': re.compile(r'^Generated:\s*(\d+)'),
    'Attempts': re.compile(r'^Attempts:\s*(\d+)'),
    'Duplicates skipped': re.compile(r'^Duplicates skipped:\s*(\d+)'),
    'ZeroDivision skipped': re.compile(r'^ZeroDivision skipped:\s*(\d+)'),
    'Op count distribution': re.compile(r'^Op count distribution:\s*1->(\d+),\s*2->(\d+),\s*3->(\d+)'),
    'Time': re.compile(r'^Time:\s*(\d+)\s*ms'),
}


def parse_perf() -> Dict[str, int]:
    if not os.path.exists(PERF_FILE):
        raise FileNotFoundError('未找到Perf.txt，请先执行带--stats的生成。')
    metrics: Dict[str, int] = {}
    with open(PERF_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            for key, pat in PERF_PATTERNS.items():
                m = pat.match(line)
                if m:
                    if key == 'Op count distribution':
                        metrics['op1'] = int(m.group(1))
                        metrics['op2'] = int(m.group(2))
                        metrics['op3'] = int(m.group(3))
                    elif key == 'Time':
                        metrics['time_ms'] = int(m.group(1))
                    else:
                        name = key.lower().replace(' ', '_')  # 简单标准化键
                        metrics[name] = int(m.group(1))
    return metrics


def run_cases(cases: List[Tuple[int, int]]):
    rows = []
    for r, n in cases:
        print(f'Running r={r}, n={n} ...')
        gen.generate(r=r, n=n, write_stats=True)
        m = parse_perf()
        rows.append({
            'r': r,
            'n': n,
            'generated': m.get('generated', 0),
            'attempts': m.get('attempts', 0),
            'duplicates': m.get('duplicates_skipped', 0),
            'zero_div': m.get('zerodivision_skipped', 0),
            'op1': m.get('op1', 0),
            'op2': m.get('op2', 0),
            'op3': m.get('op3', 0),
            'time_ms': m.get('time_ms', 0),
        })
    # 写CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=['r', 'n', 'generated', 'attempts', 'duplicates', 'zero_div', 'op1', 'op2', 'op3', 'time_ms'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'已生成 {CSV_FILE}，包含 {len(rows)} 行数据。')


if __name__ == '__main__':
    run_cases(TEST_CASES)