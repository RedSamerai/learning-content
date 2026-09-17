#!/usr/bin/env python3
"""修复所有音频引用 - 音频文件在topic目录下"""
from pathlib import Path
import json

output_dir = Path("output")

fixed = 0
for p in output_dir.rglob("*.json"):
    if p.parent.name in ['image', 'audio']:
        continue
    
    try:
        # 找到对应的audio目录或检查同级目录
        audio_dir = p.parent / 'audio'
        if not audio_dir.exists():
            audio_dir = p.parent  # 音频文件可能直接在topic目录下
        
        audio_files = []
        for audio_file in audio_dir.glob("*.mp3"):
            if audio_file.stat().st_size > 0:
                audio_files.append(audio_file.name)
        
        if audio_files:
            # 更新JSON
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['audio'] = audio_files
            
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            fixed += 1
            print(f"✅ {p.parent.name}: {audio_files}")
    except Exception as e:
        print(f"❌ {p.name}: {e}")

print(f"\n修复了 {fixed} 个文件")