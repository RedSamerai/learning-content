#!/usr/bin/env python3
"""
安全合并脚本：
1. 将"古诗文"目录内容移动到"语文"目录
2. 将"九年级全一册"目录内容移动到"九年级上/下"目录
3. 不删除任何已有的正确内容
"""

import json
import shutil
from pathlib import Path
import re

base = Path('D:/WorkBuddy/learning-app-research/learning-content/output')

def get_dest_dir(id_str, all_topics):
    """根据ID推断目标目录"""
    # 古诗文 -> 语文
    if id_str.startswith('语文古诗文'):
        return base / '语文'
    
    # 九年级全一册 -> 九年级上/下
    if '九年级全一册' in id_str:
        # 根据科目判断放在上还是下
        if '英语' in id_str or '物理' in id_str:
            # 九年级英语和物理是全一册教材，放在九年级上
            return base / '九年级上'
        elif '数学' in id_str or '化学' in id_str:
            # 九年级数学和化学分上下册
            if '上' in id_str:
                return base / '九年级上'
            else:
                return base / '九年级下'
        elif '语文' in id_str:
            return base / '九年级上'  # 九年级语文全一册放上
        elif '道法' in id_str or '道德与法治' in id_str:
            return base / '九年级上'
        elif '历史' in id_str:
            return base / '九年级上'  # 九年级历史全一册
        elif '物理' in id_str and '九下' in id_str:
            return base / '九年级下'
        elif '化学' in id_str and '九下' in id_str:
            return base / '九年级下'
        else:
            # 默认放九年级上
            return base / '九年级上'
    
    return None

def move_directory_contents(source_dir, target_dir, id_str):
    """移动目录内容"""
    if not source_dir.exists():
        return 0
    
    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)
    
    moved = 0
    for item in source_dir.iterdir():
        if item.is_dir():
            # 目标目录可能已存在同名目录，需要合并
            target_item = target_dir / item.name
            if target_item.exists():
                # 目录已存在，移动内部文件
                for subitem in item.iterdir():
                    target_subitem = target_item / subitem.name
                    if not target_subitem.exists():
                        subitem.rename(target_subitem)
                        moved += 1
                    else:
                        print(f"  跳过已存在的文件: {target_subitem}")
            else:
                item.rename(target_dir / item.name)
                moved += 1
        elif item.is_file():
            target_file = target_dir / item.name
            if not target_file.exists():
                item.rename(target_file)
                moved += 1
            else:
                print(f"  跳过已存在的文件: {target_file}")
    
    return moved

# 加载知识图谱
with open('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)

print("=" * 60)
print("Step 1: 处理古诗文目录")
print("=" * 60)

guwen_source = base / '古诗文'
guwen_target = base / '语文'

if guwen_source.exists():
    # 统计源目录内容
    guwen_json = list(guwen_source.rglob('*.json'))
    guwen_mp3 = list(guwen_source.rglob('*.mp3'))
    print(f"古诗文目录: {len(guwen_json)}个JSON, {len(guwen_mp3)}个音频")
    
    # 移动内容
    moved = move_directory_contents(guwen_source, guwen_target, 'guwen')
    print(f"移动完成: {moved}个文件")
    
    # 删除空目录
    if guwen_source.exists() and not any(guwen_source.iterdir()):
        guwen_source.rmdir()
        print("删除空目录: 古诗文")

print("\n" + "=" * 60)
print("Step 2: 处理九年级全一册目录")
print("=" * 60)

jc_source = base / '九年级全一册'
if jc_source.exists():
    # 按科目分组
    subject_dirs = {}
    for item in jc_source.iterdir():
        if item.is_dir():
            subject_dirs[item.name] = item
    
    print(f"九年级全一册目录结构:")
    for subject, dir_path in subject_dirs.items():
        json_count = sum(1 for _ in dir_path.rglob('*.json'))
        print(f"  {subject}: {json_count}个JSON")
    
    # 根据科目移动到不同位置
    for subject, dir_path in subject_dirs.items():
        if subject == '英语':
            target = base / '九年级上'
        elif subject == '物理':
            target = base / '九年级上'
        elif subject == '数学':
            target = base / '九年级上'  # 九年级数学上册
        elif subject == '化学':
            target = base / '九年级上'
        elif subject == '语文':
            target = base / '九年级上'
        elif subject == '道德与法治':
            target = base / '九年级上'
        elif subject == '历史':
            target = base / '九年级上'
        else:
            continue
        
        moved = move_directory_contents(dir_path, target, subject)
        print(f"移动 {subject} -> {target.name}: {moved}个文件")
    
    # 删除空目录
    if jc_source.exists() and not any(jc_source.iterdir()):
        jc_source.rmdir()
        print("删除空目录: 九年级全一册")

print("\n" + "=" * 60)
print("Step 3: 清理空目录")
print("=" * 60)

empty_dirs = []
for d in sorted(base.rglob('*'), reverse=True):
    if d.is_dir() and not any(d.iterdir()):
        empty_dirs.append(d)

if empty_dirs:
    print(f"删除 {len(empty_dirs)} 个空目录")
    for d in empty_dirs:
        d.rmdir()
else:
    print("无空目录")

print("\n" + "=" * 60)
print("Step 4: 验证最终状态")
print("=" * 60)

# 统计最终状态
total_json = sum(1 for f in base.rglob('*.json') if '/audio/' not in str(f) and '/image/' not in str(f))
total_audio = sum(1 for f in base.rglob('*.mp3') if f.stat().st_size > 0)
total_dirs = sum(1 for d in base.iterdir() if d.is_dir())

print(f"JSON文件总数: {total_json}")
print(f"音频文件总数: {total_audio}")
print(f"顶级目录数: {total_dirs}")

print("\n各目录JSON数量:")
for d in sorted(base.iterdir()):
    if d.is_dir():
        count = sum(1 for _ in d.rglob('*.json'))
        if count > 0:
            print(f"  {d.name}: {count}个")

print("\n合并完成!")
