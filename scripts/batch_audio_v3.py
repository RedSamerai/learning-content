#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成音频 - 正确asyncio版本"""

import json
import asyncio
import edge_tts
from pathlib import Path
import time

OUTPUT_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content/output')
AGE_RANGE = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下']

def get_voice(grade):
    if grade in ['幼儿园', '幼小衔接']:
        return 'zh-CN-XiaoyiNeural'
    return 'zh-CN-XiaoxiaoNeural'

async def generate_one(json_file, voice):
    """生成单个音频"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = f"{data.get('topic', '')} {data.get('explanation', '')}"
        text = ' '.join(text.split())
        
        if len(text.strip()) < 10:
            return False, '内容太短'
        
        audio_dir = json_file.parent / 'audio'
        audio_dir.mkdir(parents=True, exist_ok=True)
        mp3_path = audio_dir / 'audio.mp3'
        
        communicate = edge_tts.Communicate(text, voice, rate="-10%")
        await communicate.save(str(mp3_path))
        return True, None
    except Exception as e:
        return False, str(e)

async def main():
    print("=" * 60)
    print("批量音频生成")
    print("=" * 60)
    
    # 收集缺失音频
    missing = []
    for grade in AGE_RANGE:
        grade_dir = OUTPUT_DIR / grade
        if not grade_dir.exists():
            continue
        
        for json_file in grade_dir.rglob('*.json'):
            mp3 = json_file.with_suffix('.mp3')
            audio_mp3 = json_file.parent / 'audio' / 'audio.mp3'
            
            if not mp3.exists() and not audio_mp3.exists():
                voice = get_voice(grade)
                missing.append({'path': json_file, 'grade': grade, 'voice': voice})
    
    print(f"\n发现 {len(missing)} 个缺失音频\n")
    
    if not missing:
        print("无需生成")
        return
    
    total = len(missing)
    success = 0
    fail = 0
    errors = []
    
    for i, item in enumerate(missing):
        ok, err = await generate_one(item['path'], item['voice'])
        
        if ok:
            print(f"✓ {item['path'].name}")
            success += 1
        else:
            print(f"✗ {item['path'].name}: {err}")
            fail += 1
            if err not in errors:
                errors.append(err)
        
        # 进度显示
        if (i + 1) % 20 == 0:
            print(f"\n进度: {i+1}/{total} ({(i+1)*100//total}%) 成功:{success} 失败:{fail}")
        
        await asyncio.sleep(0.05)  # 控制速度
    
    print(f"\n{'='*60}")
    print(f"完成: 成功 {success}, 失败 {fail}, 总计 {total}")
    print(f"{'='*60}")
    
    if errors:
        print(f"\n错误类型 ({len(set(errors))}种):")
        for e in set(errors)[:5]:
            print(f"  - {e[:100]}")

if __name__ == '__main__':
    asyncio.run(main())
