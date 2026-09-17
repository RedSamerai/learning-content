#!/usr/bin/env python3
"""
K12内容批量生成脚本
- 幼小衔接：汉语拼音、识字、阅读
- 小学一年级：数学、科学、道德与法治
"""
import asyncio
import aiohttp
import json
import os
import edge_tts
from PIL import Image, ImageDraw
from datetime import datetime

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 加载知识图谱
def load_knowledge_graph():
    with open('knowledge_graph_k12.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 生成文本内容
async def generate_text(topic):
    grade = topic.get('grade', '')
    prompt = f"""请为{grade}学生编写{topic['name']}的教学内容：
要求：
1. 用简单易懂的语言讲解核心概念
2. 举例要贴近儿童生活实际
3. 语言生动活泼，适合朗读
4. 生成3道选择题（附答案和解析）
5. 控制在200字以内

输出JSON格式：
{{"concept": "一句话核心概念", "explanation": "详细讲解内容", "questions": [{{"question": "...", "options": ["A...","B...","C...","D..."], "answer": "A", "explanation": "..."}}]}}"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return json.loads(data["choices"][0]["message"]["content"])
            else:
                print(f"❌ API错误 {response.status}")
                return None

# 生成图片
async def generate_image(topic):
    """根据主题生成适合的图片"""
    topic_id = topic['topic_id']
    
    # 数学类图片用代码生成（避免幻觉）
    if topic_id.startswith('math_py_'):
        return generate_math_image(topic_id)
    
    # 其他类别用AI生成
    image_prompts = {
        'py_b_d': '儿童教育插画，声母b和d的卡通形象，圆形加竖线，白色背景，彩色',
        'py_a_o_e': '儿童教育插画，韵母a o e的卡通形象，戴着光环，白色背景，可爱风格',
        'sci_py_plant_1': '儿童观察校园植物的场景，小朋友在花园里看花和树，卡通风格',
        'sci_py_water_1': '儿童教育插画，展示水的特征：透明、无色、流动，白色背景'
    }
    
    prompt = image_prompts.get(topic_id, f'儿童教育插画，主题：{topic["name"]}')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
            json={"model": "agnes-image-2.1-flash", "prompt": prompt, "size": "1024x512", "n": 1}
        ) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['data'][0].get('url', '')
                if image_url:
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            return await img_response.read()
    return None

def generate_math_image(topic_id):
    """生成数学图片（代码绘制，确保准确）"""
    img = Image.new('RGB', (1200, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    font = ImageFont.truetype("arial.ttf", 80)
    
    if topic_id == 'math_py_count_10':
        # 1-10
        for i in range(1, 11):
            x = (i-1) * 110 + 50
            draw.text((x, 80), str(i), fill='#333333', font=font)
    elif topic_id == 'math_py_count_20':
        # 1-20 两行
        for i in range(1, 21):
            x = (i-1) % 10 * 115 + 50
            y = 60 if i <= 10 else 180
            draw.text((x, y), str(i), fill='#333333', font=font)
    elif topic_id == 'math_py_add_5':
        draw.text((350, 80), "3 + 2 = 5", fill='#FF6B6B', font=font)
    elif topic_id == 'math_py_sub_5':
        draw.text((350, 80), "5 - 2 = 3", fill='#4ECDC4', font=font)
    elif topic_id == 'math_py_compare':
        draw.text((300, 80), "3 < 5  或  7 > 2", fill='#FFE66D', font=font)
    elif topic_id == 'math_py_clock_1':
        # 画一个钟面
        draw.ellipse([400, 50, 700, 350], outline='#333333', width=3)
        draw.text((530, 200), "3:00", fill='#333333', font=font)
    elif topic_id == 'math_py_shape_1':
        # 长方体（实色填充，无黑框）
        def draw_cuboid(cx, cy, w, h, colors):
            draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], fill=colors[0])
            offset = w // 4
            draw.polygon([(cx-w//2, cy-h//2), (cx-w//2+offset, cy-h//2-offset//2),
                         (cx+w//2+offset, cy-h//2-offset//2), (cx+w//2, cy-h//2)], fill=colors[1])
            draw.polygon([(cx+w//2, cy-h//2), (cx+w//2+offset, cy-h//2-offset//2),
                         (cx+w//2+offset, cy+h//2-offset//2), (cx+w//2, cy+h//2)], fill=colors[2])
        draw_cuboid(200, 200, 150, 120, ['#FF6B6B', '#EE5A5A', '#DD4444'])
        draw_cuboid(500, 180, 120, 150, ['#4ECDC4', '#3DBFB6', '#2CB0A7'])
        draw_cuboid(800, 200, 100, 100, ['#FFE66D', '#F5D74E', '#E8C830'])
        draw.text((180, 350), "盒子", fill='#333333')
        draw.text((480, 350), "书本", fill='#333333')
        draw.text((780, 350), "砖块", fill='#333333')
    else:
        # 默认显示主题名称
        draw.text((300, 100), topic['name'], fill='#333333', font=font)
    
    return img

# 生成音频
async def generate_audio(topic_id, content, subject='chinese', grade='幼小衔接', voice="zh-CN-XiaoxiaoNeural"):
    concept_path = f"output/{subject.lower()}/{grade}/{topic_id}/audio_concept.mp3"
    explanation_path = f"output/{subject.lower()}/{grade}/{topic_id}/audio_explanation.mp3"
    
    os.makedirs(os.path.dirname(concept_path), exist_ok=True)
    
    communicate = edge_tts.Communicate(content.get('concept', ''), voice)
    await communicate.save(concept_path)
    
    communicate = edge_tts.Communicate(content.get('explanation', ''), voice)
    await communicate.save(explanation_path)

async def process_topic(topic):
    print(f"\n📚 {topic['name']} ({topic['grade']})")
    
    # 生成文本
    content = await generate_text(topic)
    if not content:
        print("❌ 文本生成失败")
        return False
    
    # 生成图片
    img_data = await generate_image(topic)
    if img_data:
        img_path = f"output/{topic['subject'].lower()}/{topic['grade']}/{topic['topic_id']}/image.png"
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        with open(img_path, 'wb') as f:
            f.write(img_data)
    else:
        # 使用代码生成的图片
        img = generate_math_image(topic['topic_id'])
        img_path = f"output/{topic['subject'].lower()}/{topic['grade']}/{topic['topic_id']}/image.png"
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        img.save(img_path)
    
    # 生成音频
    await generate_audio(topic['topic_id'], content, topic['subject'], topic['grade'])
    
    # 保存JSON
    output_json = {
        "topic_id": topic['topic_id'],
        "name": topic['name'],
        "subject": topic['subject'],
        "grade": topic['grade'],
        "content": content,
        "created_at": datetime.now().isoformat()
    }
    
    json_path = f"output/{topic['subject'].lower()}/{topic['grade']}/{topic['topic_id']}.json"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成")
    return True

async def main():
    print("🚀 开始生成K12内容\n")
    
    graph = load_knowledge_graph()
    topics = []
    
    for subject in graph['subjects']:
        for area in subject.get('areas', []):
            for obj in area.get('objectives', []):
                for topic in obj.get('topics', []):
                    topic['subject'] = subject['subject_id']
                    topics.append(topic)
    
    print(f"共 {len(topics)} 个知识点待生成\n")
    
    completed = 0
    failed = 0
    
    for topic in topics:
        success = await process_topic(topic)
        if success:
            completed += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"📊 生成完成")
    print(f"   成功: {completed}")
    print(f"   失败: {failed}")
    print(f"{'='*50}")

if __name__ == '__main__':
    from PIL import ImageFont
    asyncio.run(main())
