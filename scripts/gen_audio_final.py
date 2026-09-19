#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""音频生成脚本 v7 - 修复所有bug"""

import json
import asyncio
import edge_tts
from pathlib import Path
import time

BASE_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content')
OUTPUT_DIR = BASE_DIR / 'output'

VOICES = {
    '幼儿园': 'zh-CN-XiaoyiNeural',
    '幼小衔接': 'zh-CN-XiaoyiNeural',
    '一年级上': 'zh-CN-XiaoxiaoNeural',
    '一年级下': 'zh-CN-XiaoxiaoNeural',
    '二年级上': 'zh-CN-XiaoxiaoNeural',
    '二年级下': 'zh-CN-XiaoxiaoNeural',
    '三年级上': 'zh-CN-XiaoxiaoNeural',
    '三年级下': 'zh-CN-XiaoxiaoNeural',
}

AGE_RANGE = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下']

def get_text(item: dict) -> str:
    parts = []
    if item.get('topic'): parts.append(item['topic'])
    if item.get('explanation'): parts.append(item['explanation'])
    if item.get('example'): parts.append(item['example'])
    return ' '.join(parts) if parts else ''

def find_missing():
    missing = []
    for grade in AGE_RANGE:
        grade_dir = OUTPUT_DIR / grade
        if not grade_dir.exists(): continue
        
        for json_file in grade_dir.rglob('*.json'):
            mp3 = json_file.with_suffix('.mp3')
            audio_mp3 = json_file.parent / 'audio' / 'audio.mp3'
            if not mp3.exists() and not audio_mp3.exists():
                try:
                    grade_from_path = json_file.parts[1]
                except:
                    grade_from_path = grade
                missing.append({'path': json_file, 'grade': grade_from_path})
    return missing

async def gen_one(item_info):
    try:
        path = item_info['path']
        grade = item_info['grade']
        voice = VOICES.get(grade, 'zh-CN-XiaoxiaoNeural')
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = get_text(data)
        if not text or len(text.strip()) < 10:
            return False, '内容太短'
        
        audio_dir = path.parent / 'audio'
        audio_dir.mkdir(parents=True, exist_ok=True)
        mp3_path = audio_dir / 'audio.mp3'
        
        communicate = edge_tts.Communicate(text, voice, rate="-10%")
        await communicate.save(str(mp3_path))
        return True, None
    except Exception as e:
        return False, str(e)

async def main():
    print("=" * 60)
    print("音频生成工具 v7")
    print("=" * 60)
    
    missing = find_missing()
    print(f"\n发现 {len(missing)} 个缺失音频\n")
    
    if not missing:
        print("无需生成")
        return
    
    # 按年级分组
    by_grade = {}
    for item in missing:
        g = item['grade']
        if g not in by_grade: by_grade[g] = []
        by_grade[g].append(item)
    
    total_success = 0
    total_fail = 0
    
    for grade in AGE_RANGE:
        if grade not in by_grade: continue
        items = by_grade[grade]
        print(f"\n{'='*60}")
        print(f"生成 {grade} 的音频 ({len(items)}个)")
        print(f"{'='*60}")
        
        grade_success = 0
        for i, item in enumerate(items):
            success, error = await gen_one(item)
            if success:
                print(f"✓ {item['path'].name}")
                grade_success += 1
                total_success += 1
            else:
                print(f"✗ {item['path'].name}: {error}")
                total_fail += 1
            
            await asyncio.sleep(0.05)
        
        print(f"\n{grade} 完成: {grade_success}/{len(items)}")
        
        # 每10个暂停一下
        if (i + 1) % 10 == 0:
            print("暂停2秒...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"总计: 成功 {total_success}, 失败 {total_fail}")
    print(f"{'='*60}")

if __name__ == '__main__':
    asyncio.run(main())
