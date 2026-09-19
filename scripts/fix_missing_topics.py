#!/usr/bin/env python3
"""
补全缺失的知识点内容
仅生成文本，不生成音频
RPM限制：20次/分钟，使用4秒间隔
"""

import json
import time
import requests
import os
import sys
from pathlib import Path
from datetime import datetime
import io

# 设置标准输出为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API配置
API_KEY = "sk-IoS开头的key"  # 用户提供的Key
BASE_URL = "https://apihub.agnes-ai.com/v1/chat/completions"
MODEL = "agnes-2.5-flash"

# 输出目录
OUTPUT_BASE = Path('D:/WorkBuddy/learning-app-research/learning-content/output')
LOG_FILE = Path('D:/WorkBuddy/learning-app-research/learning-content/fix_missing_progress.log')

# 加载缺失知识点列表
with open('missing_topics.json', 'r', encoding='utf-8') as f:
    missing_topics = json.load(f)

print(f"需要补全 {len(missing_topics)} 个知识点")

def generate_content(topic):
    """生成知识点内容"""
    tid = topic['id']
    grade = topic.get('grade', '')
    subject = topic.get('subject', '')
    title = topic.get('title', tid)
    
    # 根据科目设置音色
    if '幼儿园' in grade or '幼小衔接' in grade:
        voice = "zh-CN-XiaoyiNeural"
    elif '小学' in grade or '一' in grade or '二' in grade or '三' in grade:
        voice = "zh-CN-XiaoxiaoNeural"
    else:
        voice = "zh-CN-YunxiNeural"
    
    prompt = f"""你是一个专业的K12教育内容创作者。请为以下知识点生成详细的教科书式讲解内容：

知识点：{tid}
年级：{grade}
科目：{subject}
标题：{title}

要求：
1. 生成详细的教科书式正文讲解（至少500字）
2. 包含生活例子帮助理解
3. 包含公式、定理或关键概念
4. 包含常见误区提醒
5. 语言通俗易懂，适合该年龄段学生
6. 不要包含练习题

格式：
```json
{{
  "id": "{tid}",
  "grade": "{grade}",
  "subject": "{subject}",
  "title": "{title}",
  "content": "详细的教科书式讲解内容...",
  "voice": "{voice}"
}}
```"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是专业的K12教育内容创作者"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=60, verify=False)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content
    except Exception as e:
        return f"ERROR: {str(e)}"

def save_content(tid, content):
    """保存内容到文件"""
    # 解析JSON
    try:
        # 提取JSON部分
        start = content.find('{')
        end = content.rfind('}') + 1
        if start >= 0 and end > start:
            data = json.loads(content[start:end])
        else:
            data = {"id": tid, "content": content}
    except:
        data = {"id": tid, "content": content}
    
    # 确定保存路径
    grade = data.get('grade', '')
    subject = data.get('subject', '')
    
    # 构建路径
    if '幼儿园' in grade:
        dir_path = OUTPUT_BASE / '幼儿园' / subject
    elif '幼小衔接' in grade:
        dir_path = OUTPUT_BASE / '幼小衔接' / subject
    elif '一年级' in grade:
        dir_path = OUTPUT_BASE / '一年级上' if '上' in tid else OUTPUT_BASE / '一年级下'
    elif '二年级' in grade:
        dir_path = OUTPUT_BASE / '二年级上' if '上' in tid else OUTPUT_BASE / '二年级下'
    elif '三年级' in grade:
        dir_path = OUTPUT_BASE / '三年级上' if '上' in tid else OUTPUT_BASE / '三年级下'
    elif '四年级' in grade:
        dir_path = OUTPUT_BASE / '四年级上' if '上' in tid else OUTPUT_BASE / '四年级下'
    elif '五年级' in grade:
        dir_path = OUTPUT_BASE / '五年级上' if '上' in tid else OUTPUT_BASE / '五年级下'
    elif '六年级' in grade:
        dir_path = OUTPUT_BASE / '六年级上' if '上' in tid else OUTPUT_BASE / '六年级下'
    elif '七年级' in grade:
        dir_path = OUTPUT_BASE / '七年级上' if '上' in tid else OUTPUT_BASE / '七年级下'
    elif '八年级' in grade:
        dir_path = OUTPUT_BASE / '八年级上' if '上' in tid else OUTPUT_BASE / '八年级下'
    elif '九年级' in grade:
        if '全一册' in tid:
            dir_path = OUTPUT_BASE / '九年级上'  # 九年级全一册放九年级上
        else:
            dir_path = OUTPUT_BASE / '九年级上' if '上' in tid else OUTPUT_BASE / '九年级下'
    else:
        dir_path = OUTPUT_BASE / subject
    
    # 创建目录
    topic_dir = dir_path / subject / tid
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON
    output_file = topic_dir / f"{tid}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

# 主循环
success_count = 0
fail_count = 0
start_time = time.time()

with open(LOG_FILE, 'a', encoding='utf-8') as log:
    log.write(f"\n{'='*60}\n")
    log.write(f"补全缺失知识点开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write(f"{'='*60}\n")
    
    for i, topic in enumerate(missing_topics):
        tid = topic['id']
        print(f"[{i+1}/{len(missing_topics)}] 处理: {tid}")
        log.write(f"\n[{i+1}/{len(missing_topics)}] 处理: {tid}\n")
        
        # 生成内容
        content = generate_content(topic)
        
        if content.startswith("ERROR"):
            print(f"  失败: {content}")
            log.write(f"  失败: {content}\n")
            fail_count += 1
        else:
            # 保存内容
            try:
                output_file = save_content(tid, content)
                print(f"  成功: {output_file}")
                log.write(f"  成功: {output_file}\n")
                success_count += 1
            except Exception as e:
                print(f"  保存失败: {e}")
                log.write(f"  保存失败: {e}\n")
                fail_count += 1
        
        # RPM控制：4秒间隔
        if i < len(missing_topics) - 1:
            time.sleep(4)
            log.write(f"  等待4秒...\n")

elapsed = time.time() - start_time
print(f"\n{'='*60}")
print(f"补全完成！")
print(f"成功: {success_count}个")
print(f"失败: {fail_count}个")
print(f"耗时: {elapsed:.1f}秒")
print(f"{'='*60}")

with open(LOG_FILE, 'a', encoding='utf-8') as log:
    log.write(f"\n补全完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write(f"成功: {success_count}个\n")
    log.write(f"失败: {fail_count}个\n")
    log.write(f"总耗时: {elapsed:.1f}秒\n")
