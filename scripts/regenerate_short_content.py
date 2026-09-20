#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补全短内容文件（<200字），通过API重新生成
"""

import json
from pathlib import Path
import time
import os
import urllib.request
import urllib.error

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
API_KEY = 'sk-IoSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'

# 收集短内容文件
short_files = []
for f in output_dir.rglob('*.json'):
    try:
        data = json.loads(f.read_text(encoding='utf-8'))
        content = data.get('content', '') or data.get('explanation', '')
        if content and len(content) < 200:
            short_files.append(f)
    except:
        pass

print(f"发现 {len(short_files)} 个短内容文件")

# 系统提示
sys_prompt = """你是一个K12教育内容专家。请根据知识点编写详细的教学内容，要求：
1. 像教科书正文一样详细，不要只是提纲
2. 包含生活例子、公式定理、常见误区提醒
3. 语言生动有趣，适合小学生阅读
4. 字数不少于300字
5. 直接输出内容，不要标题或解释"""

def regenerate_content(topic, grade, subject):
    """通过API重新生成内容"""
    prompt = f"""请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 像教科书正文一样详细，包含生活例子、公式定理、常见误区提醒
2. 语言生动有趣，适合小学生阅读
3. 字数不少于300字
4. 直接输出内容正文"""
    
    payload = json.dumps({
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500
    }).encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    
    try:
        req = urllib.request.Request(API_URL, data=payload, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API错误: {e}")
        return None

# 处理每个短内容文件
success = 0
failed = 0

for i, f in enumerate(short_files):
    try:
        # 从路径提取信息
        rel_path = f.relative_to(output_dir)
        parts = list(rel_path.parts)
        grade = parts[0]  # 一年级上
        subject = parts[1]  # 英语
        
        # 从文件名提取知识点
        topic = f.stem.replace(f'{grade}-{subject}-', '')
        
        print(f"[{i+1}/{len(short_files)}] 重新生成: {f.name[:50]}...")
        
        new_content = regenerate_content(topic, grade, subject)
        
        if new_content:
            # 读取并更新
            data = json.loads(f.read_text(encoding='utf-8'))
            data['content'] = new_content
            data['explanation'] = new_content
            f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            success += 1
            print(f"  ✓ 已更新: {len(new_content)}字")
        else:
            failed += 1
            print(f"  ✗ 失败")
        
        # 限速：15 RPM
        time.sleep(4)
        
    except Exception as e:
        failed += 1
        print(f"  ✗ 错误: {e}")

print(f"\n完成: 成功{success}, 失败{failed}")