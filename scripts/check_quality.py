#!/usr/bin/env python3
"""全面检查各年级内容质量"""
import json
from pathlib import Path

grades = {}
for p in Path('output').rglob('*.json'):
    if p.parent.name in ['image', 'audio']:
        continue
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        grade = data.get('grade', data.get('age_group', '未知'))
        if grade not in grades:
            grades[grade] = {'total': 0, 'has_quiz': 0, 'empty_quiz': 0, 'has_audio': 0, 'empty_audio': 0}
        grades[grade]['total'] += 1
        
        quiz = str(data.get('quiz', ''))
        audio = data.get('audio', [])
        
        if len(quiz) > 50:
            grades[grade]['has_quiz'] += 1
        else:
            grades[grade]['empty_quiz'] += 1
        
        if len(audio) > 0:
            grades[grade]['has_audio'] += 1
        else:
            grades[grade]['empty_audio'] += 1
    except:
        pass

print('=' * 70)
print('各年级内容质量统计')
print('=' * 70)
for grade in sorted(grades.keys()):
    g = grades[grade]
    total = g['total']
    quiz_rate = g['has_quiz'] / total * 100 if total > 0 else 0
    audio_rate = g['has_audio'] / total * 100 if total > 0 else 0
    print(f"\n【{grade}】共 {total} 个知识点")
    print(f"  有练习题: {g['has_quiz']}个 ({quiz_rate:.0f}%) | 无题/空题: {g['empty_quiz']}个")
    print(f"  有音频:   {g['has_audio']}个 ({audio_rate:.0f}%) | 无音频: {g['empty_audio']}个")

print('\n' + '=' * 70)
print('问题总结')
print('=' * 70)
total_empty_quiz = sum(g['empty_quiz'] for g in grades.values())
total_empty_audio = sum(g['empty_audio'] for g in grades.values())
total_topics = sum(g['total'] for g in grades.values())
print(f"\n总知识点: {total_topics}个")
print(f"零练习题: {total_empty_quiz}个 ({total_empty_quiz/total_topics*100:.1f}%)")
print(f"零音频:   {total_empty_audio}个 ({total_empty_audio/total_topics*100:.1f}%)")