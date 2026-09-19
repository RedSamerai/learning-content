#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成内容不足的条目
目标：确保每个知识点内容>=400字
"""

import json
import time
import requests
from pathlib import Path

BASE = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_FILE = BASE / 'knowledge_graph_complete.json'
OUTPUT_DIR = BASE / 'output'

API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'
# API Key from memory
API_KEY = 'sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
MODEL = 'agnes-2.5-flash'

def generate_content(topic, grade, subject, chapter=None):
    """生成详细的教科书式内容"""
    
    prompt = f"""你是一位经验丰富的{subject}老师，正在编写人教版教材的知识点讲解。

【知识点】{topic}
【年级】{grade}
【章节】{chapter or '未指定'}

请按以下要求生成详细讲解内容：
1. 像教科书正文一样详细展开，不要简单罗列
2. 包含生活化的例子帮助理解
3. 包含公式、定理或核心概念的详细解释
4. 包含常见误区提醒
5. 内容要丰富详实，至少400字以上
6. 使用清晰的段落结构，便于学生阅读

请直接输出讲解内容，不需要标题和引言。"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': MODEL,
        'messages': [
            {'role': 'system', 'content': '你是一位专业的K12教育内容专家，擅长用通俗易懂的方式讲解知识点。'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            return content
        else:
            print(f"  API错误: {resp.status_code}, {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  请求异常: {e}")
        return None

def main():
    print("=" * 60)
    print("开始重新生成内容不足的条目")
    print("=" * 60)
    
    # 找出内容不足300字的文件
    short_files = []
    for f in OUTPUT_DIR.rglob('*.json'):
        if '/audio/' in str(f) or '/image/' in str(f):
            continue
        try:
            data = json.load(open(f, encoding='utf-8'))
            content = data.get('content', '') or data.get('explanation', '')
            if len(content) < 300:
                short_files.append({
                    'path': f,
                    'data': data,
                    'current_len': len(content),
                    'topic': data.get('topic', 'N/A'),
                    'grade': data.get('grade', 'N/A'),
                    'subject': data.get('subject', 'N/A'),
                    'chapter': data.get('chapter', '')
                })
        except:
            pass
    
    print(f"发现 {len(short_files)} 个内容不足300字的文件\n")
    
    success = 0
    fail = 0
    
    for i, item in enumerate(short_files, 1):
        f = item['path']
        data = item['data']
        topic = item['topic']
        grade = item['grade']
        subject = item['subject']
        chapter = item['chapter']
        
        print(f"[{i}/{len(short_files)}] {topic[:50]}...")
        print(f"  当前字数: {item['current_len']}")
        
        # 生成新内容
        new_content = generate_content(topic, grade, subject, chapter)
        
        if new_content and len(new_content) >= 300:
            # 更新文件
            data['explanation'] = new_content
            data['content'] = new_content
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            print(f"  ✅ 已更新 ({len(new_content)}字)")
            success += 1
        else:
            print(f"  ❌ 生成失败或内容不足")
            fail += 1
        
        # 20RPM限制，间隔3秒
        time.sleep(3)
    
    print("\n" + "=" * 60)
    print(f"完成! 成功: {success}, 失败: {fail}")
    print("=" * 60)

if __name__ == '__main__':
    main()
