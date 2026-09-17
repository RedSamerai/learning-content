#!/usr/bin/env python3
"""批量生成缺失的explanation"""
import asyncio, aiohttp, json, time, os
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
        data = {"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400}
        try:
            async with session.post(f"{AGNES_BASE_URL}/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except:
            return None

def gen_pil_image(topic_name, grade, subject):
    from PIL import Image, ImageDraw, ImageFont
    w, h = 1024, 768
    img = Image.new('RGB', (w, h), color='#F5F7FA')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
        title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
    except:
        font = ImageFont.load_default()
        title_font = font
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    # 顶部标题栏
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50')
    grade_text = grade if grade else "学习内容"
    draw.text((w//2, 85), f"{grade_text} · {topic_name}", font=title_font, fill='white', anchor='mm')
    
    # 根据科目选择图案
    if subject == 'math':
        # 数学：几何图形
        shapes = [('circle', '#FF6B6B'), ('rect', '#4ECDC4'), ('triangle', '#45B7D1')]
        positions = [(200, 350), (512, 350), (824, 350)]
        for i, ((shape, color), (x, y)) in enumerate(zip(shapes, positions)):
            if shape == 'circle':
                draw.ellipse([x-80, y-80, x+80, y+80], fill=color)
            elif shape == 'rect':
                draw.rectangle([x-80, y-80, x+80, y+80], fill=color)
            elif shape == 'triangle':
                draw.polygon([(x, y-80), (x-80, y+80), (x+80, y+80)], fill=color)
        draw.text((w//2, 550), "数学学习", font=font, fill='#2C3E50', anchor='mm')
    elif subject in ['history', 'geography']:
        icons = ['📜', '🗺️', '🏛️', '⚔️']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "历史文化", font=font, fill='#2C3E50', anchor='mm')
    elif subject in ['physics', 'chemistry', 'biology']:
        icons = ['⚡', '🧪', '🧬', '🔬']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "科学探索", font=font, fill='#2C3E50', anchor='mm')
    elif subject == 'chinese':
        icons = ['📖', '✏️', '🎨', '🎵']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "语文学习", font=font, fill='#2C3E50', anchor='mm')
    else:
        icons = ['📚', '🔬', '🌍', '🎨']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "学习内容", font=font, fill='#2C3E50', anchor='mm')
    
    return img

async def main():
    # 找出需要修复的文件
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            if not data.get('explanation') or len(data.get('explanation', '')) < 10:
                tasks.append(p)
        except:
            pass
    
    print(f"🔧 需要修复: {len(tasks)}个文件\n")
    
    semaphore = asyncio.Semaphore(2)
    completed = 0
    
    async def fix_one(p):
        nonlocal completed
        async with semaphore:
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                topic_name = data.get('name', '')
                grade = data.get('grade', data.get('age_group', ''))
                subject = data.get('subject', '')
                focus = data.get('focus', '')
                
                if not topic_name:
                    return True
                
                # 生成explanation
                prompt = f"为{grade}学生讲解'{topic_name}'，{focus}。用简单易懂的语言，150字以内。"
                explanation = await call_agnes(prompt)
                
                if explanation:
                    data['explanation'] = explanation
                
                # 检查图片
                image_file = data.get('image', '')
                image_path = p.parent / image_file
                if not image_path.exists() or image_path.stat().st_size == 0:
                    img = gen_pil_image(topic_name, grade, subject)
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(image_path)
                
                # 保存
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                completed += 1
                if completed % 20 == 0:
                    print(f"  已完成 {completed}/{len(tasks)}")
                return True
            except Exception as e:
                return False
    
    # 分批处理
    batch_size = 30
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        await asyncio.gather(*[fix_one(p) for p in batch])
    
    print(f"\n✅ 完成修复: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())