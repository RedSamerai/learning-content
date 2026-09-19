#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补全3-9岁音频 - 针对缺失部分"""
import json
import asyncio
import edge_tts
from pathlib import Path
import re

base = Path('D:/WorkBuddy/learning-app-research/learning-content')

# 3-9岁需要音频的学段
AUDIO_GRADES = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下']

# 音色配置
VOICE_MAP = {
    '幼儿园': 'zh-CN-XiaoyiNeural',
    '幼小衔接': 'zh-CN-XiaoyiNeural',
    '一年级上': 'zh-CN-XiaoxiaoNeural',
    '一年级下': 'zh-CN-XiaoxiaoNeural',
    '二年级上': 'zh-CN-XiaoxiaoNeural',
    '二年级下': 'zh-CN-XiaoxiaoNeural',
    '三年级上': 'zh-CN-XiaoxiaoNeural',
    '三年级下': 'zh-CN-XiaoxiaoNeural',
}

# 加载知识图谱
with open(base / 'knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    knowledge_base = json.load(f)

# 统计每个学段的缺失情况
missing = []
for topic in knowledge_base:
    grade = topic.get('grade', '')
    if grade not in AUDIO_GRADES:
        continue
    
    content = topic.get('content', '').strip()
    if not content or len(content) < 50:
        continue
    
    # 检查音频是否存在
    audio_dir = base / 'output' / grade / 'audio'
    audio_file = audio_dir / f"{topic['id']}.mp3"
    
    if not audio_file.exists() or audio_file.stat().st_size < 1000:
        missing.append({
            'grade': grade,
            'subject': topic.get('subject', '未知'),
            'topic': topic.get('topic', ''),
            'id': topic['id'],
            'content': content
        })

print(f"需要补全音频的知识点: {len(missing)}个\n")

# 按学段分组显示
from collections import defaultdict
by_grade = defaultdict(list)
for m in missing:
    by_grade[m['grade']].append(m)

for g in AUDIO_GRADES:
    if g in by_grade:
        print(f"{g}: {len(by_grade[g])}个缺失")

# 生成音频
async def generate_audio(topic_id, content, voice):
    try:
        communicate = edge_tts.Communicate(content, voice)
        audio_dir = base / 'output' / topic_id.split('_')[0].replace('年级', '').replace('上', '上').replace('下', '下') / 'audio'
        
        # 从知识图谱中查找正确的学段
        grade = None
        for t in knowledge_base:
            if t['id'] == topic_id:
                grade = t.get('grade', '')
                break
        
        if not grade:
            return False
        
        audio_dir = base / 'output' / grade / 'audio'
        audio_file = audio_dir / f"{topic_id}.mp3"
        
        await communicate.save(str(audio_file))
        return True
    except Exception as e:
        print(f"  音频生成失败: {topic_id}, 错误: {e}")
        return False

print("\n开始生成音频...")
import time
start = time.time()
success = 0
failed = 0

for i, m in enumerate(missing[:50]):  # 先处理前50个
    grade = m['grade']
    voice = VOICE_MAP[grade]
    content = m['content'][:2000]  # 限制长度
    
    print(f"[{i+1}/{len(missing)}] {grade} - {m['id']}...", end=" ")
    
    try:
        result = asyncio.run(generate_audio(m['id'], content, voice))
        if result:
            print("✅")
            success += 1
        else:
            print("❌")
            failed += 1
    except Exception as e:
        print(f"❌ {e}")
        failed += 1
    
    time.sleep(2)  # 2秒间隔

print(f"\n完成! 成功: {success}, 失败: {failed}")

# 继续处理剩余的
for i, m in enumerate(missing[50:]):
    grade = m['grade']
    voice = VOICE_MAP[grade]
    content = m['content'][:2000]
    
    print(f"[{51+i}/{len(missing)}] {grade} - {m['id']}...", end=" ")
    
    try:
        result = asyncio.run(generate_audio(m['id'], content, voice))
        if result:
            print("✅")
            success += 1
        else:
            print("❌")
            failed += 1
    except Exception as e:
        print(f"❌ {e}")
        failed += 1
    
    time.sleep(2)

print(f"\n最终结果: 成功: {success}, 失败: {failed}")