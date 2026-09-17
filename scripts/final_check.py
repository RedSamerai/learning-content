#!/usr/bin/env python3
"""正确统计音频完成度"""
from pathlib import Path
import json

total = 0
has_audio = 0
has_exp = 0
has_img = 0
complete = 0

for p in Path('output').rglob('*.json'):
    if p.parent.name in ['image', 'audio']:
        continue
    total += 1
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
        
        # 检查文本
        has_exp = bool(data.get('explanation')) and len(data.get('explanation', '')) > 20
        
        # 检查图片
        img_path = p.parent / data.get('image', '')
        has_img = img_path.exists() and img_path.stat().st_size > 0
        
        # 检查音频 - 检查audio子目录和同级目录
        has_audio = False
        for search_dir in [p.parent / 'audio', p.parent]:
            if search_dir.exists():
                for af in search_dir.glob('*.mp3'):
                    if af.stat().st_size > 0:
                        has_audio = True
                        break
            if has_audio:
                break
        
        if has_exp: has_exp_count += 1
        if has_img: has_img_count += 1
        if has_audio: has_audio_count += 1
        if has_exp and has_img and has_audio:
            complete += 1
    except Exception as e:
        pass

print(f'=== 最终审核报告 ===')
print(f'总知识点: {total}')
print(f'有文本: {has_exp_count}/{total} ({has_exp_count*100//total}%)')
print(f'有图片: {has_img_count}/{total} ({has_img_count*100//total}%)')
print(f'有音频: {has_audio_count}/{total} ({has_audio_count*100//total}%)')
print(f'完整内容: {complete}/{total} ({complete*100//total}%)')