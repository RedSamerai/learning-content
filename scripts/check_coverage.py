#!/usr/bin/env python3
"""统计各年级实际知识点数量"""
import json
from pathlib import Path

# 定义各年级应有的知识点数量（参考新课标）
EXPECTED = {
    # 幼儿园
    "幼儿园(3-4岁)": 30, "幼儿园(4-5岁)": 30, "幼儿园(5-6岁)": 30,
    # 幼小衔接
    "幼小衔接": 40,
    # 小学
    "一年级上": 60, "一年级下": 50,
    "二年级上": 55, "二年级下": 50,
    "三年级上": 55, "三年级下": 50,
    "四年级上": 50, "四年级下": 45,
    "五年级上": 50, "五年级下": 45,
    "六年级上": 45, "六年级下": 40,
    # 初中
    "七年级上": 55, "七年级下": 50,
    "八年级上": 55, "八年级下": 50,
    "九年级上": 55, "九年级下": 50
}

# 统计现有
actual = {}
for p in Path('output').rglob('*.json'):
    if p.parent.name in ['image', 'audio']:
        continue
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        grade = data.get('grade', data.get('age_group', '未知'))
        actual[grade] = actual.get(grade, 0) + 1
    except:
        pass

print("=" * 70)
print("知识点覆盖缺口分析")
print("=" * 70)
print(f"{'年级':<15} {'应有':>8} {'已有':>8} {'缺口':>8} {'覆盖率':>8}")
print("-" * 70)

total_expected = 0
total_actual = 0
for grade in sorted(EXPECTED.keys()):
    exp = EXPECTED[grade]
    act = actual.get(grade, 0)
    gap = exp - act
    rate = act / exp * 100 if exp > 0 else 0
    total_expected += exp
    total_actual += act
    print(f"{grade:<15} {exp:>8} {act:>8} {gap:>8} {rate:>7.0f}%")

print("-" * 70)
print(f"{'合计':<15} {total_expected:>8} {total_actual:>8} {total_expected - total_actual:>8} {total_actual/total_expected*100:.0f}%")
print("=" * 70)

# 按科目统计
print("\n【按科目统计】")
subjects = {}
for p in Path('output').rglob('*.json'):
    if p.parent.name in ['image', 'audio']:
        continue
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        subject = data.get('subject', '未知')
        grade = data.get('grade', data.get('age_group', '未知'))
        key = f"{subject}/{grade}"
        subjects[key] = subjects.get(key, 0) + 1
    except:
        pass

print(f"{'科目/年级':<30} {'数量':>6}")
print("-" * 40)
for k in sorted(subjects.keys()):
    print(f"{k:<30} {subjects[k]:>6}")