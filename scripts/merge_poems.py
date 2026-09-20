#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并古诗文内容并清理残留目录"""

import json
from pathlib import Path
from collections import defaultdict

BASE = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_PATH = BASE / 'knowledge_graph_complete.json'
OLD_POEM_DIR = BASE / 'output' / '语文' / '语文'

# 读取知识图谱
with open(KG_PATH, encoding='utf-8') as f:
    kg = json.load(f)

print(f"知识图谱初始条目数: {len(kg)}")

# 读取古诗文目录中的所有JSON文件
poem_contents = {}
for json_file in OLD_POEM_DIR.rglob('*.json'):
    topic_id = json_file.stem  # e.g., "语文古诗文0750"
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    poem_contents[topic_id] = data

print(f"古诗文目录文件数: {len(poem_contents)}")

# 合并内容到知识图谱
merged_count = 0
for item in kg:
    if item.get('grade') == '古诗文':
        topic_id = item['id']
        if topic_id in poem_contents:
            old_data = poem_contents[topic_id]
            # 合并内容（保留原有，补充缺失）
            for key in ['topic', 'explanation', 'description', 'example', 'key_points']:
                if key in old_data and (not item.get(key) or len(item.get(key, '')) < 10):
                    item[key] = old_data[key]
            merged_count += 1

print(f"合并后条目数: {len(kg)}")
print(f"成功合并古诗文: {merged_count}条")

# 检查合并结果
poem_filled = sum(1 for item in kg if item.get('grade') == '古诗文' and len(item.get('explanation', '')) > 100)
print(f"有内容的古诗文条目: {poem_filled}/{len([i for i in kg if i.get('grade') == '古诗文'])}")

# 保存知识图谱
with open(KG_PATH, 'w', encoding='utf-8') as f:
    json.dump(kg, f, ensure_ascii=False, indent=2)
print(f"知识图谱已保存")

# 删除残留目录
if OLD_POEM_DIR.exists():
    import shutil
    shutil.rmtree(OLD_POEM_DIR)
    print(f"已删除残留目录: {OLD_POEM_DIR}")

print("\n完成！")