#!/usr/bin/env python3
"""
图片质检Bot - 用文本审核图片内容是否正确
"""

import asyncio
import aiohttp
import json
import os
import base64

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1"

async def qa_image(image_path: str, expected_content: str) -> dict:
    """
    用文本审核图片内容是否正确
    
    Args:
        image_path: 图片文件路径
        expected_content: 期望的内容描述，如"3个苹果"
    
    Returns:
        {"passed": bool, "score": int, "issues": list}
    """
    
    # 读取图片并转为base64
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = f"""
请审核这张教育插图是否符合要求：

【期望内容】
{expected_content}

【审核标准】
1. 物体数量是否正确？
2. 物体类型是否正确？（比如要求苹果，不能是梨）
3. 内容是否清晰易懂？
4. 风格是否适合目标年龄段？

【输出格式】
{{
  "passed": true/false,
  "score": 0-100,
  "issues": ["问题1", "问题2"],
  "suggestion": "改进建议"
}}
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
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "response_format": {"type": "json_object"}
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                result = json.loads(data["choices"][0]["message"]["content"])
                return result
            else:
                error_text = await response.text()
                return {"passed": False, "score": 0, "issues": [f"API错误: {error_text}"]}


async def qa_all_images():
    """质检所有生成的图片"""
    
    print("🔍 图片质检...")
    print("=" * 50)
    
    # 测试图片及期望内容
    tests = [
        ("test_output/examples/1-apple.png", "1个红苹果"),
        ("test_output/examples/2-birds.png", "2只小鸟站在树枝上"),
        ("test_output/examples/3-flowers.png", "3朵花"),
        ("test_output/examples/numbers-123.png", "数字1、2、3的卡通形象，旁边有对应数量的物体（1个苹果、2只鸟、3朵花）")
    ]
    
    results = []
    for image_path, expected in tests:
        if os.path.exists(image_path):
            print(f"\n📷 检查: {os.path.basename(image_path)}")
            print(f"   期望: {expected}")
            
            result = await qa_image(image_path, expected)
            results.append({
                "file": image_path,
                "passed": result["passed"],
                "score": result["score"],
                "issues": result.get("issues", [])
            })
            
            status = "✅ 通过" if result["passed"] else "❌ 不通过"
            print(f"   结果: {status} (分数: {result['score']})")
            if result.get("issues"):
                print(f"   问题: {', '.join(result['issues'])}")
        else:
            print(f"\n❌ 文件不存在: {image_path}")
    
    print("\n" + "=" * 50)
    print(f"📊 质检完成: {sum(1 for r in results if r['passed'])}/{len(results)} 通过")
    
    return results


async def main():
    await qa_all_images()


if __name__ == '__main__':
    asyncio.run(main())
