#!/usr/bin/env python3
"""列出所有中文女声音色（不分方言/标准）"""
import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    
    print("=== 所有中文女声音色 ===\n")
    
    # 筛选所有中文女声
    chinese_female = []
    for v in voices:
        if 'zh' in v['Locale'] and v['Gender'] == 'Female':
            chinese_female.append(v)
    
    for i, v in enumerate(chinese_female, 1):
        print(f"{i}. {v['Name']} ({v['Locale']}) - {v['Gender']}")
    
    print(f"\n共 {len(chinese_female)} 个中文女声音色")

if __name__ == '__main__':
    asyncio.run(main())
