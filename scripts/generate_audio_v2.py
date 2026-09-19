#!/usr/bin/env python3
"""
音频生成脚本 - 仅生成3-9岁（幼儿园+幼小衔接+小学1-3年级）的音频
使用两个音色：
- zh-CN-XiaoyiNeural（幼儿园、幼小衔接）
- zh-CN-XiaoxiaoNeural（小学1-3年级）
"""
import json
import asyncio
import edge_tts
from pathlib import Path
import re

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

base = Path('D:/WorkBuddy/learning-app-research/learning-content/output')

async def generate_audio(topic):
    """生成单个知识点的音频"""
    grade = topic['grade']
    subject = topic['subject']
    topic_id = topic['id']
    voice = VOICE_MAP[grade]
    
    # 查找对应的JSON文件
    json_path = base / grade / subject / f"{topic_id}.json"
    if not json_path.exists():
        for sub_dir in (base / grade).rglob(f"{topic_id}.json"):
            if '/audio/' not in str(sub_dir) and '/image/' not in str(sub_dir):
                json_path = sub_dir
                break
    
    if not json_path.exists():
        return None, f"未找到JSON文件: {topic_id}"
    
    # 读取内容
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        content = data.get('content', '')
    except Exception as e:
        return None, f"读取JSON失败: {e}"
    
    # 提取纯文本（去除Markdown标记）
    text = re.sub(r'#.*\n', '', content)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'```[^`]*```', '', text)
    text = re.sub(r'\n+', ' ', text).strip()[:600]  # 限制长度
    
    # 检查是否已有音频
    audio_path = base / grade / subject / topic_id / f"{topic_id}.mp3"
    if audio_path.exists() and audio_path.stat().st_size > 0:
        return str(audio_path), None
    
    # 创建目录
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(audio_path))
        return str(audio_path), None
    except Exception as e:
        return None, f"生成失败: {e}"

async def main():
    # 加载知识图谱
    with open('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_complete.json', 
              'r', encoding='utf-8') as f:
        all_topics = json.load(f)
    
    # 筛选需要音频的知识点
    topics_to_audio = [t for t in all_topics if t.get('grade') in VOICE_MAP]
    
    print(f"需要生成音频的知识点: {len(topics_to_audio)}个")
    print(f"音色: XiaoyiNeural(幼儿园/幼小衔接), XiaoxiaoNeural(小学1-3年级)")
    print("=" * 50)
    
    success = 0
    failed = []
    
    for i, topic in enumerate(topics_to_audio, 1):
        grade = topic['grade']
        topic_id = topic['id']
        
        audio_path, error = await generate_audio(topic)
        
        if error:
            failed.append((topic_id, error))
            print(f"[{i}/{len(topics_to_audio)}] ✗ {topic_id}: {error}")
        else:
            success += 1
            print(f"[{i}/{len(topics_to_audio)}] ✓ {topic_id}")
    
    print("\n" + "=" * 50)
    print(f"完成! 成功: {success}, 失败: {len(failed)}")
    
    if failed:
        print("\n失败的知识点:")
        for tid, err in failed[:10]:
            print(f"  - {tid}: {err}")
        if len(failed) > 10:
            print(f"  ... 还有{len(failed)-10}个")

if __name__ == '__main__':
    asyncio.run(main())
