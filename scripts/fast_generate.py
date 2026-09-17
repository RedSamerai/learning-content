#!/usr/bin/env python3
"""快速生成所有剩余知识点 - 使用后台任务"""
import asyncio
import aiohttp
import json
import os
import edge_tts
from PIL import Image, ImageDraw

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 所有待生成的知识点
REMAINING = [
    ("chinese", "幼小衔接", "py_pin du", "拼音拼读练习"),
    ("chinese", "幼小衔接", "py_char_100", "认识100个常用字"),
    ("chinese", "幼小衔接", "py_char_name", "认识自己的名字"),
    ("chinese", "幼小衔接", "py_write_heaven", "写天和地"),
    ("chinese", "幼小衔接", "py_write_human", "写人和大"),
    ("chinese", "一年级上", "py_look_talk_1", "看图说一句话"),
    ("chinese", "一年级上", "py_read_lesson1", "朗读课文秋天"),
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
    ("math", "一年级上", "math_py_shape_2", "认识正方体"),
    ("math", "一年级上", "math_py_shape_3", "认识圆柱"),
    ("math", "一年级上", "math_py_shape_4", "认识球"),
    ("math", "一年级下", "math_py_flat_shape", "认识平面图形"),
    ("math", "一年级上", "math_py_clock_1", "认识整时"),
    ("math", "一年级上", "math_py_clock_2", "认识半时"),
    ("math", "一年级下", "math_py_money_1", "认识元角分"),
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

PROMPTS = {
    "py_pin du": "编写拼音拼读练习教学内容，讲解拼读规则，举例说明，生成练习题。",
    "py_char_100": "编写认识100个常用字的教学内容，介绍识字方法。",
    "py_char_name": "编写认识自己名字的教学内容。",
    "py_write_heaven": "编写写天和地的教学内容，教笔画顺序。",
    "py_write_human": "编写写人和大的教学内容，教笔画顺序。",
    "py_look_talk_1": "编写看图说一句话的教学内容。",
    "py_read_lesson1": "编写朗读课文《秋天》的教学内容。",
    "math_py_compare": "编写比大小的教学内容，讲解大于小于等于号。",
    "math_py_order": "编写数的顺序教学内容。",
    "math_py_add_5": "编写5以内加法的练习题和讲解。",
    "math_py_sub_5": "编写5以内减法的练习题和讲解。",
    "math_py_add_10": "编写10以内加法的练习题和讲解。",
    "math_py_sub_10": "编写10以内减法的练习题和讲解。",
    "math_py_count_20": "编写数数1-20的教学内容。",
    "math_py_write_20": "编写写数1-20的教学内容。",
    "math_py_add_20_1": "编写9加几的进位加法教学内容。",
    "math_py_add_20_2": "编写8、7、6加几的进位加法教学内容。",
    "math_py_add_20_3": "编写5、4、3、2加几的进位加法教学内容。",
    "math_py_shape_2": "编写认识正方体的教学内容。",
    "math_py_shape_3": "编写认识圆柱的教学内容。",
    "math_py_shape_4": "编写认识球的教学内容。",
    "math_py_flat_shape": "编写认识平面图形（圆形、三角形、正方形、长方形）的教学内容。",
    "math_py_clock_1": "编写认识整时的教学内容。",
    "math_py_clock_2": "编写认识半时的教学内容。",
    "math_py_money_1": "编写认识元角分的教学内容。",
    "sci_py_plant_1": "编写观察校园植物的教学内容。",
    "sci_py_animal_1": "编写认识常见动物的教学内容。",
    "sci_py_plant_need": "编写植物生长需要的教学内容。",
    "sci_py_water_1": "编写水的特征的教学内容。",
    "sci_py_air_1": "编写空气特点的教学内容。",
    "sci_py_hard_soft": "编写软硬比较的教学内容。",
    "sci_py_float_sink": "编写浮与沉的教学内容。",
    "sci_py_weather_1": "编写认识天气的教学内容。",
    "sci_py_season_1": "编写四季变化的教学内容。",
    "mor_py_good habit_1": "编写早睡早起习惯培养的教学内容。",
    "mor_py_clean_1": "编写讲卫生勤洗手的教学内容。",
}

def create_image(name):
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((250, 80), name, fill='#333333')
    return img

async def generate_single(item):
    subj, grade, tid, name = item
    prompt_text = PROMPTS.get(tid, f"编写{name}的教学内容。")
    
    try:
        async with aiohttp.ClientSession() as session:
            # 生成文本
            async with session.post(
                f"{AGNES_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": f"请为小学{grade}学生编写{name}的教学内容：要求用简单易懂的语言，举例贴近生活，生成3道选择题。输出JSON：{{\"concept\":\"...\",\"explanation\":\"...\",\"questions\":[...]}}"}], "response_format": {"type": "json_object"}}
            ) as r:
                if r.status != 200:
                    return False
                data = await r.json()
                content = json.loads(data["choices"][0]["message"]["content"])
            
            # 保存文件
            dir_path = f"output/{subj}/{grade}/{tid}"
            os.makedirs(dir_path, exist_ok=True)
            
            # 图片
            img = create_image(name)
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
            
            return True
    except Exception as e:
        print(f"   ❌ {name}: {e}")
        return False

async def main():
    print(f"🚀 开始生成 {len(REMAINING)} 个知识点...\n")
    
    # 分批处理，每批5个并行
    batch_size = 5
    completed = 0
    
    for i in range(0, len(REMAINING), batch_size):
        batch = REMAINING[i:i+batch_size]
        tasks = [generate_single(item) for item in batch]
        results = await asyncio.gather(*tasks)
        
        batch_done = sum(results)
        completed += batch_done
        
        print(f"进度: {completed}/{len(REMAINING)} 完成")
    
    print(f"\n✅ 全部完成！共生成 {completed} 个知识点")

if __name__ == '__main__':
    asyncio.run(main())
