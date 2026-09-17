#!/usr/bin/env python3
"""修复缺失音频 - 使用edge-tts"""
import asyncio
import edge_tts
import json
from pathlib import Path
import time

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

async def generate_audio(text, output_path, voice):
    """生成单个音频"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+5%")
        await communicate.save(str(output_path))
        return True
    except Exception as e:
        print(f"      错误: {e}")
        return False

async def main():
    # 找出缺失音频的知识点
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            audio_path = p.parent / 'audio.mp3'
            
            # 检查是否真的缺失
            if not audio_path.exists() or audio_path.stat().st_size < 1000:
                text = data.get('explanation', '')
                if text and len(text) > 10:
                    age_group = data.get('age_group', data.get('grade', ''))
                    voice = get_voice(age_group)
                    topic_name = data.get('name', '')
                    tasks.append({
                        'path': p.parent,
                        'name': topic_name,
                        'text': text,
                        'voice': voice,
                        'audio_path': audio_path
                    })
        except Exception as e:
            print(f"      读取错误: {e}")
            pass
    
    print(f"🎵 需要生成音频: {len(tasks)}个知识点\n")
    
    completed = 0
    errors = 0
    
    for i, item in enumerate(tasks):
        full_text = f"{item['name']}。{item['text']}"
        
        if (i + 1) % 5 == 0:
            print(f"\n进度: [{i+1}/{len(tasks)}] 已完成 {completed} 个, 失败 {errors} 个\n")
        
        print(f"[{i+1}/{len(tasks)}] {item['name']}", end=" ", flush=True)
        
        if await generate_audio(full_text, item['audio_path'], item['voice']):
            print("✅")
            completed += 1
        else:
            print("❌")
            errors += 1
        
        # 短暂延迟避免过载
        await asyncio.sleep(0.3)
    
    print(f"\n{'='*50}")
    print(f"✅ 成功: {completed}")
    print(f"❌ 失败: {errors}")
    print(f"📊 总计: {len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())