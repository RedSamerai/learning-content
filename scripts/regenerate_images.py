#!/usr/bin/env python3
"""
重新生成示例图片（下载URL方式）
"""

import asyncio
import aiohttp
import os

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def generate_and_download_image(prompt: str, output_path: str, resolution: str = "1024x1024"):
    """生成图片并下载"""
    
    async with aiohttp.ClientSession() as session:
        # 1. 调用API生成图片
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
            if response.status != 200:
                print(f"❌ API调用失败: {response.status}")
                return False
            
            data = await response.json()
            
            # 2. 获取图片URL
            if 'data' not in data or len(data['data']) == 0:
                print(f"❌ 没有返回图片数据")
                return False
            
            image_url = data['data'][0].get('url', '')
            if not image_url:
                print(f"❌ 没有图片URL")
                return False
            
            print(f"   下载: {image_url[:60]}...")
            
            # 3. 下载图片
            async with session.get(image_url) as img_response:
                if img_response.status == 200:
                    content = await img_response.read()
                    
                    # 保存
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    
                    file_size = len(content)
                    print(f"✅ 已保存 ({file_size} bytes)")
                    return True
                else:
                    print(f"❌ 下载失败: {img_response.status}")
                    return False

async def main():
    print("🎨 重新生成示例图片（幼儿园风格）...")
    print("=" * 50)
    
    # 幼儿园风格的图片
    images = [
        {
            "desc": "1个红苹果",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，一个红苹果，适合幼儿认知，教育类插图，卡通风格",
            "output": "test_output/examples/1-apple.png",
            "resolution": "512x512"
        },
        {
            "desc": "2只小鸟",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，两只小鸟站在树枝上唱歌，适合幼儿认知，教育类插图，卡通风格",
            "output": "test_output/examples/2-birds.png",
            "resolution": "512x512"
        },
        {
            "desc": "3朵花",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁白色背景，三朵鲜花在阳光下跳舞，适合幼儿认知，教育类插图，卡通风格",
            "output": "test_output/examples/3-flowers.png",
            "resolution": "512x512"
        },
        {
            "desc": "数字123卡通",
            "prompt": "儿童插画风格，线条圆润可爱，色彩鲜艳明亮，扁平化设计，简洁背景，数字1、2、3的卡通形象，每个数字旁边有对应数量的物体（1个苹果、2只鸟、3朵花），适合幼儿认知，教育类插图",
            "output": "test_output/examples/numbers-123.png",
            "resolution": "768x512"
        }
    ]
    
    success_count = 0
    for img in images:
        print(f"\n📷 {img['desc']}")
        if await generate_and_download_image(img['prompt'], img['output'], img['resolution']):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ 完成！成功: {success_count}/{len(images)}")
    print(f"📁 保存位置: {os.path.abspath('test_output/examples/')}")

if __name__ == '__main__':
    asyncio.run(main())
