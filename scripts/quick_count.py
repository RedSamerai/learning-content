#!/usr/bin/env python3
"""快速统计当前内容"""
from pathlib import Path
from collections import defaultdict

current = defaultdict(lambda: defaultdict(int))
for p in Path("output").rglob("*.json"):
    if "image" in str(p) or "audio" in str(p):
        continue
    rel = str(p.relative_to("output"))
    parts = rel.split("/")
    if len(parts) >= 3:
        subject = parts[0]
        grade = "/".join(parts[1:3])
        current[grade][subject] += 1

print("=== 当前内容统计 ===")
total = 0
for g in sorted(current.keys()):
    d = current[g]
    s = ", ".join([f"{k}:{v}" for k, v in d.items()])
    n = sum(d.values())
    total += n
    print(f"{g}: {n}个 [{s}]")
print(f"\n总计: {total}个知识点")
