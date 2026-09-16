#!/usr/bin/env python3
"""
AudioBot - 语音设计Bot
使用 Edge-TTS 生成语音（免费）
"""

import asyncio
import edge_tts
from pathlib import Path

# 推荐音色配置
VOICE_CONFIG = {
    'kindergarten': {
        'voice': 'zh-CN-XiaoxiaoNeural',
        'rate': '-10%',  # 稍慢
        'pitch': '+5Hz'  # 稍高
    },
    'grade1': {
        'voice': 'zh-CN-XiaoxiaoNeural',
        'rate': '-5%',
        'pitch': '+3Hz'
    },
    'grade2': {
        'voice': 'zh-CN-YunxiNeural',
        'rate': '0%',
        'pitch': '0Hz'
    },
    'default': {
        'voice': 'zh-CN-YunxiNeural',
        'rate': '0%',
        'pitch': '0Hz'
    }
}

class AudioBot:
    """语音设计Bot - 生成语音"""
    
    def __init__(self):
        self.output_dir = Path("audio")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_speech(self, text: str, output_path: str, age_group: str = 'default'):
        """生成语音文件"""
        
        config = VOICE_CONFIG.get(age_group, VOICE_CONFIG['default'])
        communicate = edge_tts.Communicate(
            text,
            config['voice'],
            rate=config['rate'],
            pitch=config['pitch']
        )
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        await communicate.save(output_path)
        print(f"✅ 语音已生成: {output_path}")
    
    async def generate_concept_audio(self, concept: str, topic_id: str, age_group: str):
        """为概念讲解生成语音"""
        output_path = f"{self.output_dir}/{topic_id}/concept.mp3"
        await self.generate_speech(concept, output_path, age_group)
        return output_path
    
    async def generate_practice_audios(self, practice_items: list, topic_id: str, age_group: str):
        """批量生成练习题语音"""
        audios = []
        for item in practice_items:
            if 'audio_question' not in item or 'audio_explanation' not in item:
                # 生成问题语音
                q_path = f"{self.output_dir}/{topic_id}/q_{item['id']}.mp3"
                await self.generate_speech(item['question'], q_path, age_group)
                item['audio_question'] = f"audio/{topic_id}/q_{item['id']}.mp3"
                
                # 生成解释语音
                e_path = f"{self.output_dir}/{topic_id}/e_{item['id']}.mp3"
                await self.generate_speech(item['explanation'], e_path, age_group)
                item['audio_explanation'] = f"audio/{topic_id}/e_{item['id']}.mp3"
            
            audios.append(item)
        return audios


async def main():
    """测试：生成示例语音"""
    bot = AudioBot()
    
    test_text = "数字3的形状像半个耳朵，弯弯的。我们来数一数：一、二、三！"
    await bot.generate_speech(test_text, "test.mp3", 'kindergarten')
    
    print("✅ 测试完成！")

if __name__ == '__main__':
    asyncio.run(main())
