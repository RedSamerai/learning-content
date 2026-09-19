#!/usr/bin/env python3
"""
清理output目录：
1. 检查冗余目录（九年级全一册、古诗文）是否在正确位置已有相同内容
2. 将根目录的音频文件移动到正确的子目录
3. 删除空音频文件
4. 音频策略：仅幼儿园+幼小衔接+小学1-3年级需要音频
"""

import json
import os
import shutil
from pathlib import Path

base = Path('output')

# 加载标准知识点清单
with open('knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)
standard_ids = {t['id'] for t in all_topics}

# 定义标准目录映射（音频需要移动到的目标）
def get_audio_dest_dir(id_str):
    """根据知识点ID确定音频目标目录"""
    if id_str.startswith('kind_'):
        return base / '幼儿园'
    elif id_str.startswith('kt_'):
        return base / '幼小衔接'
    elif id_str.startswith('py_'):
        # 小学一年级
        return base / '一年级上'
    elif id_str.startswith('yx_'):
        # 小学语文
        return base / '一年级上'
    elif id_str.startswith('pm_'):
        # 小学数学
        # 根据文件名中的年级数字判断
        if '一上' in id_str or '一下' in id_str:
            return base / '一年级上' if '一上' in id_str else base / '一年级下'
        elif '二上' in id_str or '二下' in id_str:
            return base / '二年级上' if '二上' in id_str else base / '二年级下'
        elif '三上' in id_str or '三下' in id_str:
            return base / '三年级上' if '三上' in id_str else base / '三年级下'
        elif '四上' in id_str or '四下' in id_str:
            return base / '四年级上' if '四上' in id_str else base / '四年级下'
        elif '五上' in id_str or '五下' in id_str:
            return base / '五年级上' if '五上' in id_str else base / '五年级下'
        elif '六上' in id_str or '六下' in id_str:
            return base / '六年级上' if '六上' in id_str else base / '六年级下'
        else:
            return base / '小学'
    elif id_str.startswith('jy_') or id_str.startswith('je_'):
        # 初中英语
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jp_'):
        # 初中物理
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jm_'):
        # 初中数学
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jc_'):
        # 初中语文
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jch_'):
        # 初中化学
        if '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jh_'):
        # 初中历史
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jg_'):
        # 初中地理
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jci_'):
        # 初中道法
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        elif '九' in id_str:
            return base / '九年级上' if '上' in id_str else base / '九年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jb_'):
        # 初中生物
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        else:
            return base / '初中'
    elif id_str.startswith('js_'):
        # 初中科学
        if '七' in id_str:
            return base / '七年级上' if '上' in id_str else base / '七年级下'
        elif '八' in id_str:
            return base / '八年级上' if '上' in id_str else base / '八年级下'
        else:
            return base / '初中'
    elif id_str.startswith('jx_'):
        # 初中信息
        return base / '初中'
    else:
        return base

def needs_audio(id_str):
    """判断该知识点是否需要音频"""
    if id_str.startswith('kind_') or id_str.startswith('kt_'):
        return True  # 幼儿园、幼小衔接需要音频
    elif id_str.startswith('py_') or id_str.startswith('px_'):
        return True  # 小学一年级
    elif id_str.startswith('yx_'):
        return True  # 小学语文一年级
    elif id_str.startswith('pm_'):
        # 小学数学，根据年级判断
        if '一上' in id_str or '一下' in id_str:
            return True
        elif '二上' in id_str or '二下' in id_str:
            return True
        elif '三上' in id_str or '三下' in id_str:
            return True
        else:
            return False  # 四到六年级不需要音频
    return False

print("=" * 60)
print("Step 1: 检查冗余目录内容是否重复")
print("=" * 60)

