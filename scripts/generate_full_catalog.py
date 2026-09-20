#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成完整的人教版3-15岁知识点目录"""

import json
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))

# 按年级-科目分组，按课排列
by_grade_subject = defaultdict(lambda: defaultdict(list))
for item in kg:
    grade = item.get('grade', '')
    subject = item.get('subject', '')
    topic = item.get('topic', '')
    chapter = item.get('chapter', '') or '基础'
    if topic:
        by_grade_subject[grade][subject].append({
            'topic': topic,
            'chapter': chapter,
            'has_content': bool(item.get('explanation')) and len(item.get('explanation', '')) >= 50
        })

# 生成目录
lines = ['# 人教版3-15岁知识点总目录（按课划分）\n\n']
lines.append('> 划分标准：一课一个知识点\n')
lines.append('> 数据来源：人民教育出版社教材目录\n')
lines.append('> 生成时间：2026-09-20\n\n')
lines.append('---\n\n')

# 年级顺序
grade_order = ['幼儿园', '幼小衔接', 
               '一年级上', '一年级下', 
               '二年级上', '二年级下',
               '三年级上', '三年级下',
               '四年级上', '四年级下',
               '五年级上', '五年级下',
               '六年级上', '六年级下',
               '七年级上', '七年级下',
               '八年级上', '八年级下',
               '九年级上', '九年级下']

total_count = 0
total_with_content = 0

for grade in grade_order:
    if grade not in by_grade_subject:
        continue
    
    lines.append(f'## {grade}\n\n')
    
    grade_total = 0
    grade_content = 0
    
    for subject in sorted(by_grade_subject[grade].keys()):
        topics = by_grade_subject[grade][subject]
        if not topics:
            continue
        
        grade_total += len(topics)
        grade_content += sum(1 for t in topics if t['has_content'])
        
        lines.append(f'### {subject}（{len(topics)}课）\n\n')
        
        # 按章节分组
        by_chapter = defaultdict(list)
        for t in topics:
            ch = t['chapter']
            by_chapter[ch].append(t)
        
        for ch in sorted(by_chapter.keys()):
            ch_topics = by_chapter[ch]
            lines.append(f'**{ch}**\n\n')
            
            for i, t in enumerate(ch_topics, 1):
                status = '✅' if t['has_content'] else '❌'
                lines.append(f'{i}. {t["topic"]} {status}')
                lines.append('')
        
        lines.append('\n')
    
    total_count += grade_total
    total_with_content += grade_content
    lines.append(f'**小计：{grade_total}课，其中{grade_content}课有内容**\n\n')
    lines.append('---\n\n')

# 汇总统计
lines.append('## 统计汇总\n\n')
lines.append('| 年级 | 知识点总数 | 有内容 | 缺失 | 完成率 |\n')
lines.append('|------|----------|--------|------|--------|\n')

for grade in grade_order:
    if grade in by_grade_subject:
        grade_total = sum(len(topics) for topics in by_grade_subject[grade].values())
        grade_content = sum(sum(1 for t in topics if t['has_content']) for topics in by_grade_subject[grade].values())
        missing = grade_total - grade_content
        rate = grade_content / grade_total * 100 if grade_total > 0 else 0
        lines.append(f'| {grade} | {grade_total} | {grade_content} | {missing} | {rate:.1f}% |\n')

lines.append(f'| **总计** | **{total_count}** | **{total_with_content}** | **{total_count - total_with_content}** | **{total_with_content/total_count*100:.1f}%** |\n')

# 写入文件
output_path = base / 'docs/人教版3-15岁知识点总目录.md'
output_path.write_text('\n'.join(lines), encoding='utf-8')

print(f"目录已生成: {output_path}")
print(f"总知识点数: {total_count}")
print(f"有内容: {total_with_content}")
print(f"缺失: {total_count - total_with_content}")
print(f"完成率: {total_with_content/total_count*100:.1f}%")
