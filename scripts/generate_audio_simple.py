#!/usr/bin/env python3
"""生成3-9岁知识点的音频，仅使用两个音色：
- 幼儿园/幼小衔接: zh-CN-XiaoyiNeural (活泼)
- 小学1-3年级: zh-CN-XiaoxiaoNeural (温暖)
"""
import json
import time
import edge_tts
import asyncio
from pathlib import Path

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

# 加载知识图谱
with open('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)

# 收集需要音频的知识点
topics_to_audio = []
for topic in all_topics:
    grade = topic.get('grade', '')
    if grade in VOICE_MAP:
        topics_to_audio.append(topic)

print(f"需要生成音频的知识点: {len(topics_to_audio)}个")
print(f"音色配置: XiaoyiNeural(幼儿园/幼小衔接), XiaoxiaoNeural(小学1-3年级)")
print("=" * 50)

async def generate_audio(topic):
    """生成单个知识点的音频"""
    grade = topic['grade']
    subject = topic['subject']
    topic_id = topic['id']
    voice = VOICE_MAP[grade]
    
    # 查找对应的JSON文件
    json_path = base / grade / subject / f"{topic_id}.json"
    if not json_path.exists():
        # 尝试其他路径格式
        for sub_dir in (base / grade).rglob(f"{topic_id}.json"):
            if '/audio/' not in str(sub_dir) and '/image/' not in str(sub_dir):
                json_path = sub_dir
                break
    
    if not json_path.exists():
        print(f"  未找到JSON文件: {topic_id}")
        return None
    
    # 读取内容
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        content = data.get('content', '')
    except:
        content = f"{topic_id}的学习内容"
    
    # 提取纯文本（去除Markdown标记）
    import re
    text = re.sub(r'#.*\n', '', content)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'```[^`]*```', '', text)
    text = text[:800]  # 限制长度
    
    # 生成音频文件名
    audio_name = f"{topic_id}.mp3"
    audio_path = base / grade / subject / topic_id / audio_name
    
    # 创建目录
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(audio_path))
        return str(audio_path)
    except Exception as e:
        print(f"  生成失败: {e}")
        return None

async def main():
    success = 0
    failed = 0
    
    for i, topic in enumerate(topics_to_audio, 1):
        grade = topic['grade']
        topic_id = topic['id']
        
        print(f"\n[{i}/{len(topics_to_audio)}] {topic_id} ({grade})")
        
        audio_path = await generate_audio(topic)
        
        if audio_path:
            print(f"  ✓ 已生成: {audio_path}")
            success += 1
        else:
            print(f"  ✗ 失败")
            failed += 1
        
        # 避免RPM超限
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"完成! 成功: {success}, 失败: {failed}")
    print("=" * 50)

if __name__ == '__main__':
    asyncio.run(main())
