#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并音乐、美术、体育、道德与法治到知识图谱"""

import json
from pathlib import Path

BASE = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_PATH = BASE / 'knowledge_graph_complete.json'
OUTPUT_DIR = BASE / 'output'

def merge_temp(temp_file, subject, grade_prefix):
    """合并临时文件到知识图谱"""
    data = json.load(open(temp_file, encoding='utf-8'))
    
    # 读取现有知识图谱
    kg = json.load(open(KG_PATH, encoding='utf-8'))
    
    # 创建现有ID集合
    existing_ids = {item['id'] for item in kg}
    
    # 合并新数据
    new_count = 0
    for item in data:
        topic_id = item['id']
        if topic_id not in existing_ids:
            # 添加subject和grade
            item['subject'] = subject
            # 从topic提取年级信息（如 yinyue_1s_001 -> 一年级上）
            if '1s' in topic_id:
                item['grade'] = '一年级上'
            elif '1x' in topic_id:
                item['grade'] = '一年级下'
            elif '2s' in topic_id:
                item['grade'] = '二年级上'
            elif '2x' in topic_id:
                item['grade'] = '二年级下'
            else:
                item['grade'] = '未知'
            
            kg.append(item)
            existing_ids.add(topic_id)
            new_count += 1
    
    # 保存更新后的知识图谱
    with open(KG_PATH, 'w', encoding='utf-8') as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)
    
    return new_count, len(data)

# 合并各科目
subjects = [
    ('yinyue', '音乐'),
    ('meishu', '美术'), 
    ('tiyu', '体育'),
    ('daode', '道德与法治')
]

total_new = 0
total_files = 0

for suffix, subject in subjects:
    temp_1s = BASE / 'scripts' / f'temp_{suffix}_1s.json'
    temp_1x = BASE / 'scripts' / f'temp_{suffix}_1x.json'
    
    count_1s = 0
    count_1x = 0
    
    if temp_1s.exists():
        count_1s, total = merge_temp(temp_1s, subject, '1s')
        print(f'{subject}一年级上: 新增 {count_1s}/{total} 个')
        total_new += count_1s
        total_files += total
    
    if temp_1x.exists():
        count_1x, total = merge_temp(temp_1x, subject, '1x')
        print(f'{subject}一年级下: 新增 {count_1x}/{total} 个')
        total_new += count_1x
        total_files += total

print(f'\n总计: 新增 {total_new} 个知识点，共处理 {total_files} 个')

# 验证结果
kg = json.load(open(KG_PATH, encoding='utf-8'))
print(f'知识图谱总数: {len(kg)} 个')