#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成音频 - 修复版"""
import json
import asyncio
import edge_tts
from pathlib import Path
import re

base = Path('D:/WorkBuddy/learning-app-research/learning-content/output')

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
with open('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)

# 收集需要音频的知识点
topics_to_audio = []
for topic in all_topics:
    grade = topic.get('grade', '')
    if grade in VOICE_MAP:
        topics_to_audio.append(topic)

print(f"需要生成音频: {len(topics_to_audio)}个")
print("=" * 50)

async def generate_single(topic):
    """生成单个音频"""
    grade = topic['grade']
    subject = topic['subject']
    topic_id = topic['id']
    voice = VOICE_MAP[grade]
    
    # 查找JSON文件
    json_path = base / grade / subject / f"{topic_id}.json"
    if not json_path.exists():
        # 尝试其他路径
        for f in (base / grade).rglob(f"{topic_id}.json"):
            if '/audio/' not in str(f) and '/image/' not in str(f):
                json_path = f
                break
    
    if not json_path.exists():
        return False, f"未找到JSON: {topic_id}"
    
    # 读取内容
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        content = data.get('content', '')
    except Exception as e:
        content = topic_id
    
    # 简化文本
    text = re.sub(r'#.*\n', '', content)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'```[^`]*```', '', text)
    text = text[:600].strip()
    
    if not text:
        text = f"{topic_id}的学习内容"
    
    # 生成音频路径
    audio_dir = base / grade / subject / topic_id
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_path = audio_dir / f"{topic_id}.mp3"
    
    # 检查是否已存在有效音频
    if audio_path.exists() and audio_path.stat().st_size > 1000:
        return True, f"跳过(已存在): {topic_id}"
    
    # 生成音频
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(audio_path))
        
        # 验证文件大小
        if audio_path.exists() and audio_path.stat().st_size > 1000:
            return True, f"✓ {topic_id}"
        else:
            return False, f"空文件: {topic_id}"
    except Exception as e:
        return False, f"错误: {topic_id} - {e}"

async def main():
    success = 0
    failed = 0
    
    for i, topic in enumerate(topics_to_audio, 1):
        ok, msg = await generate_single(topic)
        
        if ok:
            print(f"[{i}/{len(topics_to_audio)}] {msg}")
            success += 1
        else:
            print(f"[{i}/{len(topics_to_audio)}] {msg}")
            failed += 1
        
        # 间隔避免超限
        await asyncio.sleep(0.2)
    
    print("\n" + "=" * 50)
    print(f"完成! 成功: {success}, 失败: {failed}")
    print("=" * 50)

if __name__ == '__main__':
    asyncio.run(main())
