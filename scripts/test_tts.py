#!/usr/bin/env python3
"""
测试：使用Edge-TTS生成语音
"""

import asyncio
import edge_tts

async def test_tts():
    print("🎤 测试Edge-TTS语音生成...")
    print("=" * 50)
    
    # 测试文本
    test_texts = [
        ("concept", "数字1、2、3是三个好朋友。数字像小人一样住在纸上，1最瘦，2像鸭子，3像耳朵。"),
        ("explanation", "看！数字1站得直直的，像根小棍子。它代表只有一个的东西。"),
        ("practice", "下面有3个苹果，几个苹果呀？")
    ]
    
    output_dir = "test_output/audio"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for name, text in test_texts:
        print(f"\n生成: {name}")
        
        # 幼儿园用温柔女声，稍慢
        voice = "zh-CN-XiaoxiaoNeural"
        communicate = edge_tts.Communicate(text, voice, rate="-10%")
        
        output_path = f"{output_dir}/{name}.mp3"
        await communicate.save(output_path)
        
        print(f"✅ 已保存: {output_path}")
    
    print("\n" + "=" * 50)
    print("🎉 语音生成测试完成！")
    print(f"📁 音频文件位置: {os.path.abspath(output_dir)}")

if __name__ == '__main__':
    asyncio.run(test_tts())
