#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整理输出目录结构：统一命名格式 (年级)-(科目)-(编号)"""

import json
from pathlib import Path
import shutil
import re

BASE = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_PATH = BASE / 'knowledge_graph_complete.json'
OUTPUT_DIR = BASE / 'output'

# 读取知识图谱
with open(KG_PATH, encoding='utf-8') as f:
    kg = json.load(f)

print(f"总条目数: {len(kg)}")

# 按新格式创建目录并移动文件
moved_count = 0
skipped_count = 0

for item in kg:
    grade = item.get('grade', '未知')
    subject = item.get('subject', '未知')
    old_id = item.get('id', '')
    
    # 从旧ID提取编号
    match = re.search(r'(\d{3,})$', old_id)
    if not match:
        skipped_count += 1
        continue
    num = match.group(1)
    
    # 新文件名
    new_name = f"{grade}-{subject}-{num}"
    
    # 新路径
    new_dir = OUTPUT_DIR / grade / subject / new_name
    new_json = new_dir / f"{new_name}.json"
    
    # 查找旧文件
    # 可能的位置：旧格式目录或新格式目录
    old_json = None
    
    # 尝试多种可能的旧路径
    candidates = [
        OUTPUT_DIR / old_id[:3] / old_id[:6] / old_id / f"{old_id}.json",
        OUTPUT_DIR / old_id / f"{old_id}.json",
    ]
    # 添加rglob结果作为列表
    glob_results = list(OUTPUT_DIR.rglob(f"{old_id}.json"))
    candidates.extend(glob_results)
    
    for search_path in candidates:
        if search_path.exists():
            old_json = search_path
            break
    
    if not old_json:
        # 可能是古诗文目录
        old_json = OUTPUT_DIR / '语文' / '语文' / old_id / f"{old_id}.json"
        if not old_json.exists():
            skipped_count += 1
            continue
    
    # 创建新目录并移动
    new_dir.mkdir(parents=True, exist_ok=True)
    
    # 移动JSON
    shutil.move(str(old_json), str(new_json))
    moved_count += 1
    
    # 如果有audio目录，也移动
    old_audio = old_json.parent.parent / 'audio'
    new_audio = new_dir / 'audio'
    if old_audio.exists() and not new_audio.exists():
        shutil.move(str(old_audio), str(new_audio))

print(f"成功移动: {moved_count} 个文件")
print(f"跳过: {skipped_count} 个")

# 清理空目录
for root, dirs, files in OUTPUT_DIR.walk():
    for d in dirs:
        dir_path = root / d
        if not any(dir_path.iterdir()):
            dir_path.rmdir()

# 删除空余的根目录
for subdir in ['语文', '物理九年级全一册']:
    target = OUTPUT_DIR / subdir
    if target.exists() and not any(target.iterdir()):
        target.rmdir()

print("目录整理完成")