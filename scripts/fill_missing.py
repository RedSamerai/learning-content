#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补全缺失知识点内容"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
API_KEY = 'sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'

def get_missing():
    """获取缺失的知识点"""
    kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))
    missing = []
    for item in kg:
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        if not topic:
            continue
        target = output_dir / grade / subject / f'{grade}-{subject}-{topic.replace("/", "-")}.json'
        if not target.exists():
            missing.append(item)
    return missing

def generate_content(topic, grade, subject):
    """通过API生成内容"""
    prompts = {
        '健康': f'请为幼儿园健康课程编写关于"{topic}"的详细教学内容。包括健康知识介绍、生活习惯培养、安全常识等。语言生动有趣，适合幼儿阅读，字数不少于300字。',
        '语言': f'请为幼儿园语言课程编写关于"{topic}"的详细教学内容。包括词语认知、简单句子、故事讲述等。语言生动有趣，字数不少于300字。',
        '社会': f'请为幼儿园社会课程编写关于"{topic}"的详细教学内容。包括社会认知、人际交往、规则意识等。语言生动有趣，字数不少于300字。',
        '艺术': f'请为幼儿园艺术课程编写关于"{topic}"的详细教学内容。包括美术、音乐、手工等内容。语言生动有趣，字数不少于300字。',
        '英语': f'请为{grade.replace("一年级", "小学一年级").replace("二年级", "小学二年级")}英语课程编写关于"{topic}"的详细教学内容。包含词汇、语法或句型讲解，例句练习等。字数不少于400字。',
        '语文': f'请为{grade}语文课程编写关于"{topic}"的详细教学内容。包括课文讲解、字词学习、阅读理解等。字数不少于400字。',
        '数学': f'请为{grade}数学课程编写关于"{topic}"的详细教学内容。包括概念讲解、例题解析、练习题等。字数不少于400字。',
        '物理': f'请为{grade}物理课程编写关于"{topic}"的详细教学内容。包括概念解释、实验说明、公式推导、例题解析等。字数不少于500字。',
        '化学': f'请为{grade}化学课程编写关于"{topic}"的详细教学内容。包括概念解释、化学反应、实验说明等。字数不少于500字。',
        '科学': f'请为{grade}科学课程编写关于"{topic}"的详细教学内容。包括科学概念、实验探究、自然现象解释等。字数不少于400字。',
        '历史': f'请为{grade}历史课程编写关于"{topic}"的详细教学内容。包括历史背景、事件经过、影响意义等。字数不少于400字。',
        '道德与法治': f'请为{grade}道德与法治课程编写关于"{topic}"的详细教学内容。包括案例分析、价值引导、行为建议等。字数不少于400字。',
        '体育': f'请为{grade}体育课程编写关于"{topic}"的详细教学内容。包括动作要领、练习方法、安全注意事项等。字数不少于300字。',
        '美术': f'请为{grade}美术课程编写关于"{topic}"的详细教学内容。包括技法讲解、欣赏指导、实践建议等。字数不少于300字。',
        '音乐': f'请为{grade}音乐课程编写关于"{topic}"的详细教学内容。包括乐曲欣赏、节奏练习、歌唱指导等。字数不少于300字。',
    }
    
    prompt = prompts.get(subject, f'请为{grade}{subject}课程编写关于"{topic}"的详细教学内容。字数不少于400字。')
    
    payload = json.dumps({
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": "你是专业的K12教育内容创作者"},
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
    missing = get_missing()
    print(f"发现 {len(missing)} 个缺失知识点\n")
    
    success = 0
    failed = 0
    
    for i, item in enumerate(missing):
        grade = item.get('grade', '')
        subject = item.get('subject', '')
        topic = item.get('topic', '')
        
        print(f"[{i+1}/{len(missing)}] {grade}-{subject}-{topic[:20]}...", end=" ")
        
        content = generate_content(topic, grade, subject)
        
        if content and len(content) >= 200:
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
            
            filename = f'{grade}-{subject}-{topic.replace("/", "-")}.json'
            (subject_dir / filename).write_text(
                json.dumps(file_data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            success += 1
            print(f"✓ ({len(content)}字)")
        else:
            failed += 1
            print("✗")
        
        time.sleep(3)  # 限速
    
    print(f"\n完成! 成功: {success}, 失败: {failed}")

if __name__ == '__main__':
    main()
