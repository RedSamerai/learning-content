#!/usr/bin/env python3
"""修复缺失的文本说明"""
import asyncio, aiohttp, json, time
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
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
        data = {"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
        try:
            async with session.post("https://apihub.agnes-ai.com/v1/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

async def fix_one(p):
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topic_name = data.get('name', '')
        grade = data.get('grade', data.get('age_group', ''))
        focus = data.get('focus', '')
        
        if not topic_name:
            return False
        
        # 生成explanation
        prompt = f"为{grade}学生讲解'{topic_name}'，{focus}。用简单易懂的语言，150字以内。"
        explanation = await call_agnes(prompt)
        
        if explanation:
            data['explanation'] = explanation
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        return False
    except Exception as e:
        print(f"    Error: {e}")
        return False

async def main():
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']: continue
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            if not data.get('explanation') or len(data.get('explanation', '')) < 10:
                tasks.append(p)
        except: pass
    
    print(f"📝 需要修复文本: {len(tasks)}个文件\n")
    
    completed = 0
    for i, p in enumerate(tasks):
        topic_name = json.load(open(p, 'r', encoding='utf-8')).get('name', '')
        grade = json.load(open(p, 'r', encoding='utf-8')).get('grade', json.load(open(p, 'r', encoding='utf-8')).get('age_group', ''))
        
        print(f"[{i+1}/{len(tasks)}] {topic_name} ({grade})", end=" ", flush=True)
        if await fix_one(p):
            print("✅")
            completed += 1
        else:
            print("❌")
        
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())