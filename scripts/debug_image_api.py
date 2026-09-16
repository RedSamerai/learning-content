#!/usr/bin/env python3
"""
调试：测试AGNES图片生成API
"""

import asyncio
import aiohttp
import os
import base64

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def test_api():
    print("🔍 测试AGNES图片生成API...")
    print("=" * 50)
    
    prompt = "儿童插画风格，一个红苹果，简洁背景，教育类插图"
    
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
                "size": "512x512",
                "n": 1
            }
        ) as response:
            print(f"响应状态: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print(f"响应内容: {data}")
                
                # 保存
                if 'data' in data and len(data['data']) > 0:
                    image_data = data['data'][0].get('b64_json', '')
                    if image_data:
                        output_path = "test_output/debug/apple.png"
                        os.makedirs("test_output/debug", exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(base64.b64decode(image_data))
                        print(f"✅ 图片已保存: {output_path}")
                        print(f"   文件大小: {os.path.getsize(output_path)} bytes")
                    else:
                        print("❌ 返回数据中没有图片")
                else:
                    print(f"❌ 异常响应: {data}")
            else:
                error_text = await response.text()
                print(f"❌ 错误: {error_text}")

if __name__ == '__main__':
    asyncio.run(test_api())
