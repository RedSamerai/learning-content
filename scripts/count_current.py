#!/usr/bin/env python3
"""统计各年级内容"""
import json
from pathlib import Path
from collections import defaultdict

current = defaultdict(lambda: defaultdict(int))
for p in Path("output").rglob("*.json"):
    if "image" in str(p) or "audio" in str(p):
        continue
    parts = str(p.relative_to("output")).split("/")
    if len(parts) >= 3:
        subject = parts[0]
        grade = "/".join(parts[1:3])
        current[grade][subject] += 1

print("=" * 60)
print("📊 各年级内容统计")
print("=" * 60)

for grade in sorted(current.keys()):
    total = sum(current[grade].values())
    subjects = ", ".join([f"{s}:{c}" for s, c in sorted(current[grade].items())])
    print(f"\n【{grade}】 共{total}个")
    print(f"  {subjects}")

print("\n" + "=" * 60)
print(f"总计: {len(current)} 个年级段, {sum(sum(v.values()) for v in current.values())} 个知识点")
print("=" * 60)
