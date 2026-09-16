#!/usr/bin/env python3
"""
批量重新生成所有音频（按年龄段使用不同音色）
"""

import asyncio
import os
import json
from pathlib import Path
import edge_tts

# 音色配置
VOICE_CONFIG = {
    "小班": "zh-CN-XiaoyiNeural",      # 幼儿园用小燕
    "中班": "zh-CN-XiaoyiNeural",      # 幼儿园用小燕
    "大班": "zh-CN-XiaoyiNeural",      # 幼儿园用小燕
    "一年级": "zh-CN-XiaoxiaoNeural",  # 小学用晓晓
    "二年级": "zh-CN-XiaoxiaoNeural",  # 小学用晓晓
    # 其他年级可扩展...
}

def get_voice_for_age(age_group: str) -> str:
    """根据年龄段获取对应音色"""
    for key, voice in VOICE_CONFIG.items():
        if key in age_group:
            return voice
    # 默认用幼儿园音色
    return "zh-CN-XiaoyiNeural"

async def generate_audio(text: str, output_path: str, voice: str):
    """生成语音"""
    try:
        communicate = edge_tts.Communicate(text, voice)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False

async def main():
    print("🎙️ 批量重新生成所有音频")
    print("=" * 50)
    
    # 找到所有JSON文件
    json_files = list(Path("output").rglob("*.json"))
    total = len(json_files)
    
    for i, json_file in enumerate(json_files, 1):
        # 读取内容
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = data.get("content", {})
        concept = content.get("concept", "")
        explanation = content.get("explanation", "")
        
        # 获取年龄段
        age_group = data.get("age_group", "未知")
        voice = get_voice_for_age(age_group)
        
        # 输出路径
        topic_dir = json_file.parent
        
        print(f"\n[{i}/{total}] {json_file.relative_to('output')}")
        print(f"   年龄段: {age_group} → 音色: {voice}")
        
        # 生成概念讲解
        if concept:
            concept_path = topic_dir / "audio_concept.mp3"
            if await generate_audio(concept, concept_path, voice):
                print(f"   ✅ 概念讲解 ({os.path.getsize(concept_path)} bytes)")
        
        # 生成详细讲解
        if explanation:
            explanation_path = topic_dir / "audio_explanation.mp3"
            if await generate_audio(explanation, explanation_path, voice):
                print(f"   ✅ 详细讲解 ({os.path.getsize(explanation_path)} bytes)")
    
    print("\n" + "=" * 50)
    print("✅ 全部完成！")

if __name__ == '__main__':
    asyncio.run(main())
