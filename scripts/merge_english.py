import json
from pathlib import Path
from datetime import datetime

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'

# 加载现有知识图谱
kg = json.load(open(base / 'knowledge_graph_complete.json', encoding='utf-8'))

# 加载新的英语数据
new_items = []
for temp_file in ['scripts/temp_yingyu_1s.json', 'scripts/temp_yingyu_1x.json', 'scripts/temp_yingyu_2s.json']:
    with open(base / temp_file, encoding='utf-8') as f:
        new_items.extend(json.load(f))

print(f"新增知识点: {len(new_items)}个")

# 添加到知识图谱
kg.extend(new_items)

# 保存更新后的知识图谱
json.dump(kg, open(base / 'knowledge_graph_complete.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"知识图谱更新完成，共 {len(kg)} 个知识点")

# 生成对应的JSON文件
for item in new_items:
    grade = item['grade']
    subject = item['subject']
    topic = item['topic']
    
    # 创建目录结构
    grade_dir = output_dir / grade
    subject_dir = grade_dir / subject
    subject_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    filename = f"{topic}.json"
    filepath = subject_dir / filename
    
    # 生成内容
    content = {
        'id': item['id'],
        'grade': item['grade'],
        'subject': item['subject'],
        'chapter': item.get('chapter', ''),
        'topic': item['topic'],
        'description': item.get('description', ''),
        'content': item.get('content', ''),
        'example': item.get('example', '')
    }
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

print(f"已生成 {len(new_items)} 个知识点文件")

# 清理临时文件
import os
for temp_file in ['scripts/temp_yingyu_1s.json', 'scripts/temp_yingyu_1x.json', 'scripts/temp_yingyu_2s.json']:
    if (base / temp_file).exists():
        os.remove(base / temp_file)
        print(f"已删除临时文件: {temp_file}")

print("\n完成!")