#!/usr/bin/env python3
"""审核所有生成内容，检查完整性和质量"""
import json
from pathlib import Path

print("📋 开始审核内容完整性...\n")

# 加载知识图谱
with open('knowledge_graph_k12_full.json', 'r') as f:
    g = json.load(f)

issues = []
complete_count = 0

for s in g['subjects']:
    subj = s['subject_id']
    for a in s.get('areas', []):
        for o in a.get('objectives', []):
            for t in o.get('topics', []):
                grade = t.get('grade', '')
                if '幼小衔接' in grade or '幼儿园' in grade or '小班' in grade or '中班' in grade or '大班' in grade:
                    continue
                tid = t['topic_id']
                
                # 检查文件
                paths = [
                    Path(f'output/{subj}/{grade}/{tid}.json'),
                    Path(f'output/{subj}/{grade}/{tid}/{tid}.json'),
                ]
                main_json = next((p for p in paths if p.exists()), None)
                
                if not main_json:
                    issues.append(f"❌ 缺少: {subj} {grade} {tid}")
                    continue
                
                # 读取JSON检查内容
                try:
                    with open(main_json, 'r') as f:
                        data = json.load(f)
                    
                    # 检查必填字段
                    required = ['topic_id', 'name', 'explanation', 'image', 'audio']
                    missing = [f for f in required if not data.get(f)]
                    if missing:
                        issues.append(f"⚠️  {tid}: 缺少字段 {missing}")
                    
                    # 检查图片文件
                    img_path = Path(main_json.parent / data.get('image', ''))
                    if not img_path.exists():
                        issues.append(f"⚠️  {tid}: 图片文件缺失 {data.get('image')}")
                    
                    # 检查音频文件
                    for aud in data.get('audio', []):
                        aud_path = Path(main_json.parent / aud)
                        if not aud_path.exists():
                            issues.append(f"⚠️  {tid}: 音频文件缺失 {aud}")
                    
                    complete_count += 1
                    print(f"✅ {tid} ({grade})")
                    
                except Exception as e:
                    issues.append(f"❌ {tid}: 读取错误 {e}")

print(f"\n{'='*50}")
print(f"✅ 完整内容: {complete_count}个")
print(f"❌ 问题: {len(issues)}个")

if issues:
    print("\n问题列表:")
    for i in issues[:20]:
        print(f"  {i}")
    if len(issues) > 20:
        print(f"  ... 还有 {len(issues)-20} 个问题")
else:
    print("  无问题！")