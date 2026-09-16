#!/usr/bin/env python3
"""
CurriculumBot - 课程设计Bot
使用 AGNES-2.5-flash 生成知识点内容
"""

import asyncio
import json
import aiohttp
import os
from pathlib import Path
from typing import Dict, List, Any

# AGNES API配置
AGNES_API_KEY = os.getenv("AGNES_API_KEY", "你的AGNES_API_KEY")
AGNES_BASE_URL = "https://api.agnes.ai/v1"

# 年龄适配配置
AGE_CONFIG = {
    'kindergarten': {
        'language_style': 'simple',
        'sentence_length': 'short',
        'use_animals': True,
        'use_emojis': True,
        'examples_theme': 'daily_life'
    },
    'grade1': {
        'language_style': 'friendly',
        'sentence_length': 'medium',
        'use_animals': True,
        'use_emojis': True,
        'examples_theme': 'school_and_home'
    },
    'grade2': {
        'language_style': 'friendly',
        'sentence_length': 'medium',
        'use_animals': False,
        'use_emojis': True,
        'examples_theme': 'school_and_home'
    },
    'grade3-6': {
        'language_style': 'clear',
        'sentence_length': 'normal',
        'use_animals': False,
        'use_emojis': False,
        'examples_theme': 'real_world'
    },
    'middle_school': {
        'language_style': 'professional',
        'sentence_length': 'normal',
        'use_animals': False,
        'use_emojis': False,
        'examples_theme': 'academic'
    }
}

class CurriculumBot:
    """课程设计Bot - 生成文本内容"""
    
    def __init__(self):
        self.api_key = AGNES_API_KEY
        self.base_url = AGNES_BASE_URL
    
    async def generate_topic(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """为单个知识点生成完整内容"""
        
        age_group = topic['age_group']
        config = AGE_CONFIG.get(age_group, AGE_CONFIG['grade3-6'])
        
        prompt = self._build_prompt(topic, config)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "agnes-2.5-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7
                }
            ) as response:
                data = await response.json()
                content = json.loads(data["choices"][0]["message"]["content"])
                return self._post_process(content, topic)
    
    def _build_prompt(self, topic: Dict, config: Dict) -> str:
        """构建AI生成提示词"""
        
        return f"""
你是{topic['grade']}年级的{topic['subject']}老师。请为以下知识点生成教学内容：

知识点ID: {topic['id']}
主题: {topic['name']}
年级: {topic['grade']} ({topic['age_group']})
教学目标: {', '.join(topic.get('objectives', []))}

【语言风格要求】
- 使用{config['language_style']}语言
- 句子长度:{config['sentence_length']}
- 使用动物比喻: {'是' if config['use_animals'] else '否'}
- 使用表情符号: {'是' if config['use_emojis'] else '否'}
- 例子主题:{config['examples_theme']}

【输出格式】
请输出JSON格式，包含以下字段：
{{
  "concept": "概念解释（100字以内，生动有趣）",
  "explanation": "详细讲解（200字以内，循序渐进）",
  "examples": [
    {{"text": "例子文字", "description": "简短说明"}}
  ],
  "common_mistakes": ["常见错误1", "常见错误2"],
  "tips": ["学习技巧1", "学习技巧2"]
}}

【年龄适配要点】
"""
        
        if topic['age_group'] == 'kindergarten':
            return prompt + """
- 用孩子能理解的简单语言
- 多用比喻和故事
- 加入拟人化的元素
- 避免抽象概念
- 每个句子不要超过15个字
"""
        elif topic['age_group'] in ['grade1', 'grade2']:
            return prompt + """
- 语言要亲切友好
- 可以加入一些趣味性
- 例子要贴近生活
- 保持鼓励的语气
- 适当使用表情符号
"""
        else:
            return prompt + """
- 语言准确规范
- 逻辑清晰
- 例子要有代表性
- 可以适当深入
"""
    
    def _post_process(self, content: Dict, topic: Dict) -> Dict:
        """后处理：添加元数据"""
        
        content['id'] = topic['id']
        content['version'] = '1.0.0'
        content['metadata'] = {
            'subject': topic['subject'],
            'grade': topic['grade'],
            'age_group': topic['age_group'],
            'generated_by': 'CurriculumBot'
        }
        
        return content


async def main():
    """主函数 - 测试单个知识点生成"""
    
    # 测试数据
    test_topic = {
        "id": "math_kg_counting",
        "name": "数数（1-20）",
        "subject": "math",
        "grade": "kindergarten",
        "age_group": "kindergarten",
        "objectives": [
            "能手口一致点数1-20",
            "能说出总数",
            "能按数量取物"
        ]
    }
    
    bot = CurriculumBot()
    result = await bot.generate_topic(test_topic)
    
    print("✅ 生成成功！")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
