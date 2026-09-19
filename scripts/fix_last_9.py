#!/usr/bin/env python3
"""补全缺失的9个知识点，仅对3-9岁生成音频"""
import json
import requests
import time
from pathlib import Path

API_KEY = 'sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
BASE_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'
base = Path('D:/WorkBuddy/learning-app-research/learning-content/output')

# 加载知识图谱
with open('D:/WorkBuddy/learning-app-research/learning-content/knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)

# 缺失ID列表
missing_ids = [
    '英语七年级上2697', '英语七年级下2771',
    '数学九年级下2011', '化学九年级下2573', '化学九年级下2501',
    '英语九年级全一册2999', '历史八年级上3095',
    '数学八年级下1872', '历史八年级下3146'
]

# 音频范围：仅幼儿园、幼小衔接、小学1-3年级
AUDIO_GRADES = {'幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下'}

def generate_content(topic):
    """使用AGNES API生成详细教学内容"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    prompt = f"""请为"{topic.get('title', topic['id'])}"生成详细的教科书式教学内容。

要求：
1. 内容要详细完整，像教科书正文一样，不是提纲式
2. 包含生活实例、公式定理、常见误区提醒
3. 字数500字以上
4. 使用Markdown格式

请按以下结构输出：
# {topic.get('title', topic['id'])}

## 知识点介绍
（介绍这个知识点的重要性和基本含义）

## 详细讲解
### 核心概念
（详细解释核心概念）

### 生活实例
（举2-3个生活中的例子）

### 公式/定理
（列出相关公式或定理）

### 解题方法
（说明解题步骤和方法）

### 常见误区
（列出学生常犯的错误）

## 练习题
（出5道练习题，含答案）
"""
    
    data = {
        'model': 'agnes-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"生成失败: {e}")
        return None

def generate_audio(topic_id, grade, subject):
    """使用edge-tts生成音频（仅3-9岁）"""
    try:
        import edge_tts
        import asyncio
        
        # 根据学段选择音色
        if grade in {'幼儿园', '幼小衔接'}:
            voice = 'zh-CN-XiaoyiNeural'
        else:
            voice = 'zh-CN-XiaoxiaoNeural'
        
        # 准备文本（提取内容的前500字）
        text = f"{topic_id}的学习内容..."
        
        # 异步生成
        communicate = edge_tts.Communicate(text, voice)
        output_path = base / grade / subject / f"{topic_id}.mp3"
        asyncio.run(communicate.save(str(output_path)))
        return True
    except Exception as e:
        print(f"音频生成失败: {e}")
        return False

def save_topic(topic, content, has_audio=False):
    """保存知识点到JSON文件"""
    grade = topic['grade']
    subject = topic['subject']
    
    # 创建目录
    dir_path = base / grade / subject
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # 创建子目录
    topic_dir = dir_path / topic['id']
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON
    data = {
        'id': topic['id'],
        'subject': subject,
        'grade': grade,
        'content': content,
        'audio_url': f"{topic['id']}.mp3" if has_audio else None,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    file_path = topic_dir / f"{topic['id']}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return file_path

print("=" * 50)
print("开始补全缺失的9个知识点")
print("=" * 50)

success_count = 0
audio_count = 0

for i, mid in enumerate(missing_ids, 1):
    # 查找对应的知识点信息
    topic = None
    for t in all_topics:
        if t['id'] == mid:
            topic = t
            break
    
    if not topic:
        print(f"[{i}/9] 未找到知识点: {mid}")
        continue
    
    grade = topic.get('grade', '未知')
    subject = topic.get('subject', '未知')
    
    print(f"\n[{i}/9] 正在处理: {mid} ({grade}-{subject})")
    
    # 生成内容
    content = generate_content(topic)
    if not content:
        print(f"  跳过: 内容生成失败")
        continue
    
    # 判断是否需要音频
    has_audio = grade in AUDIO_GRADES
    
    # 保存
    file_path = save_topic(topic, content, has_audio)
    print(f"  已保存: {file_path}")
    success_count += 1
    
    # 生成音频（仅3-9岁）
    if has_audio:
        print(f"  正在生成音频...")
        if generate_audio(mid, grade, subject):
            audio_count += 1
            print(f"  音频已生成")
    
    # 避免RPM超限
    time.sleep(4)

print("\n" + "=" * 50)
print(f"补全完成!")
print(f"成功: {success_count}/9")
print(f"音频: {audio_count}个（仅3-9岁）")
print("=" * 50)
