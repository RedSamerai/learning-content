#!/usr/bin/env python3
"""批量生成缺失的图片"""
import asyncio, aiohttp, json, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REQUEST_DELAY = 4.5
last_request_time = 0

async def call_agnes(prompt, model="agnes-image-2.1-flash"):
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": "Bearer sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk", "Content-Type": "application/json"}
        data = {"model": model, "prompt": prompt, "size": "1024x768"}
        try:
            async with session.post("https://apihub.agnes-ai.com/v1/images/generations", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    result = await resp.json()
                    if result.get('data'):
                        url = result['data'][0].get('url')
                        if url:
                            async with session.get(url) as img_resp:
                                return await img_resp.read()
        except Exception as e:
            print(f"    API错误: {e}")
        return None

def gen_pil_image(topic_name, grade, subject):
    """用PIL生成图片"""
    w, h = 1024, 768
    img = Image.new('RGB', (w, h), color='#F5F7FA')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
        title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
    except:
        font = ImageFont.load_default()
        title_font = font
    
    # 顶部标题栏
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50')
    grade_text = grade if grade else "学习内容"
    draw.text((w//2, 85), f"{grade_text} · {topic_name}", font=title_font, fill='white', anchor='mm')
    
    # 根据科目选择图案
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    if subject == 'math':
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
    elif subject in ['morality', 'health', 'social']:
        icons = ['❤️', '🤝', '🌟', '💪']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "品德与健康", font=font, fill='#2C3E50', anchor='mm')
    else:
        icons = ['📚', '🔬', '🌍', '🎨']
        for i, ic in enumerate(icons):
            x = 200 + i * 200
            draw.text((x, 300), ic, font=title_font, fill='#2C3E50')
        draw.text((w//2, 550), "学习内容", font=font, fill='#2C3E50', anchor='mm')
    
    return img

async def fix_one(p):
    """修复单个知识点的图片"""
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        topic_name = data.get('name', '')
        grade = data.get('grade', data.get('age_group', ''))
        subject = data.get('subject', '')
        
        if not topic_name:
            return False
        
        # 生成图片
        img = gen_pil_image(topic_name, grade, subject)
        
        # 保存
        img_path = p.parent / "image.png"
        img_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(img_path)
        
        # 更新JSON
        data['image'] = "image.png"
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False

async def main():
    # 找出缺失图片的文件
    tasks = []
    for p in Path('output').rglob('*.json'):
        if p.parent.name in ['image', 'audio']:
            continue
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            img_file = data.get('image', '')
            img_path = p.parent / img_file
            if not img_path.exists() or img_path.stat().st_size == 0:
                tasks.append(p)
        except:
            pass
    
    print(f"🎨 需要生成图片: {len(tasks)}个文件\n")
    
    semaphore = asyncio.Semaphore(1)
    completed = 0
    
    for i, p in enumerate(tasks):
        async with semaphore:
            topic_name = json.load(open(p, 'r', encoding='utf-8')).get('name', '')
            grade = json.load(open(p, 'r', encoding='utf-8')).get('grade', json.load(open(p, 'r', encoding='utf-8')).get('age_group', ''))
            subject = json.load(open(p, 'r', encoding='utf-8')).get('subject', '')
            
            if (i + 1) % 10 == 0:
                print(f"\n进度: [{i+1}/{len(tasks)}] 已完成 {completed} 个\n")
            
            print(f"[{i+1}/{len(tasks)}] {topic_name} ({grade}) [{subject}]", end=" ", flush=True)
            if await fix_one(p):
                print("✅")
                completed += 1
            else:
                print("❌")
            
            # 避免RPM超限
            await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n✅ 完成: {completed}/{len(tasks)}")

if __name__ == "__main__":
    asyncio.run(main())