#!/usr/bin/env python3
"""全面审核所有知识点"""
from pathlib import Path
import json

output_dir = Path("output")

# 收集所有JSON文件（排除image和audio目录）
json_files = []
for p in output_dir.rglob("*.json"):
    if p.parent.name in ['image', 'audio']:
        continue
    json_files.append(p)

print(f"总共检查 {len(json_files)} 个知识点\n")

issues = {
    "no_explanation": [],
    "no_image": [],
    "no_audio": [],
    "empty_image": [],
    "short_explanation": [],
}

for p in json_files:
    try:
        data = json.load(open(p, 'r', encoding='utf-8'))
    except:
        issues["no_explanation"].append((str(p), "JSON解析失败"))
        continue
    
    topic_name = data.get('name', '未知')
    grade = data.get('grade', data.get('age_group', '未知'))
    
    # 检查explanation
    explanation = data.get('explanation', '')
    if not explanation:
        issues["no_explanation"].append((str(p), f"{topic_name} ({grade})"))
    elif len(explanation) < 50:
        issues["short_explanation"].append((str(p), f"{topic_name} ({grade}) - 仅{len(explanation)}字"))
    
    # 检查图片
    image_file = data.get('image', '')
    if not image_file:
        issues["no_image"].append((str(p), f"{topic_name} ({grade})"))
    else:
        image_path = p.parent / image_file
        if not image_path.exists():
            issues["no_image"].append((str(p), f"{topic_name} ({grade}) - 图片不存在"))
        elif image_path.stat().st_size == 0:
            issues["empty_image"].append((str(p), f"{topic_name} ({grade})"))
    
    # 检查音频
    audio_list = data.get('audio', [])
    has_audio = False
    for audio_file in audio_list:
        audio_path = p.parent / audio_file
        if audio_path.exists() and audio_path.stat().st_size > 0:
            has_audio = True
            break
    if not has_audio:
        issues["no_audio"].append((str(p), f"{topic_name} ({grade})"))

print("=" * 60)
print("审核结果")
print("=" * 60)

print(f"\n【无文本说明】共 {len(issues['no_explanation'])} 个:")
for path, desc in issues['no_explanation']:
    print(f"  ❌ {desc}")

print(f"\n【文本说明过短】共 {len(issues['short_explanation'])} 个:")
for path, desc in issues['short_explanation']:
    print(f"  ⚠️  {desc}")

print(f"\n【缺少图片】共 {len(issues['no_image'])} 个:")
for path, desc in issues['no_image']:
    print(f"  ❌ {desc}")

print(f"\n【图片为空】共 {len(issues['empty_image'])} 个:")
for path, desc in issues['empty_image']:
    print(f"  ❌ {desc}")

print(f"\n【缺少音频】共 {len(issues['no_audio'])} 个:")
for path, desc in issues['no_audio']:
    print(f"  ⚠️  {desc}")

print("\n" + "=" * 60)
total = len(json_files)
complete = total - len(issues['no_explanation']) - len(issues['no_image'])
print(f"总结: 共{total}个知识点")
print(f"完整内容: {complete}个")
print(f"问题内容: {total - complete}个")