# 检查冗余目录
redundant_dirs = ['九年级全一册', '古诗文']
for d in redundant_dirs:
    dir_path = base / d
    if not dir_path.exists():
        continue
    
    # 收集该目录下的所有知识点ID
    dir_ids = set()
    for f in dir_path.rglob('*.json'):
        if '/audio/' in str(f) or '/image/' in str(f):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                tid = data.get('id', '')
                if tid:
                    dir_ids.add(tid)
        except:
            pass
    
    # 检查是否在标准清单中
    in_standard = dir_ids & standard_ids
    not_in_standard = dir_ids - standard_ids
    
    print(f"\n{d}:")
    print(f"  在标准清单中: {len(in_standard)}个")
    print(f"  不在标准清单: {len(not_in_standard)}个")
    
    if not_in_standard:
        print(f"  不在标准清单的ID示例: {list(not_in_standard)[:5]}")

print("\n" + "=" * 60)
print("Step 2: 处理根目录音频文件")
print("=" * 60)

# 获取根目录所有音频文件
root_audios = list(base.glob('*.mp3'))
print(f"根目录音频文件总数: {len(root_audios)}")

# 分类统计
non_empty = [f for f in root_audios if f.stat().st_size > 0]
empty = [f for f in root_audios if f.stat().st_size == 0]
print(f"非空文件: {len(non_empty)}个")
print(f"空文件: {len(empty)}个")

# 处理空文件（删除）
if empty:
    print(f"\n删除 {len(empty)} 个空音频文件...")
    for f in empty:
        f.unlink()
    print(f"✓ 已删除空文件")

# 处理非空文件（移动到正确目录）
moved = 0
failed = 0
for audio_file in non_empty:
    # 从文件名提取知识点ID
    # 例如: jm_九上_一元.mp3 -> jm_九上_一元
    audio_name = audio_file.stem
    
    # 在标准清单中查找匹配的知识点
    target_dir = None
    for topic in all_topics:
        if topic['id'] == audio_name:
            target_dir = get_audio_dest_dir(audio_name)
            break
    
    if target_dir:
        # 创建目标目录
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动到目标目录
        target_path = target_dir / audio_file.name
        if not target_path.exists():
            audio_file.rename(target_path)
            moved += 1
        else:
            # 目标已存在，删除源文件
            audio_file.unlink()
            moved += 1
    else:
        failed += 1
        print(f"  未找到匹配的知识点: {audio_name}")

print(f"\n移动完成: {moved}个文件")
if failed:
    print(f"失败: {failed}个文件")

print("\n" + "=" * 60)
print("Step 3: 删除空目录")
print("=" * 60)

# 递归删除空目录
empty_dirs = []
for d in sorted(base.rglob('*'), reverse=True):
    if d.is_dir() and not any(d.iterdir()):
        empty_dirs.append(d)

if empty_dirs:
    print(f"删除 {len(empty_dirs)} 个空目录...")
    for d in empty_dirs:
        d.rmdir()
    print(f"✓ 已删除空目录")
else:
    print("无空目录")

print("\n" + "=" * 60)
print("Step 4: 检查最终状态")
print("=" * 60)

# 统计最终状态
total_json = sum(1 for f in base.rglob('*.json') if '/audio/' not in str(f) and '/image/' not in str(f))
total_audio = sum(1 for f in base.rglob('*.mp3') if f.stat().st_size > 0)
total_dirs = sum(1 for d in base.iterdir() if d.is_dir())

print(f"JSON文件总数: {total_json}")
print(f"音频文件总数: {total_audio}")
print(f"顶级目录数: {total_dirs}")

# 各年级音频数量统计
print("\n各年级音频分布:")
grade_dirs = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', 
              '三年级上', '三年级下', '四年级上', '四年级下', '五年级上', '五年级下',
              '六年级上', '六年级下', '七年级上', '七年级下', '八年级上', '八年级下', 
              '九年级上', '九年级下']

for grade in grade_dirs:
    grade_path = base / grade
    if grade_path.exists():
        count = sum(1 for f in grade_path.rglob('*.mp3') if f.stat().st_size > 0)
        if count > 0:
            print(f"  {grade}: {count}个音频")

print("\n清理完成!")
