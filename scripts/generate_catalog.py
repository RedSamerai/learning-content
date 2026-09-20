#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成知识点总目录"""

import json
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))

# 统计
stats = {}
for item in kg:
    grade = item.get('grade', '未知')
    subject = item.get('subject', '未知')
    topic = item.get('topic', '未知')
    
    has_file = (output_dir / grade / subject / f'{grade}-{subject}-{topic.replace("/", "-")}.json').exists()
    
    if grade not in stats:
        stats[grade] = {'total': 0, 'files': 0, 'subjects': {}}
    stats[grade]['total'] += 1
    if has_file:
        stats[grade]['files'] += 1
    if subject not in stats[grade]['subjects']:
        stats[grade]['subjects'][subject] = {'total': 0, 'files': 0}
    stats[grade]['subjects'][subject]['total'] += 1
    if has_file:
        stats[grade]['subjects'][subject]['files'] += 1

# 生成目录
lines = ['# 学习APP知识点总目录\n\n']
lines.append(f'**生成时间**：2026-09-20\n\n')
lines.append(f'**知识点总数**：{sum(s["total"] for s in stats.values())}个\n\n')
lines.append(f'**文件总数**：{sum(s["files"] for s in stats.values())}个\n\n')
lines.append(f'**完成率**：{sum(s["files"] for s in stats.values()) / sum(s["total"] for s in stats.values()) * 100:.1f}%\n\n')

lines.append('---\n\n')

# 按年级分组
grade_order = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', 
               '三年级上', '三年级下', '四年级上', '四年级下', '五年级上', '五年级下',
               '六年级上', '六年级下', '七年级上', '七年级下', '八年级上', '八年级下',
               '九年级上', '九年级下', '古诗文', '九年级全一册']

for grade in grade_order:
    if grade not in stats:
        continue
    s = stats[grade]
    lines.append(f'## {grade}\n\n')
    lines.append(f'**总计**：{s["total"]}个知识点，{s["files"]}个文件\n\n')
    lines.append('| 科目 | 知识点 | 文件 | 状态 |\n|------|--------|------|------|')
    for subject, sub_stats in sorted(s['subjects'].items()):
        missing = sub_stats['total'] - sub_stats['files']
        status = "✅" if missing == 0 else f"❌缺{missing}"
        lines.append(f'| {subject} | {sub_stats["total"]} | {sub_stats["files"]} | {status} |\n')
    lines.append('\n---\n\n')

# 写入
output_path = base / 'knowledge_catalog.md'
output_path.write_text('\n'.join(lines), encoding='utf-8')

print(f"目录已生成: {output_path}")
print(f"总计: {sum(s['total'] for s in stats.values())}个知识点")