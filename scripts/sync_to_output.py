# -*- coding: utf-8 -*-
"""同步知识图谱到output目录"""

import json
from pathlib import Path

KG_PATH = Path('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_v5.json')
OUTPUT_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content/output')

print("加载知识图谱...")
kg = json.load(open(KG_PATH, encoding='utf-8'))

print(f"共 {len(kg)} 条，开始同步...\n")

for i, item in enumerate(kg):
    book_id = item['id']
    grade = item['grade']
    subject = item['subject']
    
    # 创建目录
    topic_dir = OUTPUT_DIR / grade / subject
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建JSON文件
    json_path = topic_dir / f'{book_id}.json'
    
    json_data = {
        'id': book_id,
        'grade': grade,
        'subject': subject,
        'title': item['title'],
        'topic': item['topic'],
        'pdf_pages': item.get('pdf_pages', 0),
        'pdf_size_mb': item.get('pdf_size_mb', 0),
        'pdf_path': item.get('pdf_path', ''),
        'full_text': item.get('full_text', ''),
        'text_length': item.get('text_length', 0),
        'content': item.get('content', ''),
        'explanation': item.get('explanation', ''),
        'examples': item.get('examples', []),
        'exercises': item.get('exercises', []),
        'audio': item.get('audio', '')
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    if (i + 1) % 20 == 0:
        print(f"  进度:{i+1}/{len(kg)}")

print(f"\n完成！已同步 {len(kg)} 条到 output 目录")
