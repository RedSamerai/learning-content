#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成音频 - 简单直接版本"""

import json
import asyncio
import edge_tts
from pathlib import Path
import time

OUTPUT_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content/output')
AGE_RANGE = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下']

async def generate_audio(json_file, voice):
    """生成单个音频"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = f"{data.get('topic', '')} {data.get('explanation', '')} {data.get('example', '')}"
        text = ' '.join(text.split())  # 清理空白
        
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

def main():
    print("=" * 60)
    print("批量音频生成工具")
    print("=" * 60)
    
    # 收集所有需要生成音频的JSON文件
    missing = []
    for grade in AGE_RANGE:
        grade_dir = OUTPUT_DIR / grade
        if not grade_dir.exists():
            continue
        
        for json_file in grade_dir.rglob('*.json'):
            mp3 = json_file.with_suffix('.mp3')
            audio_mp3 = json_file.parent / 'audio' / 'audio.mp3'
            
            if not mp3.exists() and not audio_mp3.exists():
                try:
                    grade_from_path = json_file.parts[1]
                except:
                    grade_from_path = grade
                
                voice = 'zh-CN-XiaoyiNeural' if grade_from_path in ['幼儿园', '幼小衔接'] else 'zh-CN-XiaoxiaoNeural'
                missing.append({'path': json_file, 'grade': grade_from_path, 'voice': voice})
    
    print(f"\n发现 {len(missing)} 个缺失音频\n")
    
    if not missing:
        print("无需生成")
        return
    
    # 按年级分组
    by_grade = {}
    for item in missing:
        g = item['grade']
        if g not in by_grade:
            by_grade[g] = []
        by_grade[g].append(item)
    
    total_success = 0
    total_fail = 0
    
    for grade in AGE_RANGE:
        if grade not in by_grade:
            continue
        
        items = by_grade[grade]
        print(f"\n{'='*60}")
        print(f"生成 {grade} 的音频 ({len(items)}个)")
        print(f"{'='*60}")
        
        grade_success = 0
        for i, item in enumerate(items):
            success, error = asyncio.run(generate_audio(item['path'], item['voice']))
            
            if success:
                print(f"✓ {item['path'].name}")
                grade_success += 1
                total_success += 1
            else:
                print(f"✗ {item['path'].name}: {error}")
                total_fail += 1
            
            time.sleep(0.05)  # 控制速度
        
        print(f"\n{grade} 完成: {grade_success}/{len(items)}")
        
        if (i + 1) % 10 == 0:
            print("暂停2秒...")
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"总计: 成功 {total_success}, 失败 {total_fail}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
