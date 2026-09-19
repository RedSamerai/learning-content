#!/usr/bin/env python3
"""全面统计各年级内容质量问题"""
import json
from pathlib import Path

# 新课标要求的知识点数量（估算）
EXPECTED = {
    "幼儿园(3-4岁)": 30, "幼儿园(4-5岁)": 30, "幼儿园(5-6岁)": 30,
    "幼小衔接": 40,
    "一年级上": 60, "一年级下": 50,
    "二年级上": 55, "二年级下": 50,
    "三年级上": 55, "三年级下": 50,
    "四年级上": 50, "四年级下": 45,
    "五年级上": 50, "五年级下": 45,
    "六年级上": 45, "六年级下": 40,
    "七年级上": 55, "七年级下": 50,
    "八年级上": 55, "八年级下": 50,
    "九年级上": 55, "九年级下": 50
}

grades = {}
for p in Path('output').rglob('*.json'):
    if p.parent.name in ['image', 'audio']:
        continue
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        grade = data.get('grade', data.get('age_group', '未知'))
        if grade not in grades:
            grades[grade] = {'total': 0, 'has_quiz': 0, 'empty_quiz': 0, 'thin_quiz': 0, 'has_audio': 0, 'empty_audio': 0, 'thin_explain': 0}
        grades[grade]['total'] += 1
        
        quiz = str(data.get('quiz', ''))
        explain = str(data.get('explanation', ''))
        audio = data.get('audio', [])
        
        # 检查题目质量
        if len(quiz) > 500:  # 至少有3道题
            grades[grade]['has_quiz'] += 1
        elif len(quiz) > 50:  # 有题目但不完整
            grades[grade]['thin_quiz'] += 1
        else:
            grades[grade]['empty_quiz'] += 1
        
        # 检查讲解质量
        if len(explain) < 100:
            grades[grade]['thin_explain'] += 1
        
        # 检查音频
        if len(audio) > 0:
            grades[grade]['has_audio'] += 1
        else:
            grades[grade]['empty_audio'] += 1
    except:
        pass

print("=" * 80)
print("各年级内容质量统计")
print("=" * 80)
print(f"{'年级':<15} {'应有':>6} {'已有':>6} {'质量':>6} {'空题':>6} {'薄讲':>6} {'无音':>6}")
print("-" * 80)

total_expected = 0
total_actual = 0
total_has_quiz = 0
total_empty_quiz = 0
total_thin_explain = 0
total_empty_audio = 0

for grade in sorted(EXPECTED.keys()):
    exp = EXPECTED[grade]
    g = grades.get(grade, {'total': 0, 'has_quiz': 0, 'empty_quiz': 0, 'thin_explain': 0, 'empty_audio': 0})
    act = g['total']
    quality = g['has_quiz']  # 高质量数量
    gap = exp - act
    
    total_expected += exp
    total_actual += act
    total_has_quiz += g['has_quiz']
    total_empty_quiz += g['empty_quiz']
    total_thin_explain += g['thin_explain']
    total_empty_audio += g['empty_audio']
    
    print(f"{grade:<15} {exp:>6} {act:>6} {quality:>6} {g['empty_quiz']:>6} {g['thin_explain']:>6} {g['empty_audio']:>6}")

print("-" * 80)
print(f"{'合计':<15} {total_expected:>6} {total_actual:>6} {total_has_quiz:>6} {total_empty_quiz:>6} {total_thin_explain:>6} {total_empty_audio:>6}")
print("=" * 80)

print(f"\n核心问题:")
print(f"  覆盖率: {total_actual/total_expected*100:.1f}% (缺{total_expected-total_actual}个)")
print(f"  高质量(有完整题目): {total_has_quiz}个 ({total_has_quiz/total_actual*100:.1f}%)")
print(f"  零题目: {total_empty_quiz}个 ({total_empty_quiz/total_actual*100:.1f}%)")
print(f"  讲解过薄: {total_thin_explain}个 ({total_thin_explain/total_actual*100:.1f}%)")
print(f"  无音频: {total_empty_audio}个 ({total_empty_audio/total_actual*100:.1f}%)")
