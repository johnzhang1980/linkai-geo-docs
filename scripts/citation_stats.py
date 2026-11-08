#!/usr/bin/env python3
"""引用率统计：读 linkai-geo-citation-ledger.csv，输出每引擎/每组的提及率与引用率。
用法: python3 citation_stats.py [ledger.csv]
口径: mentioned/linked 填 y/n/空(未测)；空值不计入分母。"""
import csv, sys, collections
p = sys.argv[1] if len(sys.argv) > 1 else "linkai-geo-citation-ledger.csv"
rows = [r for r in csv.DictReader(open(p, encoding="utf-8-sig"))]

def rate(rows, field):
    v = [r[field].strip().lower() for r in rows if r[field].strip().lower() in ("y","n")]
    return (sum(1 for x in v if x=="y"), len(v))

print(f"{'维度':<22}{'提及':>6}{'已测':>6}{'提及率':>9}{'引用':>6}{'引用率':>9}")
print("-"*60)
def show(label, rs):
    m, mn = rate(rs, "mentioned"); c, cn = rate(rs, "linked")
    mr = f"{m/mn:.0%}" if mn else "-"
    cr = f"{c/cn:.0%}" if cn else "-"
    print(f"{label:<20}{m:>6}{mn:>6}{mr:>10}{c:>6}{cr:>10}")

show("全部", rows)
by_eng = collections.defaultdict(list)
by_grp = collections.defaultdict(list)
for r in rows:
    by_eng[r["engine"]].append(r); by_grp[r["group"]].append(r)
for e, rs in by_eng.items(): show(e, rs)
print("-"*60)
for g, rs in by_grp.items(): show(f"[组] {g}", rs)

# 引用到的 URL 排行
urls = collections.Counter(r["cited_url"].strip() for r in rows if r["cited_url"].strip())
if urls:
    print("\n被引用 URL:")
    for u, n in urls.most_common(): print(f"  {n:>3}  {u}")
