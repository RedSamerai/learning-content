#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""继续生成剩余音频"""

import asyncio
import edge_tts
from pathlib import Path
import json
import time

OUTPUT_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content/output')
AGE_RANGE = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下']
VOICES = {'幼儿园': 'zh-CN-XiaoyiNeural', '幼小衔接': 'zh-CN-XiaoyiNeural'}
for g in AGE_RANGE:
    if g not in VOICES:
        VOICES[g] = 'zh-CN-XiaoxiaoNeural'

async def gen_one(json_path):
    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
        text = (data.get('explanation') or data.get('content') or '')[:2000]
        if not text.strip():
            return False, 'empty'
        
        parts = list(json_path.parts)
        grade = parts[1] if len(parts) > 1 else json_path.parent.name
        voice = VOICES.get(grade, 'zh-CN-XiaoxiaoNeural')
        
        audio_path = json_path.with_suffix('.mp3')
        if audio_path.exists():
            return True, None
        
        c = edge_tts.Communicate(text, voice)
        await c.save(str(audio_path))
        return True, None
    except Exception as e:
        return False, str(e)[:50]

async def main():
    print('扫描缺失音频...')
    missing = []
    for age in AGE_RANGE:
        for mp in OUTPUT_DIR.rglob(f'*{age}*.json'):
            if '/audio/' in str(mp):
                continue
            if not mp.with_suffix('.mp3').exists():
                missing.append(mp)
    
    print(f'发现 {len(missing)} 个缺失音频')
    if not missing:
        print('全部完成！')
        return
    
    success = fail = 0
    start = time.time()
    
    for i, mp in enumerate(missing):
        ok, err = await gen_one(mp)
        if ok:
            success += 1
        else:
            fail += 1
            if (i + 1) % 50 == 0:
                print(f'进度: {i+1}/{len(missing)}, 成功: {success}, 失败: {fail}')
        if (i + 1) % 20 == 0:
            await asyncio.sleep(0.1)
    
    elapsed = time.time() - start
    print(f'\n完成！成功: {success}, 失败: {fail}, 耗时: {elapsed:.1f}秒')

if __name__ == '__main__':
    asyncio.run(main())