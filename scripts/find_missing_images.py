#!/usr/bin/env python3
"""找出缺失图片的知识点"""
from pathlib import Path
import json

missing_img = []
for p in Path('output').rglob('*.json'):
    if p.parent.name in ['image', 'audio']:
        continue
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        img_file = data.get('image', '')
        img_path = p.parent / img_file
        if not img_path.exists() or img_path.stat().st_size == 0:
            grade = data.get('grade', data.get('age_group', '未知'))
            missing_img.append((p.parent.name, data.get('name', '未知'), grade, img_file))
    except:
        pass

print(f"缺失图片的知识点: {len(missing_img)}个\n")
for topic, name, grade, img in missing_img:
    print(f"  {topic}/{name} ({grade}) - 图片: {img}")