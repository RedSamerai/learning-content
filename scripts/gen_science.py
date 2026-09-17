#!/usr/bin/env python3
"""生成科学和道德与法治知识点"""
import asyncio, aiohttp, json, os, edge_tts
from PIL import Image, ImageDraw
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

SCIENCE_TOPICS = [
    ("science", "一年级上", "sci_py_plant_1", "观察校园里的植物"),
    ("science", "一年级上", "sci_py_animal_1", "认识常见的动物"),
    ("science", "二年级上", "sci_py_plant_need", "植物生长需要什么"),
    ("science", "一年级上", "sci_py_water_1", "水的特征"),
    ("science", "一年级上", "sci_py_air_1", "空气的特点"),
    ("science", "二年级上", "sci_py_hard_soft", "软硬比较"),
    ("science", "二年级上", "sci_py_float_sink", "浮与沉"),
    ("science", "一年级上", "sci_py_weather_1", "认识天气"),
    ("science", "一年级下", "sci_py_season_1", "四季的变化"),
    ("morality", "一年级上", "mor_py_good habit_1", "早睡早起"),
    ("morality", "一年级上", "mor_py_clean_1", "讲卫生勤洗手"),
]

async def gen(topic):
    subj, grade, tid, name = topic
    print(f"\n📚 {name}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{AGNES_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": f"请编写{name}的教学内容"}], "response_format": {"type": "json_object"}}) as r:
                if r.status != 200:
                    return False
                data = await r.json()
                content = json.loads(data["choices"][0]["message"]["content"])
            
            dir_path = f"output/{subj}/{grade}/{tid}"
            os.makedirs(dir_path, exist_ok=True)
            
            img = Image.new('RGB', (800, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((250, 80), name, fill='#333333')
            img.save(f"{dir_path}/image.png")
            
            concept = content.get('concept', name)
            exp = content.get('explanation', '')
            comm = edge_tts.Communicate(concept, 'zh-CN-XiaoxiaoNeural')
            await comm.save(f"{dir_path}/audio_concept.mp3")
            if exp:
                comm = edge_tts.Communicate(exp, 'zh-CN-XiaoxiaoNeural')
                await comm.save(f"{dir_path}/audio_explanation.mp3")
            
            with open(f"{dir_path}/{tid}.json", 'w', encoding='utf-8') as f:
                json.dump({"topic_id": tid, "name": name, "subject": subj, "grade": grade, "content": content}, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅")
            return True
    except Exception as e:
        print(f"   ❌ {e}")
        return False

async def main():
    tasks = [gen(t) for t in SCIENCE_TOPICS]
    results = await asyncio.gather(*tasks)
    print(f"\n✅ 完成: {sum(results)}/{len(SCIENCE_TOPICS)}")

if __name__ == '__main__':
    asyncio.run(main())
