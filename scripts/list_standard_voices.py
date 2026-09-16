#!/usr/bin/env python3
"""列出所有非方言中文女声音色"""
import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    
    print("=== 非方言中文女声音色 ===\n")
    
    # 筛选中文女声（排除方言）
    standard_voices = []
    for v in voices:
        locale = v['Locale']
        # 排除方言地区（辽宁、陕西等）
        if 'zh-CN' in locale and v['Gender'] == 'Female' and 'liaoning' not in locale and 'shaanxi' not in locale:
            standard_voices.append(v)
    
    for i, v in enumerate(standard_voices, 1):
        print(f"{i}. {v['Name']} ({v['Locale']})")
    
    print(f"\n共 {len(standard_voices)} 个标准女声音色")

if __name__ == '__main__':
    asyncio.run(main())
