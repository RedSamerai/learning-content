#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并二年级音乐、美术、体育、道德与法治到知识图谱"""

import json
from pathlib import Path

BASE = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_PATH = BASE / 'knowledge_graph_complete.json'

def merge_temp(temp_file, subject, grade):
    """合并临时文件到知识图谱"""
    data = json.load(open(temp_file, encoding='utf-8'))
    kg = json.load(open(KG_PATH, encoding='utf-8'))
    
    existing_ids = {item['id'] for item in kg}
    new_count = 0
    
    for item in data:
        topic_id = item['id']
        if topic_id not in existing_ids:
            item['subject'] = subject
            item['grade'] = grade
            kg.append(item)
            existing_ids.add(topic_id)
            new_count += 1
    
    with open(KG_PATH, 'w', encoding='utf-8') as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)
    
    return new_count, len(data)

# 合并二年级科目
subjects = [
    ('yinyue', '音乐', '二年级下'),
    ('meishu', '美术', '二年级下'),
    ('tiyu', '体育', '二年级下'),
    ('daode', '道德与法治', '二年级下')
]

total_new = 0
total_files = 0

for suffix, subject, grade in subjects:
    temp_file = BASE / 'scripts' / f'temp_{suffix}_2x.json'
    if temp_file.exists():
        count, total = merge_temp(temp_file, subject, grade)
        print(f'{subject}二年级下: 新增 {count}/{total} 个')
        total_new += count
        total_files += total

# 也合并二年级上的科目（如果存在）
for suffix, subject, grade in [('yinyue', '音乐', '二年级上'), ('meishu', '美术', '二年级上'), 
                                 ('tiyu', '体育', '二年级上'), ('daode', '道德与法治', '二年级上')]:
    temp_file = BASE / 'scripts' / f'temp_{suffix}_2s.json'
    if temp_file.exists():
        count, total = merge_temp(temp_file, subject, grade)
        print(f'{subject}二年级上: 新增 {count}/{total} 个')
        total_new += count
        total_files += total

print(f'\n本次新增: {total_new} 个知识点')

# 验证结果
kg = json.load(open(KG_PATH, encoding='utf-8'))
print(f'知识图谱总数: {len(kg)} 个')

# 统计各年级科目
from collections import defaultdict
grade_subjects = defaultdict(lambda: defaultdict(int))
for item in kg:
    grade_subjects[item.get('grade', '未知')][item.get('subject', '未知')] += 1

print('\n=== 二年级科目分布 ===')
for grade in ['二年级上', '二年级下']:
    if grade in grade_subjects:
        subjects_str = ', '.join([f'{s}:{c}' for s, c in sorted(grade_subjects[grade].items())])
        print(f'{grade}: {subjects_str}')