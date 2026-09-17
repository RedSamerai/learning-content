#!/usr/bin/env python3
"""快速修复缺失的explanation"""
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
    
    if not data.get('explanation'):
        explanation = await call_agnes(f"为{grade}学生讲解'{topic_name}'，{data.get('focus', '')}。用简单易懂的语言，150字以内。")
        if explanation:
            data['explanation'] = explanation
    
    with open(json_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return explanation is not None

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
    
    for i, p in enumerate(tasks[:30]):  # 先修复前30个
        try:
            data = json.load(open(p))
            topic_name = data.get('name', '')
            grade = data.get('grade', '')
            if not topic_name or not grade:
                continue
            print(f"[{i+1}/{min(30, len(tasks))}] 修复 {topic_name} ({grade})...", end=" ", flush=True)
            await fix_json(p)
            print("✅")
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"跳过: {e}")
    
    print(f"\n✅ 已修复前30个")

if __name__ == "__main__":
    asyncio.run(main())