#!/usr/bin/env python3
"""修复音频引用 - 音频在audio子目录"""
from pathlib import Path
import json

output_dir = Path("output")

fixed = 0
for p in output_dir.rglob("*.json"):
    if p.parent.name in ['image', 'audio']:
        continue
    
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 收集所有音频文件
        audio_files = []
        for audio_file in p.parent.rglob("*.mp3"):
            if audio_file.stat().st_size > 0:
                # 使用相对路径或文件名
                audio_files.append(audio_file.name)
        
        # 更新JSON
        if audio_files and data.get('audio') != audio_files:
            data['audio'] = audio_files
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            fixed += 1
            print(f"✅ {p.parent.name}: {audio_files}")
    except Exception as e:
        print(f"❌ {p.name}: {e}")

print(f"\n修复了 {fixed} 个文件")