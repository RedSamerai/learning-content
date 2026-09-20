#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量重命名文件：统一为 {grade}-{subject}-{topic}.json 格式
"""

import json
from pathlib import Path
import shutil
import re

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'

renamed_json = 0
renamed_mp3 = 0
errors = 0
duplicates = 0

print("=" * 60)
print("开始批量重命名文件...")
print("=" * 60)

# 处理JSON文件
print("\n【处理JSON文件】")
for f in list(output_dir.rglob('*.json')):
    rel = str(f.relative_to(output_dir)).replace('\\', '/')
    parts = rel.split('/')
    
    if len(parts) < 3:
        continue
    
    grade = parts[0]
    subject = parts[1]
    old_filename = parts[-1].replace('.json', '')
    
    # 已符合格式的跳过
    if old_filename.startswith(grade + '-') and '-' in old_filename[len(grade)+1:]:
        continue
    
    try:
        with open(f, encoding='utf-8') as fp:
            data = json.load(fp)
        
        topic = data.get('topic', '')
        
        # 如果没有topic，从filename提取
        if not topic or len(topic) < 2:
            # 清理filename中的年级前缀
            temp = old_filename
            for p in ['一年级上', '一年级下', '二年级上', '二年级下', 
                     '三年级上', '三年级下', '四年级上', '四年级下',
                     '五年级上', '五年级下', '六年级上', '六年级下',
                     '七年级上', '七年级下', '八年级上', '八年级下',
                     '九年级上', '九年级下', '九年级全一册',
                     '幼儿园', '幼小衔接']:
                temp = temp.replace(p, '')
            # 移除数字和特殊字符
            temp = re.sub(r'\d+', '', temp)
            temp = temp.replace('_', ' ').replace('-', ' ').strip()
            if len(temp) > 2:
                topic = temp[:30]
            else:
                num_match = re.search(r'\d+', old_filename)
                topic = f"第{num_match.group()}课" if num_match else f"{subject}知识"
        
        # 确保topic不超过30字符
        if len(topic) > 30:
            topic = topic[:30] + '...'
        
        new_filename = f"{grade}-{subject}-{topic}"
        # 清理非法字符
        for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            new_filename = new_filename.replace(char, '-')
        
        new_path = f.parent / (new_filename + '.json')
        
        # 如果目标已存在
        if new_path.exists() and new_path != f:
            # 检查内容是否相同
            with open(new_path, encoding='utf-8') as fp1:
                data1 = json.load(fp1)
            content1 = data1.get('explanation', '') or data1.get('content', '')
            content2 = data.get('explanation', '') or data.get('content', '')
            
            if content1 == content2:
                # 内容相同，删除重复文件
                f.unlink()
                renamed_json += 1
            elif len(content2) > len(content1):
                # 保留内容更丰富的
                new_path.unlink()
                f.rename(new_path)
                renamed_json += 1
            else:
                f.unlink()
                renamed_json += 1
                duplicates += 1
        else:
            f.rename(new_path)
            renamed_json += 1
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"  错误: {old_filename} - {e}")

print(f"  JSON文件重命名: {renamed_json} 个")

# 处理MP3文件
print("\n【处理MP3文件】")
for mp3 in list(output_dir.rglob('*.mp3')):
    rel = str(mp3.relative_to(output_dir)).replace('\\', '/')
    parts = rel.split('/')
    
    if len(parts) < 3:
        continue
    
    grade = parts[0]
    subject = parts[1]
    old_name = parts[-1].replace('.mp3', '')
    
    # 已符合格式的跳过
    if old_name.startswith(grade + '-'):
        continue
    
    try:
        # MP3文件名格式：{grade}-{subject}-XXX.mp3
        # 尝试从旧文件名提取有意义部分
        if old_name == 'audio':
            # audio.mp3，需要找到对应的JSON文件
            json_parent = mp3.parent.parent
            json_files = list(json_parent.glob('*.json'))
            if json_files:
                # 使用第一个JSON文件的topic作为参考
                with open(json_files[0], encoding='utf-8') as fp:
                    data = json.load(fp)
                topic = data.get('topic', 'audio')
                new_name = f"{grade}-{subject}-{topic}"
            else:
                new_name = f"{grade}-{subject}-audio"
        else:
            # 清理filename
            temp = old_name
            for p in ['一年级上', '一年级下', '二年级上', '二年级下', 
                     '三年级上', '三年级下', '四年级上', '四年级下',
                     '五年级上', '五年级下', '六年级上', '六年级下',
                     '七年级上', '七年级下', '八年级上', '八年级下',
                     '九年级上', '九年级下', '九年级全一册',
                     '幼儿园', '幼小衔接']:
                temp = temp.replace(p, '')
            temp = re.sub(r'\d+', '', temp)
            temp = temp.replace('_', ' ').replace('-', ' ').strip()
            if len(temp) > 2:
                topic = temp[:30]
            else:
                num_match = re.search(r'\d+', old_name)
                topic = f"第{num_match.group()}课" if num_match else 'audio'
            
            new_name = f"{grade}-{subject}-{topic}"
        
        # 清理非法字符
        for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            new_name = new_name.replace(char, '-')
        
        new_path = mp3.parent / (new_name + '.mp3')
        
        if new_path.exists() and new_path != mp3:
            mp3.unlink()
        else:
            mp3.rename(new_path)
        renamed_mp3 += 1
        
    except Exception as e:
        errors += 1

print(f"  MP3文件重命名: {renamed_mp3} 个")

# 最终统计
print("\n" + "=" * 60)
print("最终统计:")
print("=" * 60)

total_json = sum(1 for _ in output_dir.rglob('*.json'))
total_mp3 = sum(1 for _ in output_dir.rglob('*.mp3'))

good_json = 0
for f in output_dir.rglob('*.json'):
    rel = str(f.relative_to(output_dir)).replace('\\', '/')
    parts = rel.split('/')
    if len(parts) >= 3:
        filename = parts[-1].replace('.json', '')
        grade = parts[0]
        if filename.startswith(grade + '-') and '-' in filename[len(grade)+1:]:
            good_json += 1

print(f"  JSON文件总数: {total_json} 个")
print(f"  符合格式: {good_json} 个")
print(f"  不符合格式: {total_json - good_json} 个")
print(f"  MP3文件总数: {total_mp3} 个")
print(f"  重命名成功: JSON {renamed_json} 个, MP3 {renamed_mp3} 个")
print(f"  错误数: {errors} 个")
print(f"  重复文件: {duplicates} 个")
