#!/usr/bin/env python3
"""
重新生成3张数学图片 - 使用AI生成，确保内容正确且美观
"""
import asyncio
import aiohttp
import os

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

# 3个图片的精确prompt
prompts = {
    'math_kg_count_10': '''儿童数学教育插画，白色背景，显示数字1到10：
画面中央是阿拉伯数字1到10，每个数字用大号彩色字体显示，排列成一行或两行。
数字之间用简单的彩色圆点或小装饰分隔。
风格：扁平化设计，色彩鲜艳明快，字体圆润可爱，适合幼儿认知。
不要画动物、水果或其他物体，只展示数字本身。''',

    'math_kg_count_20': '''儿童数学教育插画，白色背景，显示数字1到20：
画面分为两行，第一行是数字1-10，第二行是数字11-20。
每个数字用大号彩色字体清晰显示，排列整齐。
数字之间用浅色格子或圆圈背景衬托，便于区分。
风格：扁平化设计，色彩柔和，字体清晰易读，适合幼儿学习计数。
不要画任何动物、植物或其他物体，只展示数字排列。''',

    'math_kg_shape_find': '''儿童数学教育插画，白色背景，展示四个基本几何图形：
从左到右依次排列：
1. 红色实心圆形
2. 蓝色实心正方形
3. 黄色实心三角形（正三角形）
4. 绿色实心椭圆形（横向）

每个图形大小相近，间距均匀，下方留有空间标注图形名称。
风格：扁平化设计，色彩鲜明，线条简洁，适合幼儿认知。
不要添加任何背景元素、动物或装饰物，只展示这四个基本图形。'''
}

async def generate_image(topic_id, prompt):
    """生成单张图片"""
    print(f"\n🎨 生成: {topic_id}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/images/generations",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-image-2.1-flash",
                "prompt": prompt,
                "size": "1024x512",
                "n": 1
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                image_url = data['data'][0].get('url', '')
                
                if image_url:
                    # 下载图片
                    async with session.get(image_url) as img_response:
                        if img_response.status == 200:
                            img_data = await img_response.read()
                            
                            # 根据topic_id确定保存路径
                            if 'count_10' in topic_id:
                                save_path = "output/science/小班(3-4岁)/math_kg_count_10/image.png"
                            elif 'count_20' in topic_id:
                                save_path = "output/science/中班(4-5岁)/math_kg_count_20/image.png"
                            elif 'shape_find' in topic_id:
                                save_path = "output/science/小班(3-4岁)/math_kg_shape_find/image.png"
                            else:
                                save_path = f"output/{topic_id}/image.png"
                            
                            os.makedirs(os.path.dirname(save_path), exist_ok=True)
                            
                            with open(save_path, 'wb') as f:
                                f.write(img_data)
                            
                            print(f"✅ {topic_id}: {len(img_data)} bytes")
                            return True
                        else:
                            print(f"❌ 下载失败: {img_response.status}")
                            return False
            else:
                print(f"❌ API错误 {response.status}: {await response.text()}")
                return False

async def main():
    print("🔧 重新生成3张数学图片...")
    
    results = []
    for topic_id, prompt in prompts.items():
        result = await generate_image(topic_id, prompt)
        results.append(result)
    
    if all(results):
        print("\n✅ 全部完成！")
    else:
        print("\n⚠️ 部分图片生成失败")

if __name__ == '__main__':
    asyncio.run(main())
