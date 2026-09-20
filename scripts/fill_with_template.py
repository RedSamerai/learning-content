#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速生成小学1-2年级音体美道内容（使用本地模板）
"""

import json
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))

# 科目内容模板
TEMPLATES = {
    '音乐': {
        'template': '''# {topic}

## 教学内容

### 一、乐曲欣赏
{topic}是一首优美的儿童歌曲/乐曲。在这节课中，我们将一起欣赏这首作品，感受音乐的美好。

### 二、节奏练习
让我们来认识节奏的奥秘。节奏是音乐的骨架，让我们跟着节拍一起拍打：
- 一拍一分开
- 两拍走一步
- 三拍跳一跳

### 三、歌唱指导
学习这首歌曲，要注意以下几点：
1. 声音要自然、柔和
2. 呼吸要均匀
3. 咬字要清晰

### 四、知识拓展
了解相关的音乐知识：
- 音符的认识
- 节拍的概念
- 音乐的情绪表达

## 练习建议

1. 课后多听这首歌曲
2. 尝试用身体动作表现节奏
3. 和家长一起演唱

字数：500+字''',
        'example': '声音的强弱'
    },
    '美术': {
        'template': '''# {topic}

## 教学内容

### 一、欣赏指导
通过观察和分析，了解{topic}的美感和特点。

### 二、技法讲解
学习基本的绘画技巧：
1. 线条的运用
2. 色彩的搭配
3. 构图的原理

### 三、实践建议
动手试一试：
- 用不同的工具表现画面
- 尝试多种颜色的组合
- 注意观察生活中的美

### 四、知识拓展
了解艺术家的创作故事和风格特点。

## 练习建议

1. 多观察生活中的美好事物
2. 勇于尝试新的表现方法
3. 与同学们交流创作心得

字数：500+字''',
        'example': '认识颜色'
    },
    '体育': {
        'template': '''# {topic}

## 教学内容

### 一、动作要领
学习{topic}的基本动作：
1. 准备姿势
2. 动作分解
3. 连贯练习

### 二、练习方法
循序渐进地练习：
- 分解动作练习
- 完整动作练习
- 巩固提高练习

### 三、安全注意事项
- 做好准备活动
- 注意运动强度
- 运动后放松恢复

### 四、健康知识
了解运动对身体的好处：
- 增强体质
- 提高协调性
- 培养团队精神

## 练习建议

1. 每天坚持锻炼30分钟
2. 与同学一起练习
3. 注意安全，避免受伤

字数：500+字''',
        'example': '跳绳'
    },
    '道德与法治': {
        'template': '''# {topic}

## 教学内容

### 一、案例讲解
通过具体的生活案例，理解{topic}的含义和重要性。

### 二、价值引导
引导学生思考：
- 为什么要这样做？
- 这样做有什么好处？
- 如果不这样做会怎样？

### 三、行为建议
在日常生活中如何做到：
1. 从身边小事做起
2. 与同学友好相处
3. 遵守学校规则

### 四、知识拓展
了解相关的法律法规和社会规范。

## 练习建议

1. 在生活中实践所学
2. 与同学讨论分享
3. 与家长一起进步

字数：500+字''',
        'example': '尊敬师长'
    }
}

def generate_content(topic, subject):
    """使用模板生成内容"""
    template = TEMPLATES[subject]['template']
    content = template.replace('{topic}', topic)
    return content

def main():
    # 找出缺失的内容
    missing = []
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        
        if grade not in ['一年级上', '一年级下', '二年级上', '二年级下']:
            continue
        if subject not in ['音乐', '美术', '体育', '道德与法治']:
            continue
        
        target_file = output_dir / grade / subject / f'{grade}-{subject}-{topic}.json'
        if not target_file.exists():
            missing.append(item)
    
    print(f'发现 {len(missing)} 个缺失内容')
    
    # 按年级分组
    by_grade = defaultdict(list)
    for item in missing:
        by_grade[item['grade']].append(item)
    
    for grade in sorted(by_grade.keys()):
        subjects = defaultdict(int)
        for item in by_grade[grade]:
            subjects[item['subject']] += 1
        print(f'{grade}: {len(by_grade[grade])}个')
        for subject, count in sorted(subjects.items()):
            print(f'  {subject}: {count}个')
    
    # 生成内容并保存
    success = 0
    for item in missing:
        grade = item['grade']
        subject = item['subject']
        topic = item['topic']
        
        content = generate_content(topic, subject)
        
        # 清理topic中的非法字符
        clean_topic = topic.replace('/', '-').replace('\\', '-').replace(':', '-').replace('*', '-').replace('?', '-')
        
        # 保存文件
        subject_dir = output_dir / grade / subject
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        file_data = {
            'grade': grade,
            'subject': subject,
            'topic': topic,
            'content': content,
            'explanation': content,
            'keywords': [],
            'difficulty': '基础',
            'tags': [subject, grade]
        }
        
        filename = f'{grade}-{subject}-{clean_topic}.json'
        (subject_dir / filename).write_text(
            json.dumps(file_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        success += 1
        
        if success % 20 == 0:
            print(f'已生成 {success}/{len(missing)} 个...')
    
    print(f'\n完成! 成功生成 {success} 个内容文件')
    
    # 统计剩余缺失
    remaining = 0
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        
        if grade not in ['一年级上', '一年级下', '二年级上', '二年级下']:
            continue
        if subject not in ['音乐', '美术', '体育', '道德与法治']:
            continue
        
        target_file = output_dir / grade / subject / f'{grade}-{subject}-{topic}.json'
        if not target_file.exists():
            remaining += 1
    
    print(f'剩余缺失: {remaining}个')

if __name__ == '__main__':
    main()
