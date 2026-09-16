#!/usr/bin/env python3
"""测试所有中文女声音色（包括方言）"""
import asyncio
import edge_tts
import os

SAMPLE_TEXT = "小朋友你好！今天我们来学习一个新的知识。准备好了吗？让我们开始吧！"

VOICES = [
    ("XiaoxiaoNeural", "zh-CN-XiaoxiaoNeural", "标准女声"),
    ("XiaoyiNeural", "zh-CN-XiaoyiNeural", "标准女声"),
    ("XiaobeiNeural", "zh-CN-liaoning-XiaobeiNeural", "辽宁方言"),
    ("XiaoniNeural", "zh-CN-shaanxi-XiaoniNeural", "陕西方言"),
]

OUTPUT_DIR = "test_audio/all_voices"

async def test_voice(name: str, voice: str, desc: str):
    """测试一个音色"""
    filename = f"{OUTPUT_DIR}/{name}.mp3"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    communicate = edge_tts.Communicate(SAMPLE_TEXT, voice)
    await communicate.save(filename)
    
    size = os.path.getsize(filename)
    print(f"✅ {name} ({desc}) - {size} bytes")
    return filename, name, desc

async def main():
    print("🎙️ 测试所有中文女声音色...\n")
    
    files = []
    for name, voice, desc in VOICES:
        print(f"生成: {name}")
        f = await test_voice(name, voice, desc)
        files.append(f)
        print()
    
    print("✅ 全部完成！")
    print(f"\n生成文件:")
    for f, name, desc in files:
        print(f"  {f}")

if __name__ == '__main__':
    asyncio.run(main())
