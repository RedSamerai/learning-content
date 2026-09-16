#!/usr/bin/env python3
"""
QA bot - 质检Bot
使用 AGNES-3.0-flash 审核内容质量
"""

import asyncio
import json
import aiohttp
import os
from pathlib import Path

AGNES_API_KEY = os.getenv("AGNES_API_KEY", "你的AGNES_API_KEY")
AGNES_BASE_URL = "https://api.agnes.ai/v1"

class QABot:
    """质检Bot - 审核内容质量"""
    
    def __init__(self):
        self.api_key = AGNES_API_KEY
        self.base_url = AGNES_BASE_URL
    
    async def review_content(self, content: dict) -> dict:
        """审核学习内容质量"""
        
        prompt = f"""
请审核以下学习内容的质量：

主题: {content.get('metadata', {}).get('topic', 'N/A')}
年级: {content.get('metadata', {}).get('grade', 'N/A')}
年龄段: {content.get('age_appropriate', {}).get('age_group', 'N/A')}

【内容结构】
{{
  "概念": {content.get('content', {}).get('concept', '')[:200]}...,
  "讲解": {content.get('content', {}).get('explanation', '')[:300]}...,
  "例子数量": {len(content.get('content', {}).get('examples', []))},
  "练习题数量": {len(content.get('practice', []))},
  "常见错误": {content.get('content', {}).get('common_mistakes', [])}
}}

【审核标准】
1. 内容正确性（无知识性错误）
2. 难度合适度（符合年龄段认知）
3. 语言通顺度（无语法错误）
4. 完整性（包含所有必要字段）
5. 版权合规（不复制教材原文）

【输出格式】
{{
  "passed": true/false,
  "score": 0-100,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"],
  "grade": "A/B/C/D"
}}
"""
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "agnes-3.0-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }
            ) as response:
                data = await response.json()
                return json.loads(data["choices"][0]["message"]["content"])


async def main():
    """测试：审核示例内容"""
    
    # 示例内容
    test_content = {
        "id": "math_kg_number_recognition",
        "metadata": {
            "subject": "math",
            "grade": "kindergarten",
            "age_group": "kindergarten",
            "topic": "认识数字1-10"
        },
        "age_appropriate": {
            "min_age": 3,
            "max_age": 6
        },
        "content": {
            "concept": "数字是用来表示数量的符号...",
            "explanation": "每个数字都有独特的形状...",
            "examples": [
                {"text": "1个苹果", "description": "看，这里有1个红红的苹果！"}
            ],
            "common_mistakes": ["把6和9搞混"]
        },
        "practice": [
            {
                "type": "multiple_choice",
                "question": "下面哪个是数字3？",
                "options": ["1", "2", "3", "4"],
                "answer": "3",
                "explanation": "数字3的形状像半个耳朵"
            }
        ]
    }
    
    bot = QABot()
    result = await bot.review_content(test_content)
    
    print("✅ 审核完成！")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
