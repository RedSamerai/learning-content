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
    """标准化科目名称"""
    if not subject:
        return ''
    subject = subject.lower().strip()
    
    # 直接匹配
    if subject in ['语文', '数学', '英语', '物理', '化学', '生物', 
                   '地理', '历史', '科学', '道德与法治', '音乐', '美术', '体育']:
        return subject
    
    # 别名匹配
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
        'meishu': '美术', 'ms': '美术', 'art': '美术', 'art': '美术',
        'tiyu': '体育', 'ty': '体育', 'pe': '体育', 'sport': '体育',
        'health': '体育', '健康': '体育',
        'social': '道德与法治', '社会': '道德与法治',
        'language': '语文', '语言': '语文',
        'math_cognition': '数学认知', '数学认知': '数学认知',
        'science_inquiry': '科学探究', '科学探究': '科学探究',
        'art': '美术',
    }
    
    for alias, standard in alias_map.items():
        if alias in subject or subject in alias:
            return standard
    
    return subject

def normalize_grade(grade):
    """标准化年级名称"""
    if not grade:
        return ''
    
    # 直接匹配
    valid_grades = ['一年级上', '一年级下', '二年级上', '二年级下',
                    '三年级上', '三年级下', '四年级上', '四年级下',
                    '五年级上', '五年级下', '六年级上', '六年级下',
                    '七年级上', '七年级下', '八年级上', '八年级下',
                    '九年级上', '九年级下', '九年级全一册',
                    '幼儿园', '幼小衔接']
    
    if grade in valid_grades:
        return grade
    
    # 别名匹配
    for alias, standard in GRADE_ALIASES.items():
        if alias in grade or grade in alias:
            return standard
    
    return grade

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
        
        # 从文件内容获取关键信息
        topic = data.get('topic', '')
        explanation = data.get('explanation', '')
        subject = data.get('subject', '')
        
        # 标准化
        final_grade = normalize_grade(grade_from_path)
        final_subject = normalize_subject(subject)
        
        # 确保知识点不为空
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

# 显示样例
print("\n样例文件信息:")
for item in all_files[:15]:
    print(f"  旧路径: {item['rel_path'][:60]}")
    print(f"    年级: {item['grade']}, 科目: {item['subject']}, 知识点: {item['topic'][:30]}")
    print(f"    解释长度: {len(item['explanation'])}")
    print()

# 统计年级分布
grade_dist = defaultdict(int)
for item in all_files:
    grade_dist[item['grade']] += 1

print("\n按年级统计:")
for g in sorted(grade_dist.keys()):
    print(f"  {g}: {grade_dist[g]}个")

# 统计科目分布
subject_dist = defaultdict(int)
for item in all_files:
    subject_dist[item['subject']] += 1

print("\n按科目统计:")
for s, cnt in sorted(subject_dist.items(), key=lambda x: -x[1])[:15]:
    print(f"  {s}: {cnt}个")
