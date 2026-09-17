#!/usr/bin/env python3
"""批量修复所有缺失的explanation"""
import asyncio, aiohttp, json, time
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"
REQUEST_DELAY = 4.5

last_request_time = 0

async def call_agnes(prompt):
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
        try:
            async with session.post(f"{AGNES_BASE_URL}/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

async def fix_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    topic_name = data.get('name', '')
    grade = data.get('grade', '')
    subject = data.get('subject', '')
    focus = data.get('focus', '')
    
    if not data.get('explanation'):
        explanation = await call_agnes(f"为{grade}学生讲解'{topic_name}'，{focus}。用简单易懂的语言，150字以内。")
        if explanation:
            data['explanation'] = explanation
        return explanation is not None
    return True

async def main():
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        try:
            data = json.load(open(p))
            if not data.get('explanation'):
                tasks.append(p)
        except:
            pass
    
    print(f"🔧 需要修复: {len(tasks)}个文件\n")
    
    completed = 0
    for i, p in enumerate(tasks):
        try:
            data = json.load(open(p))
            topic_name = data.get('name', '')
            grade = data.get('grade', '')
            if not topic_name or not grade:
                continue
            
            if (i + 1) % 30 == 0:
                print(f"\n[{i+1}/{len(tasks)}] 正在处理...")
            
            success = await fix_json(p)
            if success:
                completed += 1
        except Exception as e:
            pass
    
    print(f"\n✅ 完成修复: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())