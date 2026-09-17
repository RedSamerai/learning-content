#!/usr/bin/env python3
"""修复所有JSON中的音频引用问题"""
from pathlib import Path
import json

count = 0
for json_path in Path('output').rglob('*.json'):
    if json_path.parent.name in ['image', 'audio']:
        continue
    
    try:
        data = json.load(open(json_path, 'r'))
        
        # 检查音频字段
        audio_list = data.get('audio', [])
        fixed_audio = []
        
        for aud in audio_list:
            aud_path = json_path.parent / aud
            if aud_path.exists():
                fixed_audio.append(aud)
        
        # 如果没有有效音频，移除音频字段
        if not fixed_audio:
            data.pop('audio', None)
        else:
            data['audio'] = fixed_audio
        
        # 保存
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        count += 1
        
    except Exception as e:
        print(f"Error {json_path}: {e}")

print(f"修复了 {count} 个JSON文件")