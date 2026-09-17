#!/usr/bin/env python3
"""生成剩余数学知识点"""
import asyncio, aiohttp, json, os, edge_tts
from PIL import Image, ImageDraw
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

MATH_TOPICS = [
    ("math", "一年级上", "math_py_compare", "比大小"),
    ("math", "一年级上", "math_py_order", "数的顺序"),
    ("math", "一年级上", "math_py_add_5", "5以内的加法"),
    ("math", "一年级上", "math_py_sub_5", "5以内的减法"),
    ("math", "一年级上", "math_py_add_10", "10以内的加法"),
    ("math", "一年级上", "math_py_sub_10", "10以内的减法"),
    ("math", "一年级上", "math_py_count_20", "数数1-20"),
    ("math", "一年级上", "math_py_write_20", "写数1-20"),
    ("math", "一年级上", "math_py_shape_2", "认识正方体"),
    ("math", "一年级上", "math_py_shape_3", "认识圆柱"),
    ("math", "一年级上", "math_py_shape_4", "认识球"),
    ("math", "一年级下", "math_py_flat_shape", "认识平面图形"),
    ("math", "一年级上", "math_py_clock_1", "认识整时"),
    ("math", "一年级上", "math_py_clock_2", "认识半时"),
    ("math", "一年级下", "math_py_money_1", "认识元角分"),
]

async def gen(topic):
    subj, grade, tid, name = topic
    print(f"\n📚 {name}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{AGNES_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {AGNES_API_KEY}", "Content-Type": "application/json"},
                json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": f"请为小学一年级学生编写{name}的教学内容，用简单易懂的语言，举例说明，生成3道练习题。"}], "response_format": {"type": "json_object"}}) as r:
                if r.status != 200:
                    print(f"   ❌ API错误 {r.status}")
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
            
            print(f"   ✅")
            return True
    except Exception as e:
        print(f"   ❌ {e}")
        return False

async def main():
    tasks = [gen(t) for t in MATH_TOPICS]
    results = await asyncio.gather(*tasks)
    print(f"\n✅ 完成: {sum(results)}/{len(MATH_TOPICS)}")

if __name__ == '__main__':
    asyncio.run(main())
