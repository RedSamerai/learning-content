#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从知识图谱生成按课划分的完整目录
"""

import json
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))

# 按年级和科目分组
by_grade_subject = defaultdict(lambda: defaultdict(list))

for item in kg:
    grade = item.get('grade', '未知')
    subject = item.get('subject', '未知')
    topic = item.get('topic', '')
    chapter = item.get('chapter', '')
    if topic:
        by_grade_subject[grade][subject].append({
            'topic': topic,
            'chapter': chapter,
            'explanation': item.get('explanation', '')[:50] if item.get('explanation') else ''
        })

# 生成目录
lines = ['# 人教版3-15岁知识点目录（按课划分）\n\n']
lines.append('> 划分标准：一课一个知识点\n')
lines.append('> 生成时间：2026-09-20\n\n')

# 年级顺序
grade_order = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下',
               '三年级上', '三年级下', '四年级上', '四年级下', '五年级上', '五年级下',
               '六年级上', '六年级下', '七年级上', '七年级下', '八年级上', '八年级下',
               '九年级上', '九年级下', '古诗文']

total_count = 0
total_with_content = 0

for grade in grade_order:
    if grade not in by_grade_subject:
        continue
    
    lines.append(f'## {grade}\n\n')
    
    grade_total = 0
    for subject in sorted(by_grade_subject[grade].keys()):
        topics = by_grade_subject[grade][subject]
        if not topics:
            continue
        
        grade_total += len(topics)
        lines.append(f'### {subject}（{len(topics)}课）\n\n')
        
        # 按章节分组显示
        by_chapter = defaultdict(list)
        for t in topics:
            ch = t.get('chapter', '未分类') or '未分类'
            by_chapter[ch].append(t)
        
        for ch in sorted(by_chapter.keys()):
            ch_topics = by_chapter[ch]
            lines.append(f'**{ch}**\n\n')
            for i, t in enumerate(ch_topics, 1):
                lines.append(f'{i}. {t["topic"]}')
                if t.get('explanation'):
                    lines.append(f'   - {t["explanation"][:30]}...')
                lines.append('')
        
        lines.append('\n')
    
    total_count += grade_total
    lines.append(f'**小计：{grade_total}课**\n\n')
    lines.append('---\n\n')

# 统计汇总
lines.append('## 统计汇总\n\n')
lines.append(f'| 年级 | 知识点数量 |\n|------|----------|\n')

for grade in grade_order:
    if grade in by_grade_subject:
        count = sum(len(topics) for topics in by_grade_subject[grade].values())
        lines.append(f'| {grade} | {count} |\n')

lines.append(f'| **总计** | **{total_count}** |\n')

# 写入文件
output_path = base / 'knowledge_catalog_lesson_based.md'
output_path.write_text('\n'.join(lines), encoding='utf-8')

print(f"目录已生成: {output_path}")
print(f"总知识点数: {total_count}")

# 检查内容完整性
for grade in ['一年级上', '一年级下']:
    for subject in ['语文', '数学']:
        if grade in by_grade_subject and subject in by_grade_subject[grade]:
            topics = by_grade_subject[grade][subject]
            with_content = sum(1 for t in topics if t.get('explanation'))
            print(f"{grade}-{subject}: {len(topics)}课, {with_content}课有内容")
