#!/usr/bin/env python3
"""修复JSON中的音频引用"""
from pathlib import Path
import json
import os

output_dir = Path("output")

# 扫描所有包含音频的目录
for audio_dir in output_dir.rglob("audio"):
    if not audio_dir.is_dir():
        continue
    
    # 找到对应的topic目录
    topic_dir = audio_dir.parent
    json_file = topic_dir / f"{topic_dir.name}.json"
    
    if not json_file.exists():
        # 尝试找到其他可能的json文件名
        for jf in topic_dir.glob("*.json"):
            if jf.name != "knowledge_graph.json":
                json_file = jf
                break
    
    if not json_file.exists():
        continue
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 收集音频文件
        audio_files = []
        for af in audio_dir.glob("*.mp3"):
            if af.stat().st_size > 0:
                audio_files.append(af.name)
        
        # 更新JSON
        if audio_files and data.get('audio') != audio_files:
            data['audio'] = audio_files
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ {json_file.name}: 添加 {len(audio_files)} 个音频")
    except Exception as e:
        print(f"❌ {json_file.name}: {e}")

print("\n修复完成")