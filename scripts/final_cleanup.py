#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理output目录：
1. 合并"物理九年级全一册XXXX"到"九年级全一册/物理/"
2. 统一英文科目名为中文
3. 删除空audio目录（音频已在各科目录内）
"""

import json
from pathlib import Path
import shutil
import os

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'

# 英文科目映射
EN_TO_ZH = {
    'art': '美术', 'health': '体育', 'language': '语文',
    'science': '科学', 'social': '道德与法治',
    'chinese': '语文', 'math': '数学', 'english': '英语',
    'physics': '物理', 'chemistry': '化学', 'biology': '生物',
    'geography': '地理', 'history': '历史', 'music': '音乐', 'pe': '体育',
    'math_cognition': '数学认知', 'science_inquiry': '科学探究',
    'moral': '道德与法治', 'morality': '道德与法治',
    '艺术': '美术', '健康': '体育', '语言': '语文'
}

# 物理九年级全一册的文件应该移到 九年级全一册/物理/
FULL_YEAR_PHYSICS_PATTERN = '物理九年级全一册'
FULL_YEAR_ENGLISH_PATTERN = '英语九年级全一册'

moved = 0
deleted = 0
renamed = 0

print("开始清理...")

# 第一遍：处理"物理九年级全一册XXXX"和"英语九年级全一册XXXX"这类子目录
for grade_dir in output_dir.iterdir():
    if not grade_dir.is_dir():
        continue
    
    for subj_dir in grade_dir.iterdir():
        if not subj_dir.is_dir():
            continue
        
        subj_name = subj_dir.name
        
        # 检查是否是"物理九年级全一册XXXX"或"英语九年级全一册XXXX"
        for f in list(subj_dir.rglob('*.json')):
            rel = f.relative_to(output_dir)
            parts = rel.parts
            
            if len(parts) >= 4 and parts[2].startswith(('物理九年级全一册', '英语九年级全一册')):
                # 提取真实年级
                subdir_name = parts[2]
                new_grade = '九年级全一册'  # 所有"九年级全一册XXXX"都归到九年级全一册
                
                # 确定科目
                if '物理' in subdir_name:
                    new_subject = '物理'
                elif '英语' in subdir_name:
                    new_subject = '英语'
                else:
                    new_subject = subj_name
                
                target_dir = output_dir / new_grade / new_subject
                target_dir.mkdir(parents=True, exist_ok=True)
                new_path = target_dir / f.name
                
                if not new_path.exists():
                    shutil.move(str(f), str(new_path))
                    moved += 1
                else:
                    f.unlink()
                    deleted += 1

print(f"第一遍清理: 移动 {moved} 个，删除 {deleted} 个")

# 第二遍：统一英文科目名
for grade_dir in output_dir.iterdir():
    if not grade_dir.is_dir():
        continue
    
    for subj_dir in list(grade_dir.iterdir()):
        if not subj_dir.is_dir():
            continue
        
        subj_name = subj_dir.name
        if subj_name in EN_TO_ZH:
            zh_name = EN_TO_ZH[subj_name]
            target_dir = grade_dir / zh_name
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 移动所有文件
            for f in subj_dir.rglob('*'):
                if f.is_file():
                    new_path = target_dir / f.name
                    if not new_path.exists():
                        shutil.move(str(f), str(new_path))
            
            # 删除空目录
            if not any(subj_dir.iterdir()):
                subj_dir.rmdir()
            
            renamed += 1

print(f"第二遍清理: 重命名 {renamed} 个科目目录")

# 第三遍：删除空的audio目录（音频已在各科目录内）
audio_count = 0
for grade_dir in output_dir.iterdir():
    if not grade_dir.is_dir():
        continue
    audio_dir = grade_dir / 'audio'
    if audio_dir.is_dir() and not any(audio_dir.iterdir()):
        audio_dir.rmdir()
        audio_count += 1

print(f"第三遍清理: 删除 {audio_count} 个空audio目录")

# 第四遍：删除残留的空目录
for dirpath, dirnames, filenames in os.walk(output_dir, topdown=False):
    if not filenames and not any(Path(dirpath).iterdir()):
        try:
            os.rmdir(dirpath)
        except:
            pass

# 最终统计
total_json = sum(1 for _ in output_dir.rglob('*.json'))
total_mp3 = sum(1 for _ in output_dir.rglob('*.mp3'))
print(f"\n最终统计:")
print(f"  JSON文件: {total_json}个")
print(f"  MP3文件: {total_mp3}个")

# 显示目录结构
print("\n目录结构:")
for grade_dir in sorted(output_dir.iterdir()):
    if grade_dir.is_dir():
        subjects = [d.name for d in grade_dir.iterdir() if d.is_dir()]
        json_count = sum(1 for _ in grade_dir.rglob('*.json'))
        mp3_count = sum(1 for _ in grade_dir.rglob('*.mp3'))
        print(f"  {grade_dir.name}/ ({json_count} JSON, {mp3_count} MP3): {', '.join(sorted(set(subjects)))}")

print("\n清理完成!")
