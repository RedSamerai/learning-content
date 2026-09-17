#!/usr/bin/env python3
"""生成补充知识点内容 - 按年龄排序入库"""
import asyncio, aiohttp, json, time, os
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
REQUEST_DELAY = 4.5
last_request_time = 0

# 年龄段排序
AGE_ORDER = [
    "幼儿园(3-4岁)", "幼儿园(4-5岁)", "幼儿园(5-6岁)",
    "幼小衔接",
    "一年级上", "一年级下",
    "二年级上", "二年级下",
    "三年级上", "三年级下",
    "四年级上", "四年级下",
    "五年级上", "五年级下",
    "六年级上", "六年级下",
    "初中"
]

def get_age_sort_key(item):
    age = item.get('age_group', item.get('grade', ''))
    try:
        return AGE_ORDER.index(age)
    except ValueError:
        return len(AGE_ORDER)

async def call_agnes(prompt, model="agnes-2.5-flash"):
    global last_request_time
    now = time.time()
    elapsed = now - last_request_time
    if elapsed < REQUEST_DELAY:
        await asyncio.sleep(REQUEST_DELAY - elapsed)
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"}
        data = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
        try:
            async with session.post("https://apihub.agnes-ai.com/v1/chat/completions", headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    last_request_time = time.time()
                    return (await resp.json())['choices'][0]['message']['content']
                return None
        except Exception as e:
            print(f"    API错误: {e}")
            return None

async def generate_image(topic_name, grade, subject):
    """生成图片"""
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
    
    # 顶部标题栏
    draw.rectangle([50, 50, w-50, 150], fill='#2C3E50')
    grade_text = grade if grade else "学习内容"
    draw.text((w//2, 85), f"{grade_text} · {topic_name}", font=title_font, fill='white', anchor='mm')
    
    # 根据科目选择图案
    subject_colors = {
        'math': '#FF6B6B', 'chinese': '#4ECDC4', 'english': '#45B7D1',
        'science': '#96CEB4', 'morality': '#FFEAA7', 'physics': '#DDA0DD',
        'chemistry': '#98D8C8', 'biology': '#F7DC6F', 'history': '#BB8FCE',
        'geography': '#85C1E9'
    }
    color = subject_colors.get(subject, '#BDC3C7')
    
    # 绘制主题图案
    center_y = 450
    icons = {'math': '🔢', 'chinese': '📖', 'english': '🔤', 'science': '🔬', 
             'morality': '❤️', 'physics': '⚡', 'chemistry': '🧪', 'biology': '🧬',
             'history': '📜', 'geography': '🌍'}
    icon = icons.get(subject, '📚')
    draw.text((w//2, center_y), icon, font=title_font, fill=color)
    
    # 装饰元素
    shapes = [
        (200, 300, 300, 400, '#FF6B6B'),
        (700, 300, 800, 400, '#4ECDC4'),
        (200, 550, 300, 650, '#45B7D1'),
        (700, 550, 800, 650, '#96CEB4'),
    ]
    for x1, y1, x2, y2, c in shapes:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=20, fill=c)
    
    return img

async def generate_audio(text, age_group, voice=None):
    """生成音频"""
    # 根据年龄段选择音色
    if voice is None:
        if age_group in ["幼儿园(3-4岁)", "幼儿园(4-5岁)", "幼儿园(5-6岁)", "幼小衔接"]:
            voice = "zh-CN-XiaoyiNeural"  # 温柔女声
        else:
            voice = "zh-CN-XiaoxiaoNeural"  # 标准女声
    
    url = f"https://api.xtts-api.com/api/tts?text={text}&voice={voice}&speed=0.9"
    return url

async def create_topic_content(topic):
    """为单个知识点创建内容"""
    topic_id = topic['topic_id']
    name = topic['name']
    grade = topic.get('age_group', topic.get('grade', ''))
    subject = topic.get('subject', '')
    focus = topic.get('focus', '')
    
    # 确定输出目录
    age_dir = grade.split('(')[0] if '(' in grade else grade
    subject_dir = {'math': 'math', 'chinese': 'chinese', 'english': 'english', 
                   'science': 'science', 'morality': 'morality', 'physics': 'physics',
                   'chemistry': 'chemistry', 'biology': 'biology', 'history': 'history',
                   'geography': 'geography'}.get(subject, subject.lower())
    
    dir_path = Path(f'output/{age_dir}/{topic_id}')
    dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[{topic_id}] {name} ({grade}) [{subject}]", end=" ", flush=True)
    
    # 生成explanation
    prompt = f"为{grade}学生讲解'{name}'，{focus}。用简单易懂的语言，150字以内。"
    explanation = await call_agnes(prompt)
    
    if not explanation:
        print("❌ 生成失败")
        return False
    
    # 生成示例题目
    questions = []
    if subject in ['math', 'chinese', 'english']:
        q_prompt = f"为'{name}'设计3道练习题，{focus}。格式：题目+答案。"
        questions_text = await call_agnes(q_prompt)
        if questions_text:
            lines = [l.strip() for l in questions_text.split('\n') if l.strip()]
            for line in lines[:6]:
                if any(k in line for k in ['1.', '2.', '3.', 'A)', 'B)', 'C)', '答案', '解析']):
                    questions.append(line)
    
    # 创建JSON
    content = {
        "id": topic_id,
        "name": name,
        "grade": grade,
        "age_group": grade,
        "subject": subject,
        "focus": focus,
        "explanation": explanation,
        "questions": "\n".join(questions) if questions else "",
        "image": "image.png",
        "audio": "audio.mp3"
    }
    
    # 保存JSON
    json_path = dir_path / f"{topic_id}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    # 生成图片
    img = await generate_image(name, grade, subject)
    img_path = dir_path / "image.png"
    img.save(img_path)
    
    # 生成音频
    audio_text = f"{name}。{explanation}"
    # 音频生成省略，使用占位符
    
    print("✅")
    return True

async def main():
    # 加载知识图谱
    with open('knowledge_graph_supplementary.json', 'r', encoding='utf-8') as f:
        kg = json.load(f)
    
    topics = sorted(kg['topics'], key=get_age_sort_key)
    
    print(f"📚 开始生成补充内容: {len(topics)}个知识点\n")
    print(f"⏱️ 预计时间: {len(topics) * REQUEST_DELAY / 60:.1f} 分钟\n")
    
    completed = 0
    for i, topic in enumerate(topics):
        if (i + 1) % 10 == 0:
            print(f"\n进度: [{i+1}/{len(topics)}] 已完成 {completed} 个\n")
        
        if await create_topic_content(topic):
            completed += 1
        
        # 避免RPM超限
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n✅ 完成: {completed}/{len(topics)}")
    
    # 更新主知识图谱
    with open('knowledge_graph_k12_full.json', 'r', encoding='utf-8') as f:
        main_kg = json.load(f)
    
    main_kg['topics'].extend(topics)
    main_kg['statistics']['total_topics'] = len(main_kg['topics'])
    
    with open('knowledge_graph_k12_full.json', 'w', encoding='utf-8') as f:
        json.dump(main_kg, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 已更新主知识图谱")

if __name__ == "__main__":
    asyncio.run(main())