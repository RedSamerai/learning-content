#!/usr/bin/env python3
"""快速补全缺失音频 - 使用本地Edge-TTS"""
import asyncio, json, time
from pathlib import Path
import edge_tts

VOICE_MAP = {
    "幼儿园": "zh-CN-XiaoyiNeural",
    "幼小衔接": "zh-CN-XiaoyiNeural", 
    "一年级": "zh-CN-XiaoxiaoNeural",
    "二年级": "zh-CN-XiaoxiaoNeural",
    "三年级": "zh-CN-XiaoxiaoNeural",
    "四年级": "zh-CN-XiaoxiaoNeural",
    "五年级": "zh-CN-XiaoxiaoNeural",
    "六年级": "zh-CN-XiaoxiaoNeural",
    "初中": "zh-CN-YunxiNeural"
}

def get_voice(age_group):
    for key, voice in VOICE_MAP.items():
        if key in age_group:
            return voice
    return "zh-CN-XiaoxiaoNeural"

async def main():
    # 找出缺失音频的知识点
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            audio_path = p.parent / 'audio.mp3'
            
            if not audio_path.exists() or audio_path.stat().st_size == 0:
                text = data.get('explanation', '')
                if text:
                    age_group = data.get('age_group', data.get('grade', ''))
                    voice = get_voice(age_group)
                    tasks.append((p, text, voice, audio_path, data.get('name', '')))
        except:
            pass
    
    print(f"🎵 补全音频: {len(tasks)}个知识点")
    
    completed = 0
    for i, (json_path, text, voice, audio_path, topic_name) in enumerate(tasks):
        full_text = f"{topic_name}。{text}"
        
        # 每5个暂停一下避免过载
        if i > 0 and i % 5 == 0:
            await asyncio.sleep(1)
        
        try:
            communicate = edge_tts.Communicate(full_text, voice)
            await communicate.save(audio_path)
            completed += 1
            print(f"[{i+1}/{len(tasks)}] {topic_name} ✅")
        except Exception as e:
            print(f"[{i+1}/{len(tasks)}] {topic_name} ❌ ({e})")
    
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())