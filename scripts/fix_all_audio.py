#!/usr/bin/env python3
"""修复所有音频引用"""
from pathlib import Path
import json

output_dir = Path("output")

fixed = 0
for p in output_dir.rglob("*.json"):
    if p.parent.name in ['image', 'audio']:
        continue
    
    try:
        # 找到音频文件 - 可能在audio子目录或同级目录
        audio_files = []
        
        # 先检查audio子目录
        audio_dir = p.parent / 'audio'
        if audio_dir.exists():
            for audio_file in audio_dir.glob("*.mp3"):
                if audio_file.stat().st_size > 0:
                    audio_files.append(audio_file.name)
        
        # 再检查同级目录（有些音频可能在topic目录下）
        if not audio_files:
            for audio_file in p.parent.glob("*.mp3"):
                if audio_file.stat().st_size > 0:
                    audio_files.append(audio_file.name)
        
        if audio_files:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['audio'] = audio_files
            
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            fixed += 1
            print(f"✅ {p.parent.name}/{p.name}: {len(audio_files)}个音频")
    except Exception as e:
        pass

print(f"\n共修复 {fixed} 个文件")