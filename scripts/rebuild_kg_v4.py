# -*- coding: utf-8 -*-
"""重建知识图谱 - 每本书一个知识点"""

import json
from pathlib import Path
from collections import Counter

# 加载筛选后的教材列表
books = json.load(open('D:/WorkBuddy/tchMaterial-parser/target_books_filtered.json', encoding='utf-8'))
print(f"教材总数: {len(books)} 本")

# 创建工作目录
output_dir = Path('D:/WorkBuddy/learning-app-research/learning-content/output')
output_dir.mkdir(parents=True, exist_ok=True)

# 创建知识图谱
knowledge_graph = []

for book in books:
    book_id = book.get('id', 'unknown')
    title = book.get('title', '')
    
    # 提取年级和科目
    grade = ''
    subject = ''
    version = ''
    
    # 年级
    if '一年级' in title:
        grade = '一年级'
    elif '二年级' in title:
        grade = '二年级'
    elif '三年级' in title:
        grade = '三年级'
    elif '四年级' in title:
        grade = '四年级'
    elif '五年级' in title:
        grade = '五年级'
    elif '六年级' in title:
        grade = '六年级'
    elif '七年级' in title:
        grade = '七年级'
    elif '八年级' in title:
        grade = '八年级'
    elif '九年级' in title:
        grade = '九年级'
    
    # 科目
    if '语文' in title:
        subject = '语文'
    elif '数学' in title:
        subject = '数学'
    elif '英语' in title:
        subject = '英语'
    elif '科学' in title:
        subject = '科学'
    elif '道德与法治' in title:
        subject = '道德与法治'
    
    # 版本（上/下）
    if '上册' in title:
        version = '上册'
    elif '下册' in title:
        version = '下册'
    
    # 知识点ID：{grade}_{subject}_{book_id_short}
    topic_id = f"{grade}_{subject}_{book_id[:8]}"
    
    # 创建知识点条目
    knowledge_entry = {
        'id': topic_id,
        'subject': subject,
        'grade': grade,
        'version': version,
        'chapter': '全书',
        'topic': title,
        'description': f"{grade}{subject}教材（人民教育出版社）{version}",
        'explanation': '',  # 待填充
        'content': '',  # 待填充
        'example': '',  # 待填充
        'key_points': '',  # 待填充
        'reference': f'https://basic.smartedu.cn/tchMaterial/detail?contentId={book_id}',
        'pdf_path': ''  # 待填充
    }
    
    knowledge_graph.append(knowledge_entry)
    
    # 创建输出目录和空文件
    subject_dir = output_dir / grade / subject
    subject_dir.mkdir(parents=True, exist_ok=True)
    
    # 文件名：{grade}_{subject}_{book_id}.json
    filename = f"{grade}_{subject}_{book_id[:8]}.json"
    filepath = subject_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(knowledge_entry, f, ensure_ascii=False, indent=2)

# 保存知识图谱
kg_path = Path('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_v4.json')
with open(kg_path, 'w', encoding='utf-8') as f:
    json.dump(knowledge_graph, f, ensure_ascii=False, indent=2)

# 统计
print(f"\n知识图谱: {len(knowledge_graph)} 个知识点")
print(f"输出文件: {len(list(output_dir.rglob('*.json')))} 个JSON文件")
print(f"知识图谱已保存到: {kg_path}")

# 年级科目分布统计
stats = Counter()
for entry in knowledge_graph:
    stats[f"{entry['grade']}-{entry['subject']}"] += 1

print("\n各年级科目分布:")
for key in sorted(stats.keys()):
    print(f"  {key}: {stats[key]}本")

print("\n一年级分布:")
year_one = [s for s in stats.keys() if s.startswith('一年级')]
for key in sorted(year_one):
    print(f"  {key}: {stats[key]}本")
