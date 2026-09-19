#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于人教版教材目录补全知识图谱
检查所有年级的内容完整性
"""
import json
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')

# 人教版教材知识点参考（基于公开教材目录）
TEXTBOOK_REFERENCE = {
    # 幼儿园 - 按《3-6岁儿童学习与发展指南》五大领域
    '幼儿园': {
        '语言': 15, '数学认知': 15, '科学探究': 12, 
        '艺术': 12, '健康': 12, '社会': 14
    },
    # 幼小衔接
    '幼小衔接': {
        '语文': 8, '数学': 8, '英语': 4, '科学': 4
    },
    # 一年级上 - 人教版一年级上册
    '一年级上': {
        '语文': {
            '识字': 20, '拼音': 15, '课文': 25, 
            '口语交际': 5, '语文园地': 10
        },
        '数学': {
            '数一数': 3, '比一比': 5, '1-5的认识': 10,
            '分与合': 8, '6-10的认识': 12, '11-20各数的认识': 8,
            '认识钟表': 5, '20以内进位加法': 12
        }
    },
    # 一年级下
    '一年级下': {
        '语文': {
            '识字': 18, '课文': 22, '口语交际': 4, '语文园地': 8
        },
        '数学': {
            '认识图形': 5, '20以内的退位减法': 10,
            '分类与整理': 5, '100以内数的认识': 15,
            '认识人民币': 8, '100以内的加法和减法': 15,
            '找规律': 5
        }
    },
    # 二年级上 - 人教版二年级上册（需扩充）
    '二年级上': {
        '语文': {
            '识字': 20, '课文': 25, '写话': 5, '语文园地': 10,
            '古诗背诵': 10
        },
        '数学': {
            '长度单位': 5, '100以内的加法和减法': 15,
            '角的初步认识': 5, '表内乘法': 20,
            '观察物体': 3, '时间': 5, '数学广角': 3
        },
        '科学': {
            '植物': 5, '动物': 5, '天气': 3, '材料': 4
        }
    },
    # 二年级下
    '二年级下': {
        '语文': {
            '识字': 18, '课文': 22, '写话': 4, '语文园地': 8, '古诗': 8
        },
        '数学': {
            '数据收集整理': 4, '表内除法': 15, '图形与变换': 5,
            '万以内数的认识': 10, '克和千克': 4,
            '万以内的加法和减法': 10, '统计': 4, '找规律': 3
        },
        '科学': {
            '植物生长': 4, '动物生活': 4, '简单机械': 3, '天气观测': 3
        }
    },
    # 三年级上
    '三年级上': {
        '语文': {
            '识字': 15, '课文': 30, '习作': 8, '语文园地': 12, '古诗': 10
        },
        '数学': {
            '时分秒': 5, '万以内的加减法': 12, '测量': 8,
            '倍的认识': 5, '多位数乘一位数': 15,
            '长方形和正方形': 8, '分数的初步认识': 10, '数学广角': 5
        },
        '英语': {
            '字母': 5, '日常用语': 15, '数字颜色': 10, '动物食物': 10, '身体家庭': 12
        },
        '科学': {
            '植物': 8, '动物': 8, '天空水': 6, '材料': 6
        }
    },
    # 三年级下
    '三年级下': {
        '语文': {'识字': 12, '课文': 25, '习作': 8, '语文园地': 10, '古诗': 8},
        '数学': {'位置方向': 6, '除法': 12, '年月日': 6, '两位数乘两位数': 10, '面积': 12, '小数': 6, '统计': 4, '数学广角': 4},
        '英语': {'复习扩展': 20, '新句型': 16},
        '科学': {'植物变化': 6, '昆虫': 6, '温度气象': 6, '杠杆': 4}
    },
}

# 加载现有知识图谱
with open(base / 'knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    existing_topics = json.load(f)

# 统计现有各年级数量
existing_counts = defaultdict(lambda: defaultdict(int))
for t in existing_topics:
    grade = t.get('grade', '')
    subject = t.get('subject', '')
    existing_counts[grade][subject] += 1

print("=== 现有知识图谱 vs 人教版教材参考 ===\n")

# 对比分析
for grade, subjects in TEXTBOOK_REFERENCE.items():
    existing = existing_counts.get(grade, {})
    
    print(f"【{grade}】")
    total_existing = sum(existing.values())
    total_reference = 0
    
    for subject, ref_count in subjects.items():
        total_reference += ref_count
        existing_count = existing.get(subject, 0)
        diff = existing_count - ref_count
        status = "✓" if abs(diff) <= 5 else "✗"
        print(f"  {subject}: 现有{existing_count}个, 参考{ref_count}个 {status}")
    
    print(f"  总计: 现有{total_existing}个, 参考{total_reference}个\n")

# 检查output目录中的实际内容
print("\n=== output目录实际内容检查 ===\n")

for grade in ['二年级上', '二年级下']:
    dir_path = base / 'output' / grade
    
    by_subject = defaultdict(lambda: {'json': 0, 'audio': 0, 'content_len': 0})
    
    for json_file in dir_path.rglob('*.json'):
        if '/audio/' in str(json_file) or '/image/' in str(json_file):
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            subject = data.get('subject', '未知')
            by_subject[subject]['json'] += 1
            
            content = data.get('content', '')
            if not content:
                content = data.get('explanation', '')
            by_subject[subject]['content_len'] += len(content)
        except:
            pass
    
    for mp3_file in dir_path.rglob('*.mp3'):
        if mp3_file.stat().st_size > 0:
            # 找到对应的科目
            parts = mp3_file.parts
            if len(parts) >= 4:
                subject = parts[3]
                by_subject[subject]['audio'] += 1
    
    print(f"【{grade}】")
    for subject, stats in sorted(by_subject.items()):
        avg_len = stats['content_len'] / stats['json'] if stats['json'] > 0 else 0
        print(f"  {subject}: {stats['json']}个JSON, {stats['audio']}个音频, 平均{avg_len:.0f}字")
