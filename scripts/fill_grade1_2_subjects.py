#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补全小学1-2年级音体美道内容
"""

import json
from pathlib import Path
import time
import urllib.request
import urllib.error
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
API_KEY = 'sk-IoSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'

# 科目提示词模板
SUBJECT_PROMPTS = {
    '音乐': """请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 包含乐曲欣赏、节奏练习、歌唱指导
2. 介绍音乐知识和文化背景
3. 语言生动有趣，适合小学生阅读
4. 字数不少于400字
5. 直接输出内容正文""",
    
    '美术': """请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 包含技法讲解、欣赏指导、实践建议
2. 介绍美术知识和文化背景
3. 语言生动有趣，适合小学生阅读
4. 字数不少于400字
5. 直接输出内容正文""",
    
    '体育': """请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 包含动作要领、练习方法、安全注意事项
2. 介绍体育知识和健康理念
3. 语言生动有趣，适合小学生阅读
4. 字数不少于400字
5. 直接输出内容正文""",
    
    '道德与法治': """请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 包含案例讲解、价值引导、行为建议
2. 联系生活实际，培养良好品德
3. 语言生动有趣，适合小学生阅读
4. 字数不少于400字
5. 直接输出内容正文"""
}

def generate_content(topic, grade, subject):
    """通过API生成内容"""
    prompt_template = SUBJECT_PROMPTS.get(subject, """请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。
要求：
1. 像教科书正文一样详细
2. 语言生动有趣，适合小学生阅读
3. 字数不少于400字
4. 直接输出内容正文""")
    
    prompt = prompt_template.format(grade=grade, subject=subject, topic=topic)
    
    payload = json.dumps({
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": "你是一个K12教育内容专家"},
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

def main():
    # 读取知识图谱
    kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))
    
    # 找出小学1-2年级缺失的音体美道内容
    missing = []
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        
        # 只处理小学1-2年级的音体美道
        if grade not in ['一年级上', '一年级下', '二年级上', '二年级下']:
            continue
        if subject not in ['音乐', '美术', '体育', '道德与法治']:
            continue
        
        # 检查是否存在
        target_dir = output_dir / grade / subject
        expected = f"{grade}-{subject}-{topic}.json"
        
        if not target_dir.exists() or not (target_dir / expected).exists():
            missing.append(item)
    
    print(f"发现 {len(missing)} 个缺失内容\n")
    
    # 按年级分组显示
    by_grade = defaultdict(list)
    for item in missing:
        by_grade[item.get('grade')].append(item)
    
    for grade in sorted(by_grade.keys()):
        items = by_grade[grade]
        subjects = defaultdict(int)
        for item in items:
            subjects[item.get('subject')] += 1
        print(f"{grade}: {len(items)}个")
        for subject, count in sorted(subjects.items()):
            print(f"  {subject}: {count}个")
    
    print("\n开始生成内容...")
    
    # 生成内容
    success = 0
    failed = 0
    
    for i, item in enumerate(missing):
        grade = item.get('grade', 'unknown')
        subject = item.get('subject', 'unknown')
        topic = item.get('topic', '未知')
        
        print(f"\n[{i+1}/{len(missing)}] {grade}-{subject}-{topic[:20]}...", end=" ")
        
        content = generate_content(topic, grade, subject)
        
        if content and len(content) >= 200:
            # 保存文件
            subject_dir = output_dir / grade / subject
            subject_dir.mkdir(parents=True, exist_ok=True)
            
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
            
            filename = f"{grade}-{subject}-{topic}.json"
            (subject_dir / filename).write_text(
                json.dumps(file_data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            success += 1
            print(f"✓ ({len(content)}字)")
        else:
            failed += 1
            print("✗")
        
        # 限速：15 RPM（4秒间隔）
        time.sleep(4)
        
        # 每10个显示进度
        if (i + 1) % 10 == 0:
            print(f"\n--- 进度: {i+1}/{len(missing)} ({(i+1)/len(missing)*100:.1f}%) ---")
    
    print(f"\n完成! 成功: {success}, 失败: {failed}")
    
    # 统计剩余缺失
    remaining = 0
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        
        if grade not in ['一年级上', '一年级下', '二年级上', '二年级下']:
            continue
        if subject not in ['音乐', '美术', '体育', '道德与法治']:
            continue
        
        target_dir = output_dir / grade / subject
        expected = f"{grade}-{subject}-{topic}.json"
        
        if not target_dir.exists() or not (target_dir / expected).exists():
            remaining += 1
    
    print(f"剩余缺失: {remaining}个")

if __name__ == '__main__':
    main()
