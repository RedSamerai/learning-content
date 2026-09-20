#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统一文件命名格式: (年级)-(科目)-(编号)"""

import json
from pathlib import Path
import shutil
from collections import defaultdict

BASE = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_PATH = BASE / 'knowledge_graph_complete.json'
OUTPUT_DIR = BASE / 'output'

# 读取知识图谱
with open(KG_PATH, encoding='utf-8') as f:
    kg = json.load(f)

print(f"总条目数: {len(kg)}")

# 统计各年级科目分布
grade_subjects = defaultdict(lambda: defaultdict(int))
for item in kg:
    grade = item.get('grade', '未知')
    subject = item.get('subject', '未知')
    grade_subjects[grade][subject] += 1

print("\n各年级科目分布:")
for grade in sorted(grade_subjects.keys()):
    subjects = grade_subjects[grade]
    print(f"  {grade}: {dict(subjects)}")

# 为每个条目生成新路径
rename_map = {}  # 旧路径 -> 新路径
for item in kg:
    old_id = item.get('id', '')
    grade = item.get('grade', '未知')
    subject = item.get('subject', '未知')
    
    # 提取编号
    # 旧格式: 语文一年级上0085, 语言幼儿园0001
    import re
    match = re.search(r'(\d{3,})$', old_id)
    if match:
        num = match.group(1)
    else:
        num = old_id[-3:] if len(old_id) >= 3 else old_id
    
    # 新格式: 年级-科目-编号
    new_name = f"{grade}-{subject}-{num}"
    new_path = OUTPUT_DIR / grade / subject / new_name / f"{new_name}.json"
    
    # 旧路径
    old_path = OUTPUT_DIR / old_id[:3] / old_id[:6] / f"{old_id}/{old_id}.json"
    # 尝试找到实际旧路径
    for p in OUTPUT_DIR.rglob(f"{old_id}.json"):
        old_path = p
        break
    
    if old_path.exists():
        rename_map[str(old_path)] = str(new_path)

print(f"\n需要重命名的文件数: {len(rename_map)}")

# 执行重命名
success_count = 0
for old_path, new_path in rename_map.items():
    try:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(old_path, new_path)
        success_count += 1
    except Exception as e:
        print(f"错误: {old_path} -> {new_path}: {e}")

print(f"成功重命名: {success_count}个文件")

# 更新知识图谱中的ID
for item in kg:
    old_id = item.get('id', '')
    grade = item.get('grade', '未知')
    subject = item.get('subject', '未知')
    import re
    match = re.search(r'(\d{3,})$', old_id)
    if match:
        num = match.group(1)
    else:
        num = old_id[-3:] if len(old_id) >= 3 else old_id
    new_id = f"{grade}-{subject}-{num}"
    item['id'] = new_id

# 保存更新后的知识图谱
with open(KG_PATH, 'w', encoding='utf-8') as f:
    json.dump(kg, f, ensure_ascii=False, indent=2)
print("知识图谱ID已更新")

print("\n完成！")