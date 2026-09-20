#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理output目录：
1. 统一文件命名为 {grade}-{subject}-{topic}.json
2. 按年级和科目创建目录结构
3. 移动音频文件到对应科目文件夹
"""

import json
from pathlib import Path
from collections import defaultdict
import re
import shutil

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
backup_dir = base / 'backup_final'

# 创建备份（如果不存在）
if not backup_dir.exists():
    print(f"创建备份目录: {backup_dir}")
    backup_dir.mkdir(parents=True, exist_ok=True)

# 备份旧的output目录
old_output_backup = backup_dir / 'output_old'
if not old_output_backup.exists():
    print(f"备份旧output目录到: {old_output_backup}")
    shutil.copytree(output_dir, old_output_backup)

# 年级映射
GRADE_ALIASES = {
    '一上': '一年级上', '一下': '一年级下',
    '二上': '二年级上', '二下': '二年级下',
    '三上': '三年级上', '三下': '三年级下',
    '四上': '四年级上', '四下': '四年级下',
    '五上': '五年级上', '五下': '五年级下',
    '六上': '六年级上', '六下': '六年级下',
    '七上': '七年级上', '七下': '七年级下',
    '八上': '八年级上', '八下': '八年级下',
    '九上': '九年级上', '九下': '九年级下',
    '九全': '九年级全一册',
}

def normalize_subject(subject):
    if not subject:
        return ''
    subject = subject.lower().strip()
    
    if subject in ['语文', '数学', '英语', '物理', '化学', '生物', 
                   '地理', '历史', '科学', '道德与法治', '音乐', '美术', '体育']:
        return subject
    
    alias_map = {
        'yuwen': '语文', 'yuyin': '语文', 'chinese': '语文', 'ch': '语文',
        'shuxue': '数学', 'shu': '数学', 'math': '数学', 'm': '数学',
        'yingyu': '英语', 'ying': '英语', 'english': '英语', 'en': '英语',
        'wuli': '物理', 'wu': '物理', 'physics': '物理', 'ph': '物理',
        'huaxue': '化学', 'hua': '化学', 'chemistry': '化学', 'chm': '化学',
        'shengwu': '生物', 'sheng': '生物', 'biology': '生物', 'bio': '生物',
        'dili': '地理', 'di': '地理', 'geography': '地理', 'geo': '地理',
        'lishi': '历史', 'li': '历史', 'history': '历史', 'hist': '历史',
        'kexue': '科学', 'kx': '科学', 'science': '科学', 'sci': '科学',
        'daodeyuzhi': '道德与法治', 'daode': '道德与法治', 'morph': '道德与法治',
        'yinyue': '音乐', 'yy': '音乐', 'music': '音乐', 'mus': '音乐',
        'meishu': '美术', 'ms': '美术', 'art': '美术',
        'tiyu': '体育', 'ty': '体育', 'pe': '体育', 'sport': '体育',
        'health': '体育', '健康': '体育',
        'social': '道德与法治', '社会': '道德与法治',
        'language': '语文', '语言': '语文',
        'math_cognition': '数学认知', '数学认知': '数学认知',
        'science_inquiry': '科学探究', '科学探究': '科学探究',
    }
    
    for alias, standard in alias_map.items():
        if alias in subject or subject in alias:
            return standard
    
    return subject

def normalize_grade(grade):
    if not grade:
        return ''
    
    valid_grades = ['一年级上', '一年级下', '二年级上', '二年级下',
                    '三年级上', '三年级下', '四年级上', '四年级下',
                    '五年级上', '五年级下', '六年级上', '六年级下',
                    '七年级上', '七年级下', '八年级上', '八年级下',
                    '九年级上', '九年级下', '九年级全一册',
                    '幼儿园', '幼小衔接']
    
    if grade in valid_grades:
        return grade
    
    for alias, standard in GRADE_ALIASES.items():
        if alias in grade or grade in alias:
            return standard
    
    return grade

def sanitize_filename(name):
    """清理文件名中的非法字符"""
    # 移除或替换非法字符
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        name = name.replace(char, '-')
    # 限制长度
    if len(name) > 50:
        name = name[:50]
    return name.strip()

# 收集所有文件信息
all_files = []
empty_files = []

print("正在扫描output目录...")
for f in output_dir.rglob('*.json'):
    rel = f.relative_to(output_dir)
    parts = rel.parts
    
    filename = parts[-1].replace('.json', '')
    
    # 从路径获取年级
    grade_from_path = parts[0] if len(parts) > 0 else ''
    
    try:
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        
        topic = data.get('topic', '')
        explanation = data.get('explanation', '')
        subject = data.get('subject', '')
        
        final_grade = normalize_grade(grade_from_path)
        final_subject = normalize_subject(subject)
        
        if not topic or len(topic) < 2:
            topic = filename
        
        all_files.append({
            'old_path': f,
            'rel_path': str(rel),
            'grade': final_grade,
            'subject': final_subject,
            'topic': topic,
            'explanation': explanation,
            'data': data
        })
        
        if len(explanation) < 10:
            empty_files.append(f)
            
    except Exception as e:
        print(f"读取失败 {f}: {e}")

print(f"\n扫描完成: 共 {len(all_files)} 个文件")
print(f"空内容文件: {len(empty_files)} 个")

# 创建新的目录结构并移动文件
print("\n开始整理目录结构...")
moved = 0
failed = 0
duplicates = 0

# 用于跟踪已存在的文件名
existing_files = set()

for item in all_files:
    grade = item['grade']
    subject = item['subject']
    topic = sanitize_filename(item['topic'])
    
    # 生成新文件名
    new_filename = f"{grade}-{subject}-{topic}.json"
    
    # 创建目标目录
    target_dir = output_dir / grade / subject
    target_dir.mkdir(parents=True, exist_ok=True)
    
    target_path = target_dir / new_filename
    
    # 检查重复
    if target_path in existing_files:
        print(f"  重复文件: {item['old_path']} -> {target_path}")
        duplicates += 1
        continue
    
    existing_files.add(target_path)
    
    try:
        # 写入新文件
        with open(target_path, 'w', encoding='utf-8') as fp:
            json.dump(item['data'], fp, ensure_ascii=False, indent=2)
        moved += 1
    except Exception as e:
        print(f"  移动失败: {item['old_path']} -> {target_path}: {e}")
        failed += 1

print(f"\n移动完成: 成功 {moved} 个, 失败 {failed} 个, 重复 {duplicates} 个")

# 删除旧目录（先清空顶层文件，再删除空目录）
print("\n清理旧目录结构...")
deleted = 0
for f in output_dir.rglob('*.json'):
    # 只删除直接在年级目录下的文件（非子目录中的）
    rel = f.relative_to(output_dir)
    if len(rel.parts) == 2:  # 只有年级/文件名
        f.unlink()
        deleted += 1

print(f"删除旧文件: {deleted} 个")

# 删除空的子目录
for dirpath, dirnames, filenames in os.walk(output_dir, topdown=False):
    if not filenames and not any(dirpath.glob('*')):
        try:
            dirpath.rmdir()
        except:
            pass

print("\n整理完成!")
print(f"新目录结构已创建，请检查 {output_dir}")
