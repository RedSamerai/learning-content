#!/usr/bin/env python3
"""
重新生成所有音频（女声版）
"""

import asyncio
import os
import json
from pathlib import Path

async def generate_audio(text: str, output_path: str, voice: str = "zh-CN-XiaoxiaoNeural"):
    """生成语音（女声）"""
    try:
        import edge_tts
        
        communicate = edge_tts.Communicate(text, voice)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        await communicate.save(output_path)
        print(f"  ✅ {os.path.basename(output_path)} ({os.path.getsize(output_path)} bytes)")
        return True
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False

async def main():
    print("🎙️ 重新生成所有音频（女声）")
    print("=" * 50)
    
    # 找到所有JSON文件
    json_files = list(Path("output").rglob("*.json"))
    
    for json_file in json_files:
        print(f"\n📂 {json_file.relative_to('output')}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = data.get("content", {})
        concept = content.get("concept", "")
        explanation = content.get("explanation", "")
        
        # 生成路径
        rel_path = json_file.relative_to("output")
        topic_dir = json_file.parent
        
        concept_path = topic_dir / "audio_concept.mp3"
        explanation_path = topic_dir / "audio_explanation.mp3"
        
        # 生成音频
        if concept:
            print("  📝 概念讲解...")
            await generate_audio(concept, concept_path, "zh-CN-XiaoxiaoNeural")
        
        if explanation:
            print("  📖 详细讲解...")
            await generate_audio(explanation, explanation_path, "zh-CN-XiaoxiaoNeural")
    
    print("\n" + "=" * 50)
    print("✅ 全部完成！")

if __name__ == '__main__':
    asyncio.run(main())
