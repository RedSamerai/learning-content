#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补全缺失科目的内容文件
"""

import json
from pathlib import Path
import time
import urllib.request
import urllib.error
import random

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
API_KEY = 'sk-IoSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'

# 科目映射
subject_map = {
    '道德与法治': '道德与法治',
    'morality': '道德与法治',
    '音乐': '音乐',
    '美术': '美术',
    '体育': '体育',
    '健康': '健康',
    '语言': '语言',
    '社会': '社会',
    '艺术': '艺术'
}

# 系统提示
sys_prompt = """你是一个K12教育内容专家。请根据知识点编写详细的教学内容，要求：
1. 像教科书正文一样详细，不要只是提纲
2. 包含生活例子、实际应用
3. 语言生动有趣，适合小学生阅读
4. 字数不少于400字
5. 直接输出内容正文"""

def generate_content(topic, grade, subject):
    """通过API生成内容"""
    prompt = f"""请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 像教科书正文一样详细，包含生活例子和实际应用
2. 语言生动有趣，适合小学生阅读
3. 字数不少于400字
4. 直接输出内容正文，不要标题或解释"""
    
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

def ensure_dir_exists(grade, subject):
    """确保目录存在"""
    grade_dir = output_dir / grade
    subject_dir = grade_dir / subject
    subject_dir.mkdir(parents=True, exist_ok=True)
    return subject_dir

def main():
    # 从知识图谱读取数据
    kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))
    
    # 筛选缺失的科目
    missing_items = []
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        
        # 检查是否在Output目录中存在
        target_dir = output_dir / grade / subject
        if not target_dir.exists():
            missing_items.append(item)
        else:
            # 检查是否有对应的JSON文件
            expected_name = f"{grade}-{subject}-{topic}.json"
            if not (target_dir / expected_name).exists():
                missing_items.append(item)
    
    print(f"发现 {len(missing_items)} 个缺失内容")
    
    # 处理每个缺失项
    success = 0
    failed = 0
    
    for i, item in enumerate(missing_items[:50]):  # 先处理前50个
        grade = item.get('grade', 'unknown')
        subject = item.get('subject', 'unknown')
        topic = item.get('topic', '未知知识点')
        
        print(f"\n[{i+1}/{len(missing_items)}] 生成: {grade}-{subject}-{topic[:20]}...")
        
        # 确保目录存在
        subject_dir = ensure_dir_exists(grade, subject)
        
        # 生成内容
        content = generate_content(topic, grade, subject)
        
        if content:
            # 构建文件
            filename = f"{grade}-{subject}-{topic}.json"
            file_data = {
                "grade": grade,
                "subject": subject,
                "topic": topic,
                "content": content,
                "explanation": content,
                "keywords": [],
                "difficulty": "基础",
                "tags": [subject, grade]
            }
            
            file_path = subject_dir / filename
            file_path.write_text(json.dumps(file_data, ensure_ascii=False, indent=2), encoding='utf-8')
            success += 1
            print(f"  ✓ 已保存: {file_path.name}")
        else:
            failed += 1
            print(f"  ✗ 生成失败")
        
        # 限速：15 RPM（4秒间隔）
        time.sleep(4)
    
    print(f"\n完成: 成功{success}, 失败{failed}")
    
    # 重新统计
    total_missing = 0
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        target_dir = output_dir / grade / subject
        if not target_dir.exists():
            total_missing += 1
        else:
            topic = item.get('topic', '')
            if not (target_dir / f"{grade}-{subject}-{topic}.json").exists():
                total_missing += 1
    
    print(f"剩余缺失: {total_missing}个")

if __name__ == '__main__':
    main()