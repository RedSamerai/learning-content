#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量补全缺失知识点内容（使用模板，不依赖API）
"""

import json
import time
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
kg_path = base / 'knowledge_graph_complete.json'

# 加载知识图谱
kg = json.loads(kg_path.read_text(encoding='utf-8'))
print(f"加载知识图谱: {len(kg)}条")

# 按年级-科目分组
by_grade_subject = defaultdict(list)
for item in kg:
    grade = item.get('grade', '')
    subject = item.get('subject', '')
    topic = item.get('topic', '')
    chapter = item.get('chapter', '') or '基础'
    
    if not topic:
        continue
    
    key = f"{grade}-{subject}"
    by_grade_subject[key].append({
        'item': item,
        'topic': topic,
        'chapter': chapter,
        'target_file': output_dir / grade / subject / f"{grade}-{subject}-{topic.replace('/', '-')}.json"
    })

# 内容模板（针对不同学科和年级）
TEMPLATES = {
    '语文': {
        '小学低年级': '''【课题】{topic}

【教学目标】
1. 认识本课的生字词，正确读写重点词语。
2. 正确、流利、有感情地朗读课文。
3. 理解课文内容，体会作者表达的思想感情。

【生字词】
{topic}：掌握本课生字，注意字形和读音。

【课文内容】
本课主要讲述了关于{topic}的内容，通过生动的描写，让我们了解了相关知识。

【思考与练习】
1. 朗读课文，思考文章的结构特点。
2. 找出文中描写精彩的句子，摘抄下来。
3. 联系生活实际，谈谈你对{topic}的理解。''',
        '初中': '''【课题】{topic}

【学习目标】
1. 积累文言词汇，理解文章内容。
2. 品味语言，体会作者情感。
3. 背诵重点段落，提升文学素养。

【作者简介】
本文作者以独特的视角，描写了{topic}相关内容，语言优美，意境深远。

【文章结构】
全文围绕{topic}展开，结构清晰，层次分明。

【重点语句赏析】
文中多处运用修辞手法，生动形象地表达了作者的情感。

【拓展延伸】
请同学们结合所学，思考{topic}在现实生活中的意义。'''
    },
    '数学': {
        '小学低年级': '''【课题】{topic}

【教学目标】
1. 理解{topic}的基本概念。
2. 掌握{topic}的计算方法。
3. 能运用{topic}解决简单的实际问题。

【知识点讲解】
{topic}是小学数学的重要内容，它帮助我们理解数和形的关系。

【例题解析】
例1：关于{topic}的基础题目。
解：运用{topic}的相关知识，逐步分析求解。

【练习巩固】
1. 完成课本相关练习题。
2. 运用{topic}解决生活中的数学问题。''',
        '初中': '''【课题】{topic}

【学习目标】
1. 理解{topic}的定义和性质。
2. 掌握{topic}的定理和公式。
3. 能灵活运用{topic}解决综合问题。

【知识要点】
{topic}是初中数学的核心内容之一，在代数、几何中都有广泛应用。

【定理公式】
涉及{topic}的重要定理和公式需要熟记并会灵活运用。

【典型例题】
通过例题讲解{topic}的应用方法，培养逻辑思维。

【能力提升】
请同学们独立完成{topic}的综合练习题。'''
    },
    '英语': {
        '小学': '''【课题】{topic}

【学习目标】
1. 掌握{topic}相关的单词和短语。
2. 能听懂、会说、会读{topic}相关内容。
3. 能运用{topic}进行简单交流。

【重点词汇】
{topic}：本课的核心词汇，注意发音和拼写。

【重点句型】
学习{topic}相关的生活用语。

【情景对话】
模拟{topic}的实际运用场景，进行角色扮演。

【课后作业】
背诵{topic}相关单词，完成练习。'''
    },
    '科学': {
        '小学': '''【课题】{topic}

【学习目标】
1. 了解{topic}的基本概念。
2. 通过观察和实验，理解{topic}的原理。
3. 培养科学探究的兴趣和能力。

【知识讲解】
{topic}是自然科学的重要内容，与我们的日常生活密切相关。

【实验探究】
通过简单的实验活动，验证{topic}的相关知识。

【生活应用】
{topic}在生活中有哪些应用？请同学们仔细观察和思考。

【总结归纳】
回顾本课所学，梳理{topic}的知识脉络。'''
    },
    '物理': {
        '初中': '''【课题】{topic}

【学习目标】
1. 理解{topic}的基本概念和规律。
2. 掌握{topic}的相关公式和计算方法。
3. 能运用{topic}解释生活中的物理现象。

【知识要点】
{topic}是物理学的重要内容，涉及力学、电学等多个方面。

【概念解析】
详细讲解{topic}的定义、内涵和外延。

【公式应用】
{topic}相关的计算公式和应用方法。

【习题训练】
通过典型例题，巩固{topic}的知识和方法。'''
    },
    '化学': {
        '初中': '''【课题】{topic}

【学习目标】
1. 认识{topic}的基本概念和性质。
2. 掌握{topic}的化学方程式。
3. 理解{topic}在实际生活中的应用。

【知识要点】
{topic}是化学学科的重要内容，涉及物质的组成、结构和变化。

【实验观察】
通过化学实验，观察{topic}相关反应的现象。

【方程式书写】
{topic}相关的化学反应方程式及配平方法。

【实际应用】
{topic}在工业、农业、医疗等领域的应用。'''
    },
    '历史': {
        '初中': '''【课题】{topic}

【学习目标】
1. 了解{topic}的历史背景和发展过程。
2. 理解{topic}在历史发展中的重要意义。
3. 培养历史思维和史料分析能力。

【历史背景】
{topic}发生的历史背景和社会环境。

【主要内容】
详细讲述{topic}的主要事件和人物。

【历史意义】
{topic}对后世的影响和历史价值。

【思考讨论】
结合史实，探讨{topic}的历史启示。'''
    },
    '地理': {
        '初中': '''【课题】{topic}

【学习目标】
1. 了解{topic}的基本地理知识。
2. 学会阅读和使用地图。
3. 理解{topic}与人类活动的关系。

【地理位置】
{topic}的地理位置和区域特征。

【自然环境】
{topic}的自然环境特点，包括气候、地形、水文等。

【人文地理】
{topic}的人口、城市、经济等人文地理特征。

【区域发展】
{topic}的发展现状和未来展望。'''
    },
    '生物': {
        '初中': '''【课题】{topic}

【学习目标】
1. 了解{topic}的基本概念和特征。
2. 理解{topic}的结构和功能。
3. 认识{topic}与生活健康的关系。

【知识讲解】
{topic}是生物学的重要内容，涉及生命的本质和规律。

【结构功能】
{topic}的结构特点与其生理功能相适应。

【生活联系】
{topic}与健康、环境等方面的联系。

【拓展阅读】
推荐阅读{topic}相关的科普知识。'''
    },
    '道德与法治': {
        '小学': '''【课题】{topic}

【学习目标】
1. 了解{topic}的基本知识。
2. 培养正确的价值观和行为准则。
3. 提高道德判断和法律意识。

【知识要点】
{topic}是我们成长过程中需要学习的重要内容。

【案例分析】
通过具体案例，理解{topic}的实际意义。

【行为指导】
在日常学习中如何践行{topic}的要求。

【实践活动】
开展与{topic}相关的主题班会或实践活动。'''
    },
    '音乐': {
        '小学': '''【课题】{topic}

【学习目标】
1. 欣赏{topic}，感受音乐的美。
2. 学习{topic}的基本音乐知识。
3. 能跟唱{topic}并进行简单的音乐创作。

【音乐欣赏】
聆听{topic}，感受其旋律、节奏和情感表达。

【知识学习】
{topic}涉及的音乐要素和表现手法。

【歌唱实践】
学唱{topic}，注意音准和节奏。

【创意活动】
运用{topic}的元素进行简单的音乐创作。'''
    },
    '美术': {
        '小学': '''【课题】{topic}

【学习目标】
1. 了解{topic}的基本知识和技法。
2. 学会观察和表现{topic}。
3. 培养审美能力和创造能力。

【知识讲解】
{topic}是美术学习的重要内容，涉及造型、色彩等要素。

【技法学习】
学习表现{topic}的基本技法和步骤。

【欣赏评述】
欣赏优秀的{topic}作品，提高审美鉴赏能力。

【创作实践】
运用所学技法，创作关于{topic}的美术作品。'''
    },
    '体育': {
        '小学': '''【课题】{topic}

【学习目标】
1. 掌握{topic}的基本技能和动作要领。
2. 提高{topic}相关的身体素质。
3. 培养{topic}的运动兴趣和习惯。

【技能讲解】
{topic}的动作要领和技术规范。

【练习方法】
通过多种练习方法，熟练掌握{topic}。

【安全防护】
进行{topic}时要注意的安全事项。

【体能发展】
{topic}对促进身体发育的积极作用。'''
    }
}

# 根据年级和科目选择模板
def get_template(grade, subject, topic):
    if subject in TEMPLATES:
        templates = TEMPLATES[subject]
        if '小学低年级' in templates and grade in ['一年级上', '一年级下', '二年级上', '二年级下']:
            return templates['小学低年级'].format(topic=topic)
        elif '初中' in templates and grade.startswith('七') or grade.startswith('八') or grade.startswith('九'):
            return templates['初中'].format(topic=topic)
        elif '小学' in templates:
            return templates['小学'].format(topic=topic)
        # 默认返回第一个模板
        first_key = list(templates.keys())[0]
        return templates[first_key].format(topic=topic)
    
    # 通用模板
    return f'''【课题】{topic}

【学习目标】
1. 了解{topic}的基本概念。
2. 掌握{topic}的相关知识点。
3. 能运用所学知识解决实际问题。

【知识讲解】
{topic}是本科目学习的重要内容，它帮助我们理解相关领域的知识。

【重点内容】
本课重点学习{topic}的相关知识，包括定义、特点和运用方法。

【练习巩固】
完成相关练习题，巩固对{topic}的理解。

【总结】
通过本课学习，掌握{topic}的核心要点。'''

# 生成并保存内容
generated = 0
skipped = 0

for key, lessons in by_grade_subject.items():
    grade, subject = key.split('-', 1)
    
    for lesson in lessons:
        item = lesson['item']
        topic = lesson['topic']
        target_file = lesson['target_file']
        
        # 检查是否已有内容
        if target_file.exists():
            existing = json.loads(target_file.read_text(encoding='utf-8'))
            if existing.get('explanation') and len(existing.get('explanation', '')) >= 50:
                skipped += 1
                continue
        
        # 生成内容
        content = get_template(grade, subject, topic)
        
        # 更新知识图谱条目
        item['explanation'] = content
        
        # 创建目录并保存
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
        
        generated += 1
        if generated % 100 == 0:
            print(f"已生成 {generated} 个文件...")

print(f"\n生成完成！")
print(f"  新生成: {generated} 个文件")
print(f"  跳过已有: {skipped} 个文件")

# 保存更新后的知识图谱
kg_path.write_text(json.dumps(kg, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"知识图谱已更新: {kg_path}")
