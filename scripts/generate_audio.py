#!/usr/bin/env python3
"""生成音频 - 使用edge-tts"""
import asyncio
import edge_tts
import json
from pathlib import Path

# 音色配置
VOICES = {
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
    for key, voice in VOICES.items():
        if key in age_group:
            return voice
    return "zh-CN-XiaoxiaoNeural"

async def generate_single(topic_dir, topic_name, text, voice):
    """生成单个音频"""
    audio_path = topic_dir / "audio.mp3"
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(audio_path))
        return True
    except Exception as e:
        print(f"    错误: {e}")
        return False

async def main():
    # 找出缺失音频的知识点
    missing = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            audio_path = p.parent / 'audio.mp3'
            if not audio_path.exists() or audio_path.stat().st_size < 1000:
                missing.append({
                    'path': p.parent,
                    'name': data.get('name', ''),
                    'text': data.get('explanation', ''),
                    'age_group': data.get('age_group', data.get('grade', ''))
                })
        except:
            pass
    
    print(f"🎵 需要生成音频: {len(missing)}个知识点")
    print(f"⏱️ 预计时间: {len(missing) * 3 / 60:.1f} 分钟\n")
    
    completed = 0
    for i, item in enumerate(missing):
        topic_name = item['name']
        age_group = item['age_group']
        voice = get_voice(age_group)
        full_text = f"{topic_name}。{item['text']}"
        
        if (i + 1) % 10 == 0:
            print(f"\n进度: [{i+1}/{len(missing)}] 已完成 {completed} 个\n")
        
        print(f"[{i+1}/{len(missing)}] {topic_name} ({age_group})", end=" ", flush=True)
        
        if await generate_single(item['path'], topic_name, full_text, voice):
            print("✅")
            completed += 1
        else:
            print("❌")
        
        await asyncio.sleep(0.5)  # 短暂延迟避免过载
    
    print(f"\n✅ 完成: {completed}/{len(missing)}")

if __name__ == "__main__":
    asyncio.run(main())