#!/usr/bin/env python3
"""
自动修复不合格的图片（重新生成+质检循环）
"""

import asyncio
import aiohttp
import json
import os
import base64
from typing import List, Dict

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"
MAX_RETRIES = 3  # 最多重试3次

async def generate_image(prompt: str, output_path: str, resolution: str = "768x512") -> bool:
    """生成图片并下载"""
    
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
            if response.status != 200:
                return False
            
            data = await response.json()
            image_url = data['data'][0].get('url', '')
            
            if not image_url:
                return False
            
            async with session.get(image_url) as img_response:
                if img_response.status == 200:
                    content = await img_response.read()
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    return True
            return False

async def qa_image(image_path: str, expected_content: str) -> Dict:
    """质检图片"""
    
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = f"""
请审核这张教育插图：

期望：{expected_content}

检查：
1. 数量是否正确？
2. 类型是否正确？
3. 内容是否清晰？

输出JSON：{{"passed": true/false, "score": 0-100, "issues": []}}
"""
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{AGNES_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {AGNES_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "agnes-3.0-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                "response_format": {"type": "json_object"}
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                return json.loads(data["choices"][0]["message"]["content"])
            return {"passed": False, "score": 0, "issues": ["API错误"]}

async def fix_image(test_case: Dict) -> bool:
    """自动修复一张不合格的图片"""
    
    filename = test_case["filename"]
    expected = test_case["expected"]
    prompt = test_case["prompt"]
    output_path = f"test_output/examples/{filename}"
    
    print(f"\n🔄 修复: {filename}")
    print(f"   期望: {expected}")
    
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"   第{attempt}次尝试...")
        
        # 生成图片
        if not await generate_image(prompt, output_path):
            print(f"   ❌ 生成失败")
            continue
        
        # 质检
        result = await qa_image(output_path, expected)
        
        if result["passed"] and result["score"] >= 80:
            print(f"   ✅ 通过 (分数: {result['score']})")
            return True
        else:
            print(f"   ❌ 不通过 (分数: {result['score']})")
            if result.get("issues"):
                print(f"      问题: {result['issues'][0][:50]}...")
    
    print(f"   ⚠️ 达到最大重试次数，标记为需要人工审核")
    return False

async def main():
    print("🛠️ 自动修复不合格图片")
    print("=" * 50)
    
    # 需要修复的图片测试用例
    tests = [
        {
            "filename": "numbers-123.png",
            "expected": "三个独立的区域：左边数字1和1个苹果，中间数字2和2只鸟，右边数字3和3朵花。每个区域清晰分开，数量准确。",
            "prompt": "儿童插画风格，简洁白色背景，三个独立区域水平排列。左侧：卡通数字1旁边有1个红苹果；中间：卡通数字2旁边有2只小鸟；右侧：卡通数字3旁边有3朵花。每个区域用淡色边框分隔，整体风格统一可爱，适合幼儿认知，教育类插图"
        }
    ]
    
    results = []
    for test in tests:
        success = await fix_image(test)
        results.append({
            "file": test["filename"],
            "success": success
        })
    
    print("\n" + "=" * 50)
    print(f"✅ 修复完成: {sum(1 for r in results if r['success'])}/{len(results)} 通过")

if __name__ == '__main__':
    asyncio.run(main())
