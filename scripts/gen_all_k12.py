#!/usr/bin/env python3
"""生成剩余所有知识点 - 完整版"""
import asyncio, aiohttp, json, os, edge_tts
from PIL import Image, ImageDraw

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 所有待生成知识点（按科目分组）
ALL_TOPICS = [
    # 幼小衔接语文（部分已完成）
    ("chinese", "幼小衔接", "py_pin du", "拼音拼读练习"),
    ("chinese", "幼小衔接", "py_char_100", "认识100个常用字"),
    ("chinese", "幼小衔接", "py_char_name", "认识自己的名字"),
    ("chinese", "幼小衔接", "py_write_heaven", "写天和地"),
    ("chinese", "幼小衔接", "py_write_human", "写人和大"),
    ("chinese", "一年级上", "py_look_talk_1", "看图说一句话"),
    ("chinese", "一年级上", "py_read_lesson1", "朗读课文秋天"),
    
    # 小学数学（部分已完成）
    ("math", "一年级上", "math_py_count_10", "数数1-10"),
    ("math", "一年级上", "math_py_compare", "比大小"),
    ("math", "一年级上", "math_py_order", "数的顺序"),
    ("math", "一年级上", "math_py_add_5", "5以内的加法"),
    ("math", "一年级上", "math_py_sub_5", "5以内的减法"),
    ("math", "一年级上", "math_py_add_10", "10以内的加法"),
    ("math", "一年级上", "math_py_sub_10", "10以内的减法"),
    ("math", "一年级上", "math_py_count_20", "数数1-20"),
    ("math", "一年级上", "math_py_write_20", "写数1-20"),
    ("math", "一年级上", "math_py_add_20_1", "9加几"),
    ("math", "一年级上", "math_py_add_20_2", "8、7、6加几"),
    ("math", "一年级上", "math_py_add_20_3", "5、4、3、2加几"),
    ("math", "一年级上", "math_py_shape_1", "认识长方体"),
    ("math", "一年级上", "math_py_shape_2", "认识正方体"),
    ("math", "一年级上", "math_py_shape_3", "认识圆柱"),
    ("math", "一年级上", "math_py_shape_4", "认识球"),
    ("math", "一年级下", "math_py_flat_shape", "认识平面图形"),
    ("math", "一年级上", "math_py_clock_1", "认识整时"),
    ("math", "一年级上", "math_py_clock_2", "认识半时"),
    ("math", "一年级下", "math_py_money_1", "认识元角分"),
    
    # 小学科学
    ("science", "一年级上", "sci_py_plant_1", "观察校园里的植物"),
    ("science", "一年级上", "sci_py_animal_1", "认识常见的动物"),
    ("science", "二年级上", "sci_py_plant_need", "植物生长需要什么"),
    ("science", "一年级上", "sci_py_water_1", "水的特征"),
    ("science", "一年级上", "sci_py_air_1", "空气的特点"),
    ("science", "二年级上", "sci_py_hard_soft", "软硬比较"),
    ("science", "二年级上", "sci_py_float_sink", "浮与沉"),
    ("science", "一年级上", "sci_py_weather_1", "认识天气"),
    ("science", "一年级下", "sci_py_season_1", "四季的变化"),
    
    # 道德与法治
    ("morality", "一年级上", "mor_py_good_habit_1", "早睡早起"),
    ("morality", "一年级上", "mor_py_clean_1", "讲卫生勤洗手"),
]

async def gen_single(item):
    subj, grade, tid, name = item
    try:
        # 检查是否已存在
        existing = f"output/{subj}/{grade}/{tid}.json"
        if os.path.exists(existing):
            print(f"⏭️  跳过（已存在）: {name}")
            return True
        
        prompt = f"请为小学{grade}学生编写{name}的教学内容，用简单易懂的语言，举例说明，生成3道选择题。"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AGNES_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
            ) as r:
                if r.status != 200:
                    print(f"   ❌ API错误: {name}")
                    return False
                data = await r.json()
                content = json.loads(data["choices"][0]["message"]["content"])
        
        dir_path = f"output/{subj}/{grade}/{tid}"
        os.makedirs(dir_path, exist_ok=True)
        
        # 图片
        img = Image.new('RGB', (800, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((250, 80), name, fill='#333333')
        img.save(f"{dir_path}/image.png")
        
        # 音频
        concept = content.get('concept', name)
        exp = content.get('explanation', '')
        comm = edge_tts.Communicate(concept, 'zh-CN-XiaoxiaoNeural')
        await comm.save(f"{dir_path}/audio_concept.mp3")
        if exp:
            comm = edge_tts.Communicate(exp, 'zh-CN-XiaoxiaoNeural')
            await comm.save(f"{dir_path}/audio_explanation.mp3")
        
        # JSON
        with open(f"{dir_path}/{tid}.json", 'w', encoding='utf-8') as f:
            json.dump({"topic_id": tid, "name": name, "subject": subj, "grade": grade, "content": content}, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {name}")
        return True
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

async def main():
    print("🚀 开始生成所有知识点...\n")
    tasks = [gen_single(t) for t in ALL_TOPICS]
    results = await asyncio.gather(*tasks)
    completed = sum(results)
    print(f"\n{'='*50}")
    print(f"✅ 完成: {completed}/{len(ALL_TOPICS)}")
    print(f"{'='*50}")

if __name__ == '__main__':
    asyncio.run(main())
