#!/usr/bin/env python3
"""列出所有中文女声"""
import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    
    print("=== 中文女声音色列表 ===\n")
    
    # 筛选中文女声
    female_voices = []
    for v in voices:
        if 'zh-CN' in v['Locale'] and v['Gender'] == 'Female':
            female_voices.append(v)
    
    for i, v in enumerate(female_voices, 1):
        print(f"{i}. {v['Name']} ({v['Locale']}) - {v['Gender']}")
    
    print(f"\n共 {len(female_voices)} 个中文女声音色")

if __name__ == '__main__':
    asyncio.run(main())
