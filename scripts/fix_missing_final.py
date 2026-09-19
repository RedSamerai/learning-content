#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补全缺失知识点 - 最终版"""
import json
import time
import requests
from pathlib import Path

# API配置
API_KEY = 'sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
BASE_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'
MODEL = 'agnes-2.5-flash'

OUTPUT_BASE = Path('output')
LOG_FILE = Path('fix_missing_progress.log')

# 加载缺失知识点
with open('missing_topics.json', 'r', encoding='utf-8') as f:
    missing_topics = json.load(f)

print(f'需要补全 {len(missing_topics)} 个知识点')

def generate_content(topic):
    tid = topic['id']
    grade = topic.get('grade', '')
    subject = topic.get('subject', '')
    title = topic.get('title', tid)
    
    voice = 'zh-CN-YunxiNeural' if '九' in grade or '八' in grade else 'zh-CN-XiaoxiaoNeural'
    
    prompt = f'''生成{subject}{grade}知识点"{title}"的详细讲解（500字以上），包含生活例子和常见误区。返回JSON格式：{{"id":"{tid}","grade":"{grade}","subject":"{subject}","content":"...","voice":"{voice}"}}'''
    
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    data = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 1500}
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"ERROR: {str(e)}"

def save_content(tid, content):
    try:
        start = content.find('{')
        end = content.rfind('}') + 1
        data = json.loads(content[start:end]) if start >= 0 else {'id': tid, 'content': content}
    except:
        data = {'id': tid, 'content': content}
    
    grade = data.get('grade', '')
    subject = data.get('subject', '')
    
    # 确定目录
    if '幼儿园' in grade: dir_path = OUTPUT_BASE / '幼儿园' / subject
    elif '幼小衔接' in grade: dir_path = OUTPUT_BASE / '幼小衔接' / subject
    elif '一年级' in grade: dir_path = OUTPUT_BASE / ('一年级上' if '上' in tid else '一年级下')
    elif '二年级' in grade: dir_path = OUTPUT_BASE / ('二年级上' if '上' in tid else '二年级下')
    elif '三年级' in grade: dir_path = OUTPUT_BASE / ('三年级上' if '上' in tid else '三年级下')
    elif '七年级' in grade: dir_path = OUTPUT_BASE / ('七年级上' if '上' in tid else '七年级下')
    elif '八年级' in grade: dir_path = OUTPUT_BASE / ('八年级上' if '上' in tid else '八年级下')
    elif '九年级' in grade: dir_path = OUTPUT_BASE / ('九年级上' if '上' in tid or '全一册' in tid else '九年级下')
    else: dir_path = OUTPUT_BASE / subject
    
    topic_dir = dir_path / subject / tid
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    with open(topic_dir / f'{tid}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return topic_dir / f'{tid}.json'

# 主循环
success, fail = 0, 0
for i, topic in enumerate(missing_topics):
    tid = topic['id']
    print(f'[{i+1}/{len(missing_topics)}] {tid}')
    
    content = generate_content(topic)
    if content.startswith('ERROR'):
        print(f'  失败: {content}')
        fail += 1
    else:
        try:
            save_content(tid, content)
            print(f'  成功')
            success += 1
        except Exception as e:
            print(f'  保存失败: {e}')
            fail += 1
    
    if i < len(missing_topics) - 1:
        time.sleep(4)

print(f'\n完成！成功: {success}, 失败: {fail}')
