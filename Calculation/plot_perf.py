import csv
import os

INPUT = 'perf_data.csv'
PNG_OUT = 'perf_plot.png'
TXT_OUT = 'perf_plot.txt'

def load_data(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                'r': int(r['r']),
                'n': int(r['n']),
                'time_ms': float(r['time_ms']),
                'generated': int(r['generated']),
                'attempts': int(r['attempts']),
                'duplicates': int(r['duplicates']),
                'zero_div': int(r['zero_div']),
                'op1': int(r['op1']),
                'op2': int(r['op2']),
                'op3': int(r['op3']),
            })
    return rows


def write_txt_summary(rows, path):
    # Group by r and sort by n
    by_r = {}
    for row in rows:
        by_r.setdefault(row['r'], []).append(row)
    for r, items in by_r.items():
        items.sort(key=lambda x: x['n'])
    with open(path, 'w', encoding='utf-8') as f:
        f.write('Performance Summary (fallback without matplotlib)\n')
        for r in sorted(by_r.keys()):
            f.write(f"\nr={r}:\n")
            for it in by_r[r]:
                f.write(f"  n={it['n']}: time_ms={it['time_ms']}, duplicates={it['duplicates']}\n")
    return path


def plot_png(rows, path):
    import matplotlib.pyplot as plt
    # Group by r
    by_r = {}
    for row in rows:
        by_r.setdefault(row['r'], []).append(row)
    # Plot
    plt.figure(figsize=(8, 5))
    for r, items in sorted(by_r.items()):
        items.sort(key=lambda x: x['n'])
        xs = [it['n'] for it in items]
        ys = [it['time_ms'] for it in items]
        plt.plot(xs, ys, marker='o', label=f"r={r}")
    plt.xlabel('n (questions)')
    plt.ylabel('time (ms)')
    plt.title('Generation Performance by r')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path)
    return path


def main():
    if not os.path.exists(INPUT):
        print(f"Input file '{INPUT}' not found. Run 'python perf_run.py' first.")
        return 1
    rows = load_data(INPUT)
    try:
        out = plot_png(rows, PNG_OUT)
        print(f"Plot saved: {os.path.abspath(out)}")
    except Exception as e:
        print(f"matplotlib not available or plotting failed: {e}")
        out = write_txt_summary(rows, TXT_OUT)
        print(f"Text summary saved: {os.path.abspath(out)}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())