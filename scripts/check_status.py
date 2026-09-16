#!/usr/bin/env python3
"""检查生成状态并继续未完成的任务"""
import json
import os
from pathlib import Path

# 加载知识图谱
with open('knowledge_graph.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

# 加载进度
progress = {}
if os.path.exists('generation_progress.json'):
    with open('generation_progress.json', 'r', encoding='utf-8') as f:
        progress = json.load(f)

# 收集所有幼儿园知识点
all_topics = []
for subject in graph['subjects']:
    for area in subject.get('areas', []):
        for obj in area.get('objectives', []):
            for topic in obj.get('topics', []):
                if 'kg' in topic.get('topic_id', ''):
                    topic['subject'] = subject['subject_id']
                    all_topics.append(topic)

print(f"幼儿园知识点总数: {len(all_topics)}\n")

# 检查每个知识点的状态
generated = []
missing = []
incomplete = []

for topic in all_topics:
    topic_id = topic['topic_id']
    subject = topic['subject']
    age_group = topic.get('age_group', '未知')
    
    # 检查JSON文件
    json_path = f"output/{subject}/{age_group}/{topic_id}.json"
    
    if os.path.exists(json_path):
        # 检查音频文件
        audio_concept = f"output/{subject}/{age_group}/{topic_id}/audio_concept.mp3"
        audio_explanation = f"output/{subject}/{age_group}/{topic_id}/audio_explanation.mp3"
        image = f"output/{subject}/{age_group}/{topic_id}/image.png"
        
        has_audio_concept = os.path.exists(audio_concept) and os.path.getsize(audio_concept) > 0
        has_audio_explanation = os.path.exists(audio_explanation) and os.path.getsize(audio_explanation) > 0
        has_image = os.path.exists(image) and os.path.getsize(image) > 0
        
        if has_audio_concept and has_audio_explanation and has_image:
            generated.append(topic_id)
        else:
            incomplete.append({
                'id': topic_id,
                'name': topic['name'],
                'missing': []
            })
            if not has_audio_concept:
                incomplete[-1]['missing'].append('concept音频')
            if not has_audio_explanation:
                incomplete[-1]['missing'].append('explanation音频')
            if not has_image:
                incomplete[-1]['missing'].append('图片')
    else:
        missing.append(topic_id)

print(f"✅ 已完成: {len(generated)}")
print(f"❌ 未完成: {len(incomplete)}")
print(f"⬜ 未生成: {len(missing)}")
print()

if incomplete:
    print("=== 需要补充的文件 ===")
    for item in incomplete:
        print(f"  {item['id']} ({item['name']}): 缺少 {', '.join(item['missing'])}")

if missing:
    print(f"\n=== 未生成的知识点 ({len(missing)}) ===")
    for mid in missing[:10]:
        print(f"  {mid}")
    if len(missing) > 10:
        print(f"  ... 还有 {len(missing)-10} 个")
