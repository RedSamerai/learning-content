#!/usr/bin/env python3
"""修复音频引用 - 音频文件在topic目录下"""
from pathlib import Path
import json

output_dir = Path("output")

fixed = 0
for p in output_dir.rglob("*.json"):
    if p.parent.name in ['image', 'audio']:
        continue
    
    try:
        # 检查同级目录的音频文件
        audio_files = []
        for audio_file in p.parent.glob("*.mp3"):
            if audio_file.stat().st_size > 0:
                audio_files.append(audio_file.name)
        
        if audio_files:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 去重并更新
            existing = set(data.get('audio', []))
            new_audio = [f for f in audio_files if f not in existing]
            
            if new_audio:
                data['audio'] = list(existing | set(audio_files))
                
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                fixed += 1
                print(f"✅ {p.parent.name}/{p.name}: {len(data['audio'])}个音频")
    except Exception as e:
        pass

print(f"\n共修复 {fixed} 个文件")