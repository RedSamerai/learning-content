#!/usr/bin/env python3
"""检查K12生成进度"""
import json
import os
from pathlib import Path

# 加载知识图谱
with open('knowledge_graph_k12.json', 'r', encoding='utf-8') as f:
    graph = json.load(f)

total = graph['statistics']['total_topics']
completed = 0
failed = []

for s in graph['subjects']:
    for a in s.get('areas', []):
        for o in a.get('objectives', []):
            for t in o.get('topics', []):
                tid = t['topic_id']
                subj = s['subject_id']
                grade = t.get('grade', '')
                path = Path(f'output/{subj.lower()}/{grade}/{tid}.json')
                if path.exists():
                    completed += 1
                else:
                    failed.append(f'{tid} ({grade})')

print(f'总知识点: {total}')
print(f'已完成: {completed}')
print(f'未完成: {len(failed)}')
if failed:
    print('\n未完成列表:')
    for f in failed:
        print(f'  - {f}')
