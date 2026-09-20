#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理异常嵌套目录，处理重复文件
"""

import json
from pathlib import Path
import shutil
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'

print("正在清理异常目录...")

# 找出所有嵌套超过2层的目录
problem_dirs = []
for f in output_dir.rglob('*.json'):
    rel = f.relative_to(output_dir)
    parts = rel.parts
    if len(parts) > 3:  # output/grade/subject/filename.json 应该是3层
        problem_dirs.append(f)

print(f"发现 {len(problem_dirs)} 个异常嵌套文件")

# 收集重复文件名
file_map = defaultdict(list)
for f in output_dir.rglob('*.json'):
    file_map[f.name].append(f)

duplicates = {k: v for k, v in file_map.items() if len(v) > 1}
print(f"发现 {len(duplicates)} 个重复文件名")

# 处理重复文件：保留内容更丰富的版本
kept_files = set()
deleted_count = 0

for filename, files in duplicates.items():
    if len(files) == 1:
        continue
    
    # 读取所有文件内容，选择内容最丰富的
    best_file = None
    best_content_len = 0
    
    for f in files:
        try:
            with open(f, encoding='utf-8') as fp:
                data = json.load(fp)
            content_len = len(data.get('explanation', '') or data.get('content', ''))
            if content_len > best_content_len:
                best_content_len = content_len
                best_file = f
        except:
            pass
    
    if best_file:
        kept_files.add(best_file)
        # 删除其他重复文件
        for f in files:
            if f != best_file:
                f.unlink()
                deleted_count += 1
                print(f"  删除重复: {f.relative_to(output_dir)}")

print(f"\n删除了 {deleted_count} 个重复文件")

# 清理异常嵌套目录
moved_count = 0
for f in problem_dirs:
    rel = f.relative_to(output_dir)
    parts = rel.parts
    
    if len(parts) > 3:
        # 尝试提取年级和科目
        grade = parts[0]
        subject = parts[1] if parts[1] in ['语文', '数学', '英语', '物理', '化学', '生物', 
                                             '地理', '历史', '科学', '道德与法治', '音乐', '美术', '体育',
                                             'language', 'math', 'english', 'physics', 'chemistry', 'biology',
                                             'geography', 'history', 'science', 'art', 'music', 'pe', 'health'] else ''
        
        if not subject:
            # 尝试从文件名提取科目
            filename = parts[-1].replace('.json', '')
            if '语文' in filename:
                subject = '语文'
            elif '数学' in filename or 'shu' in filename.lower():
                subject = '数学'
            elif '英语' in filename or 'ying' in filename.lower() or 'en' in filename.lower():
                subject = '英语'
        
        if subject:
            # 移动到正确位置
            new_path = output_dir / grade / subject / filename
            if not new_path.exists():
                shutil.move(str(f), str(new_path))
                moved_count += 1
            else:
                # 如果目标已存在，删除源文件
                f.unlink()
                deleted_count += 1
        else:
            # 无法确定科目，删除文件
            f.unlink()
            deleted_count += 1

print(f"移动了 {moved_count} 个文件到正确位置")
print(f"删除了 {deleted_count} 个无效文件")

# 删除空目录
import os
for dirpath, dirnames, filenames in os.walk(output_dir, topdown=False):
    if not filenames and not any(Path(dirpath).iterdir()):
        try:
            os.rmdir(dirpath)
        except:
            pass

print("\n清理完成!")
