#!/usr/bin/env python3
"""测试所有女声音色"""
import asyncio
import edge_tts
import os

SAMPLE_TEXT = "小朋友你好！今天我们来学习一个新的知识。准备好了吗？让我们开始吧！"

VOICES = [
    "zh-CN-XiaoxiaoNeural",  # 通用女声
    "zh-CN-XiaoyiNeural",    # 通用女声
    "zh-CN-liaoning-XiaobeiNeural",  # 辽宁方言
    "zh-CN-shaanxi-XiaoniNeural",    # 陕西方言
]

OUTPUT_DIR = "test_audio/voices"

async def test_voice(voice: str):
    """测试一个音色"""
    filename = f"{OUTPUT_DIR}/{voice.replace('-', '_')}.mp3"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    communicate = edge_tts.Communicate(SAMPLE_TEXT, voice)
    await communicate.save(filename)
    
    size = os.path.getsize(filename)
    print(f"✅ {voice} - {size} bytes")
    return filename

async def main():
    print("🎙️ 测试所有中文女声音色...\n")
    
    files = []
    for voice in VOICES:
        print(f"测试: {voice}")
        f = await test_voice(voice)
        files.append((voice, f))
        print()
    
    print("✅ 全部完成！")
    print("\n生成文件:")
    for voice, f in files:
        print(f"  {f}")

if __name__ == '__main__':
    asyncio.run(main())
