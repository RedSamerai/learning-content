#!/usr/bin/env python3
"""
重新生成示例图片（正确风格）
"""

import asyncio
import aiohttp
import os
import base64

# 正确的API配置
AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def generate_image(prompt: str, output_path: str, resolution: str = "1024x1024"):
    """调用AGNES图片生成API"""
    
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
                "size": resolution,
                "n": 1
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                image_data = data['data'][0]['b64_json']
                
                output_dir = os.path.dirname(output_path)
                os.makedirs(output_dir, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(base64.b64decode(image_data))
                
                print(f"✅ {output_path}")
                return True
            else:
                error_text = await response.text()
                print(f"❌ 失败: {error_text[:100]}")
                return False

async def main():
    print("🎨 重新生成示例图片...")
    print("=" * 50)
    
    # 幼儿园风格提示词
    images = [
        {
            "desc": "1个红苹果",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，一个红苹果，适合幼儿认知，教育类插图，卡通风格",
            "output": "test_output/examples/1-apple.png",
            "resolution": "512x512"
        },
        {
            "desc": "2只小鸟",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，两只小鸟站在树枝上，适合幼儿认知，教育类插图，卡通风格",
            "output": "test_output/examples/2-birds.png",
            "resolution": "512x512"
        },
        {
            "desc": "3朵花",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，三朵鲜花在阳光下，适合幼儿认知，教育类插图，卡通风格",
            "output": "test_output/examples/3-flowers.png",
            "resolution": "512x512"
        },
        {
            "desc": "数字123卡通",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁背景，数字1、2、3的卡通形象，每个数字旁边有对应数量的物体，适合幼儿认知，教育类插图",
            "output": "test_output/examples/numbers-123.png",
            "resolution": "768x512"
        }
    ]
    
    for img in images:
        print(f"\n📷 生成: {img['desc']}")
        print(f"   分辨率: {img['resolution']}")
        await generate_image(img['prompt'], img['output'], img['resolution'])
    
    print("\n" + "=" * 50)
    print("✅ 全部完成！")
    print(f"📁 保存位置: {os.path.abspath('test_output/examples/')}")

if __name__ == '__main__':
    asyncio.run(main())
