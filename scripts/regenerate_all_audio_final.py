#!/usr/bin/env python3
"""重新生成所有音频（按年龄段使用不同音色）"""
import asyncio
import os
import json
from pathlib import Path
import edge_tts

# 音色配置
VOICE_CONFIG = {
    "小班": "zh-CN-XiaoyiNeural",
    "中班": "zh-CN-XiaoyiNeural",
    "大班": "zh-CN-XiaoyiNeural",
    "一年级": "zh-CN-XiaoxiaoNeural",
    "二年级": "zh-CN-XiaoxiaoNeural",
    "初中": "zh-CN-XiaoxiaoNeural",
}

def get_voice_for_age(age_group: str) -> str:
    for key, voice in VOICE_CONFIG.items():
        if key in age_group:
            return voice
    return "zh-CN-XiaoyiNeural"

async def generate_audio(text: str, output_path: str, voice: str):
    try:
        communicate = edge_tts.Communicate(text, voice)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False

async def main():
    print("🎙️ 重新生成所有音频\n")
    
    json_files = list(Path("output").rglob("*.json"))
    total = len(json_files)
    
    for i, json_file in enumerate(json_files, 1):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = data.get("content", {})
        concept = content.get("concept", "")
        explanation = content.get("explanation", "")
        
        age_group = data.get("age_group", "未知")
        voice = get_voice_for_age(age_group)
        
        topic_dir = json_file.parent
        
        print(f"[{i}/{total}] {json_file.relative_to('output')}")
        print(f"   音色: {voice}")
        
        if concept:
            await generate_audio(concept, topic_dir / "audio_concept.mp3", voice)
        if explanation:
            await generate_audio(explanation, topic_dir / "audio_explanation.mp3", voice)
    
    print("\n✅ 全部完成！")

if __name__ == '__main__':
    asyncio.run(main())
