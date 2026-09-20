#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为知识点生成内容 - 基于标准人教版教材风格
"""

import json
import time
from pathlib import Path

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
kg_path = base / 'knowledge_graph_complete.json'
output_dir = base / 'output'

# 加载知识图谱
kg = json.loads(kg_path.read_text(encoding='utf-8'))
print(f"加载知识图谱: {len(kg)}条")

# 内容模板库（按科目分类）
CONTENT_TEMPLATES = {
    '语文': {
        '一年级上': {
            '课文': lambda t: f"{t}是人教版一年级上册语文课本中的一篇课文。通过学习这篇课文，学生可以了解课文的主要内容，学习相关的字词，体会文章表达的思想感情。课文配有精美的插图，帮助学生理解课文内容。",
            '汉语拼音': lambda t: f"{t}是汉语拼音教学内容的一部分。汉语拼音是学习汉字的重要工具，通过声母、韵母和声调的学习，帮助学生掌握正确的读音。本课重点学习{t.split('-')[-1] if '-' in t else t}的拼读方法。",
            '识字': lambda t: f"{t}是人教版一年级上册语文课本中的识字课文。通过看图识字、猜字谜等方式，帮助学生认识汉字，积累词汇，培养识字兴趣。"
        },
        '一年级下': {
            '课文': lambda t: f"{t}是小学语文二年级下册的重要课文。课文内容贴近学生生活，语言优美，通过学习可以培养学生的阅读能力和语言表达能力。",
            '古诗': lambda t: f"{t}是经典古诗，作者通过生动的语言描绘了自然景色或表达了深刻的情感。这首诗要求学生背诵并理解诗意，体会古人的情感世界。"
        }
    },
    '数学': {
        '一年级上': {
            '准备课': lambda t: f"{t}是数学入门课程，通过数一数、比一比等活动，帮助学生建立初步的数感，认识1-5以内的数，学会比较物体的多少。",
            '认识图形': lambda t: f"{t}是图形认识的基础内容。学生通过观察、操作等活动，认识常见的立体图形和平面图形，发展空间观念。",
            '1-5的认识': lambda t: f"{t}是数的认识教学内容。学生需要掌握1-5各数的读法、写法，理解数的顺序和大小关系，学会用数表示物体的个数。"
        }
    }
}

def generate_content(item):
    """为单个知识点生成内容"""
    grade = item.get('grade', '')
    subject = item.get('subject', '')
    topic = item.get('topic', '')
    
    # 基础内容模板
    templates = {
        '语文': f"""【{topic}】
一、学习目标
1. 正确朗读课文，理解课文内容。
2. 认识本课生字，会写要求写的字。
3. 体会作者表达的思想感情。

二、课文简介
{topic}是人教版{grade}{subject}教材中的重要课文。课文通过生动的语言描述了相关内容，帮助学生理解基础知识。

三、学习要点
1. 熟读课文，注意朗读的语气和停顿。
2. 学习课文中的生词和短语。
3. 思考课文表达的主要意思。

四、拓展延伸
联系生活实际，说说你身边的类似情况。""",
        
        '数学': f"""【{topic}】
一、学习内容
学习{topic}的相关知识。

二、学习目标
1. 理解{topic}的概念和原理。
2. 掌握{topic}的计算方法。
3. 能够运用所学知识解决实际问题。

三、要点解析
{topic}是数学学习的重要内容。通过学习，学生需要：
- 理解基本概念
- 掌握计算方法
- 灵活运用知识

四、练习巩固
完成课后练习题，检验学习效果。""",
        
        '英语': f"""【{topic}】
一、学习内容
学习{topic}相关词汇和句型。

二、学习目标
1. 能够听、说、读、写本课词汇。
2. 能够运用本课句型进行简单交流。
3. 培养英语学习兴趣。

三、重点词汇
{topic.split('-')[-1] if '-' in topic else topic}

四、交际用语
练习本课对话，提高口语表达能力。""",
        
        '科学': f"""【{topic}】
一、学习内容
探索{topic}的科学知识。

二、学习目标
1. 了解{topic}的基本概念。
2. 通过观察和实验，认识科学现象。
3. 培养科学探究能力。

三、实验活动
设计简单实验，验证所学知识。

四、生活中的科学
联系生活，发现科学就在身边。""",
        
        '道德与法治': f"""【{topic}】
一、学习内容
学习{topic}的相关知识。

二、学习目标
1. 了解{topic}的基本内容。
2. 培养良好的道德品质。
3. 增强法治意识。

三、案例分析
通过具体案例分析，理解行为规范。

四、实践行动
在日常学习和生活中践行所学知识。""",
        
        '音乐': f"""【{topic}】
一、学习内容
学习{topic}的音乐知识。

二、学习目标
1. 学会演唱{topic}。
2. 理解音乐要素和表现手法。
3. 培养音乐审美能力。

三、演唱指导
注意音准、节奏和情感表达。

四、拓展欣赏
欣赏相关音乐作品，丰富音乐体验。"""
    }
    
    # 获取对应模板
    template = templates.get(subject, templates.get('语文', f"""【{topic}】
一、学习目标
学习{topic}的相关内容。

二、学习内容
{topic}是本课学习的重点内容。

三、学习要点
1. 理解{topic}的基本概念。
2. 掌握学习方法。
3. 能够联系实际应用。

四、练习巩固
完成相关练习题。"""))
    
    return template

def update_knowledge_points():
    """更新知识图谱和文件"""
    count = 0
    for i, item in enumerate(kg):
        if item.get('explanation', '').strip():
            continue  # 跳过已有内容的
        
        content = generate_content(item)
        item['explanation'] = content
        count += 1
        
        # 每50条打印进度
        if i % 50 == 0:
            print(f"处理进度: {i}/{len(kg)} ({count}条已生成)")
        
        # 保存到文件
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '').replace('/', '-').replace('\\', '-')
        
        # 清理文件名
        safe_topic = ''.join(c for c in topic if c not in '<>:"/\\|?*')
        file_name = f"{grade}-{subject}-{safe_topic}.json"
        
        grade_dir = output_dir / grade
        subject_dir = grade_dir / subject
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = subject_dir / f"{grade}-{subject}-{safe_topic}.json"
        file_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
        
        time.sleep(0.05)  # 短暂延迟避免IO压力
    
    # 保存知识图谱
    kg_path.write_text(json.dumps(kg, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"\n=== 生成完成 ===")
    print(f"生成内容: {count}条")
    print(f"知识图谱已更新")

if __name__ == '__main__':
    update_knowledge_points()
    print("\n内容生成完成！")
