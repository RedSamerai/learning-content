#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补全小学1-2年级音体美道"""

import json, time, urllib.request
from pathlib import Path

base = Path('D:/WorkBuddy/learning-app-research/learning-content')
output_dir = base / 'output'
API_KEY = 'sk-IoSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk'
API_URL = 'https://apihub.agnes-ai.com/v1/chat/completions'

kg = json.loads((base / 'knowledge_graph_complete.json').read_text(encoding='utf-8'))

# 科目模板
TEMPLATES = {
    '音乐': '请编写音乐课教学内容，包含乐曲欣赏、节奏练习，适合小学生',
    '美术': '请编写美术课教学内容，包含技法讲解、欣赏指导，适合小学生',
    '体育': '请编写体育课教学内容，包含动作要领、练习方法，适合小学生',
    '道德与法治': '请编写道德与法治课教学内容，包含案例讲解、价值引导，适合小学生'
}

def gen(topic, grade, subject):
    prompt = f'请为{grade}的{subject}课程编写关于"{topic}"的详细教学内容。要求：像教科书正文一样详细，包含生活例子，语言生动有趣，适合小学生阅读，字数不少于400字。直接输出内容正文。'
    payload = json.dumps({"model": "agnes-2.5-flash", "messages": [{"role": "system", "content": "你是K12教育专家"}, {"role": "user", "content": prompt}], "max_tokens": 1500}).encode()
    req = urllib.request.Request(API_URL, data=payload, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {API_KEY}'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())['choices'][0]['message']['content']
    except:
        return None

missing = [(i['grade'], i['subject'], i['topic']) for i in kg if i['grade'] in ['一年级上','一年级下','二年级上','二年级下'] and i['subject'] in ['音乐','美术','体育','道德与法治']]
missing = [(g,s,t) for g,s,t in missing if not (output_dir/g/s/f'{g}-{s}-{t}.json').exists()]

print(f'开始处理{len(missing)}个缺失内容...\n')
success = 0
for i,(g,s,t) in enumerate(missing):
    print(f'[{i+1}/{len(missing)}] {g}-{s}-{t[:20]}...', end=' ')
    c = gen(t, g, s)
    if c and len(c) >= 200:
        (output_dir/g/s).mkdir(parents=True, exist_ok=True)
        (output_dir/g/s/f'{g}-{s}-{t}.json').write_text(json.dumps({'grade':g,'subject':s,'topic':t,'content':c,'explanation':c}, ensure_ascii=False, indent=2), encoding='utf-8')
        success += 1
        print(f'✓ ({len(c)}字)')
    else:
        print('✗')
    time.sleep(3)
    if (i+1) % 10 == 0: print(f'\n--- 进度: {i+1}/{len(missing)} ---')

print(f'\n完成! 成功:{success}, 失败:{len(missing)-success}')
