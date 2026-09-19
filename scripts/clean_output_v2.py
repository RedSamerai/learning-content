#!/usr/bin/env python3
"""
清理output目录：
1. 检查冗余目录（九年级全一册、古诗文）是否与正确位置重复
2. 将根目录的音频文件移动到正确的子目录
3. 音频策略：仅幼儿园+幼小衔接+小学1-3年级需要音频
4. 4年级以后到初三不需要音频
"""

import json
import os
import shutil
from pathlib import Path
import re

base = Path('D:/WorkBuddy/learning-app-research/learning-content/output')

# 加载标准知识点清单
with open('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)

# 建立ID到知识点的映射
topic_map = {t['id']: t for t in all_topics}

def infer_grade_from_id(id_str):
    """根据ID推断年级"""
    if id_str.startswith('kind_'):
        return '幼儿园'
    elif id_str.startswith('kt_'):
        return '幼小衔接'
    elif id_str.startswith('py_') or id_str.startswith('px_') or id_str.startswith('yx_'):
        # 小学语文/数学一年级
        if '一上' in id_str or '一下' in id_str:
            return '一年级'
    elif id_str.startswith('pm_'):
        # 小学数学
        if '一上' in id_str: return '一年级上'
        if '一下' in id_str: return '一年级下'
        if '二上' in id_str: return '二年级上'
        if '二下' in id_str: return '二年级下'
        if '三上' in id_str: return '三年级上'
        if '三下' in id_str: return '三年级下'
        if '四上' in id_str: return '四年级上'
        if '四下' in id_str: return '四年级下'
        if '五上' in id_str: return '五年级上'
        if '五下' in id_str: return '五年级下'
        if '六上' in id_str: return '六年级上'
        if '六下' in id_str: return '六年级下'
    elif id_str.startswith('jc_'):
        # 初中语文
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jm_'):
        # 初中数学
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jp_'):
        # 初中物理
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jch_'):
        # 初中化学
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jh_'):
        # 初中历史
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jg_'):
        # 初中地理
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jci_'):
        # 初中道法
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
        if '九上' in id_str: return '九年级上'
        if '九下' in id_str: return '九年级下'
    elif id_str.startswith('jb_'):
        # 初中生物
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
    elif id_str.startswith('js_'):
        # 初中科学
        if '七上' in id_str: return '七年级上'
        if '七下' in id_str: return '七年级下'
        if '八上' in id_str: return '八年级上'
        if '八下' in id_str: return '八年级下'
    return None

def get_subject_dir(id_str):
    """根据ID推断科目目录"""
    if id_str.startswith('kind_'):
        # 幼儿园科目
        if 'art' in id_str: return '艺术'
        if 'health' in id_str: return '健康'
        if 'language' in id_str: return '语言'
        if 'science' in id_str: return '科学探究'
        if 'social' in id_str: return '社会'
        return '其他'
    elif id_str.startswith('kt_'):
        # 幼小衔接科目
        if 'chinese' in id_str or 'yuwen' in id_str: return '语文'
        if 'math' in id_str: return '数学'
        if 'science' in id_str: return '科学'
        return '其他'
    elif id_str.startswith('pm_') or id_str.startswith('px_'):
        return '数学'
    elif id_str.startswith('py_') or id_str.startswith('yx_'):
        return '语文'
    elif id_str.startswith('je_'):
        return '英语'
    elif id_str.startswith('jm_'):
        return '数学'
    elif id_str.startswith('jp_'):
        return '物理'
    elif id_str.startswith('jch_'):
        return '化学'
    elif id_str.startswith('jh_'):
        return '历史'
    elif id_str.startswith('jg_'):
        return '地理'
    elif id_str.startswith('jci_'):
        return '道德与法治'
    elif id_str.startswith('jb_'):
        return '生物'
    elif id_str.startswith('js_'):
        return '科学'
    return '其他'

def needs_audio(id_str):
    """判断该知识点是否需要音频"""
    if id_str.startswith('kind_') or id_str.startswith('kt_'):
        return True  # 幼儿园、幼小衔接需要音频
    elif id_str.startswith('py_') or id_str.startswith('px_'):
        return True  # 小学语文一年级
    elif id_str.startswith('yx_'):
        return True  # 小学语文一年级
    elif id_str.startswith('pm_'):
        # 小学数学，只到三年级
        if '一上' in id_str or '一下' in id_str:
            return True
        elif '二上' in id_str or '二下' in id_str:
            return True
        elif '三上' in id_str or '三下' in id_str:
            return True
        else:
            return False  # 四到六年级不需要音频
    return False  # 初中所有科目都不需要音频

print("=" * 60)
print("Step 1: 检查冗余目录")
print("=" * 60)

# 检查冗余目录
redundant_dirs = {'九年级全一册': '九年级', '古诗文': '语文'}
redundant_info = {}

for redundant_dir, correct_parent in redundant_dirs.items():
    dir_path = base / redundant_dir
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
    in_standard = dir_ids & set(topic_map.keys())
    not_in_standard = dir_ids - set(topic_map.keys())
    
    # 检查正确位置是否已有相同内容
    correct_path = base / correct_parent
    correct_ids = set()
    for f in correct_path.rglob('*.json'):
        if '/audio/' in str(f) or '/image/' in str(f):
            continue
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                tid = data.get('id', '')
                if tid:
                    correct_ids.add(tid)
        except:
            pass
    
    overlap = in_standard & correct_ids
    
    redundant_info[redundant_dir] = {
        'path': dir_path,
        'total_ids': len(dir_ids),
        'in_standard': len(in_standard),
        'not_in_standard': len(not_in_standard),
        'overlap_with_correct': len(overlap),
        'correct_path': correct_path
    }
    
    print(f"\n{redundant_dir}:")
    print(f"  总ID数: {len(dir_ids)}")
    print(f"  在标准清单中: {len(in_standard)}")
    print(f"  不在标准清单: {len(not_in_standard)}")
    print(f"  与正确位置重复: {len(overlap)}")
    
    if overlap:
        print(f"  重复ID示例: {list(overlap)[:5]}")

print("\n" + "=" * 60)
print("Step 2: 处理根目录音频文件")
print("=" * 60)

# 获取根目录所有非空音频文件
root_audios = [f for f in base.glob('*.mp3') if f.stat().st_size > 0]
print(f"根目录音频文件数: {len(root_audios)}")

moved = 0
failed = []
for audio_file in root_audios:
    audio_name = audio_file.stem
    
    # 尝试精确匹配
    if audio_name in topic_map:
        target_grade = infer_grade_from_id(audio_name)
        target_subject = get_subject_dir(audio_name)
    else:
        # 尝试从ID前缀推断
        parts = audio_name.split('_')
        if len(parts) >= 2:
            prefix = parts[0]
            grade_part = parts[1] if len(parts) > 1 else ''
            
            # 根据前缀和年级部分推断
            if prefix in ['pm', 'jm']:
                if '一上' in audio_name or '一下' in audio_name:
                    target_grade = '一年级'
                elif '二上' in audio_name or '二下' in audio_name:
                    target_grade = '二年级'
                elif '三上' in audio_name or '三下' in audio_name:
                    target_grade = '三年级'
                elif '四上' in audio_name or '四下' in audio_name:
                    target_grade = '四年级'
                elif '五上' in audio_name or '五下' in audio_name:
                    target_grade = '五年级'
                elif '六上' in audio_name or '六下' in audio_name:
                    target_grade = '六年级'
                elif '七' in audio_name:
                    target_grade = '七年级'
                elif '八' in audio_name:
                    target_grade = '八年级'
                elif '九' in audio_name:
                    target_grade = '九年级'
                else:
                    target_grade = None
            elif prefix in ['jc', 'jm', 'jp', 'jch', 'jh', 'jg', 'jci', 'jb', 'js']:
                if '七' in audio_name:
                    target_grade = '七年级'
                elif '八' in audio_name:
                    target_grade = '八年级'
                elif '九' in audio_name:
                    target_grade = '九年级'
                else:
                    target_grade = None
            elif prefix in ['jb', 'js']:
                if '七' in audio_name:
                    target_grade = '七年级'
                elif '八' in audio_name:
                    target_grade = '八年级'
                else:
                    target_grade = None
            elif prefix == 'kind':
                target_grade = '幼儿园'
            elif prefix == 'kt':
                target_grade = '幼小衔接'
            else:
                target_grade = None
        else:
            target_grade = None
    
    if target_grade:
        # 确定目标子目录
        if target_grade == '幼儿园':
            # 幼儿园按领域分
            target_dir = base / '幼儿园'
        elif target_grade == '幼小衔接':
            target_dir = base / '幼小衔接'
        else:
            # 中小学按年级上/下分
            if '上' in audio_name:
                target_dir = base / f'{target_grade}上'
            else:
                target_dir = base / f'{target_grade}下'
        
        # 创建目标目录
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 移动文件
        target_path = target_dir / audio_file.name
        if not target_path.exists():
            audio_file.rename(target_path)
            moved += 1
        else:
            # 目标已存在，删除源
            audio_file.unlink()
            moved += 1
    else:
        failed.append(audio_name)

print(f"移动完成: {moved}个文件")
if failed:
    print(f"未移动: {len(failed)}个文件")
    print(f"示例: {failed[:10]}")

print("\n" + "=" * 60)
print("Step 3: 删除冗余目录")
print("=" * 60)

# 删除确认
for redundant_dir, info in redundant_info.items():
    if info['overlap_with_correct'] > 0:
        print(f"\n{redundant_dir} ({info['total_ids']}个文件)")
        print(f"  与正确位置重复: {info['overlap_with_correct']}个")
        print(f"  删除风险: 高 - 内容与正确位置重复，可安全删除")
        info['safe_to_delete'] = True
    else:
        print(f"\n{redundant_dir} ({info['total_ids']}个文件)")
        print(f"  与正确位置重复: 0个")
        print(f"  删除风险: 低 - 内容可能独立，建议保留")
        info['safe_to_delete'] = False

# 删除安全的冗余目录
for redundant_dir, info in redundant_info.items():
    if info.get('safe_to_delete', False):
        print(f"\n删除冗余目录: {redundant_dir}")
        shutil.rmtree(info['path'])
        print(f"✓ 已删除")

print("\n" + "=" * 60)
print("Step 4: 清理空目录")
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
print("Step 5: 验证最终状态")
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

# 检查是否需要音频的知识点是否有音频
need_audio_count = 0
have_audio_count = 0
for topic in all_topics:
    tid = topic['id']
    if needs_audio(tid):
        need_audio_count += 1
        # 检查是否有对应音频
        audio_path = base / tid.replace('/', '_') + '.mp3'
        if audio_path.exists():
            have_audio_count += 1

print(f"\n需要音频的知识点: {need_audio_count}个")
print(f"已有音频: {have_audio_count}个")
print(f"缺失音频: {need_audio_count - have_audio_count}个")

print("\n清理完成!")
