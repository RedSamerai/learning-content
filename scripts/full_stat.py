#!/usr/bin/env python3
"""完整统计 - 基于实际目录"""
from pathlib import Path
from collections import defaultdict

# 统计实际内容
current = defaultdict(lambda: defaultdict(int))
for p in Path("output").rglob("*.json"):
    if "image" in str(p) or "audio" in str(p):
        continue
    rel = str(p.relative_to("output"))
    parts = rel.split("/")
    if len(parts) >= 4:
        subject = parts[0]
        grade = parts[1]
        topic = parts[2]
        current[grade][subject] += 1

print("=" * 70)
print("📊 当前内容统计（按年级）")
print("=" * 70)

total = 0
for grade in sorted(current.keys()):
    d = current[grade]
    n = sum(d.values())
    total += n
    print(f"\n【{grade}】共{n}个")
    for subj, cnt in sorted(d.items()):
        print(f"  {subj}: {cnt}个")

print("\n" + "=" * 70)
print(f"总计: {total}个知识点")
print("=" * 70)

# 检查质量：哪些有空内容
print("\n" + "=" * 70)
print("📋 质量检查 - 空内容")
print("=" * 70)

empty_count = 0
for p in Path("output").rglob("*.json"):
    if "image" in str(p) or "audio" in str(p):
        continue
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        exp = len(data.get("explanation", ""))
        quiz = len(data.get("quiz", ""))
        audio = len(data.get("audio", []))
        if exp < 100 or quiz == "":
            print(f"  {p.parent.name}: 讲解{exp}字, 题目{'空' if quiz=='' else str(len(quiz))}字, 音频{audio}个")
            empty_count += 1
    except:
        pass

print(f"\n共{empty_count}个知识点存在内容质量问题")
