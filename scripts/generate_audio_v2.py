#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频生成脚本 - 为3-9岁学习内容生成音频文件
使用edge-tts本地生成，音色：
- 幼儿园/幼小衔接: zh-CN-XiaoyiNeural
- 小学1-3年级: zh-CN-XiaoxiaoNeural
"""

import json
import asyncio
import edge_tts
from pathlib import Path
from datetime import datetime
import time

# 配置
BASE_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content')
OUTPUT_DIR = BASE_DIR / 'output'
LOG_FILE = BASE_DIR / 'audio_generation_log.txt'

# 音色配置
VOICES = {
    '幼儿园': 'zh-CN-XiaoyiNeural',
    '幼小衔接': 'zh-CN-XiaoyiNeural',
    '一年级上': 'zh-CN-XiaoxiaoNeural',
    '一年级下': 'zh-CN-XiaoxiaoNeural',
    '二年级上': 'zh-CN-XiaoxiaoNeural',
    '二年级下': 'zh-CN-XiaoxiaoNeural',
    '三年级上': 'zh-CN-XiaoxiaoNeural',
    '三年级下': 'zh-CN-XiaoxiaoNeural',
}

# 年龄范围（需要音频）
AGE_RANGE = ['幼儿园', '幼小衔接', '一年级上', '一年级下', '二年级上', '二年级下', '三年级上', '三年级下']

async def generate_audio(text: str, output_path: Path, voice: str, rate: str = "-10%"):
    """生成单个音频文件"""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(str(output_path))

def get_text_for_audio(item: dict) -> str:
    """提取用于音频生成的文本"""
    parts = []
    if item.get('topic'):
        parts.append(item['topic'])
    if item.get('content'):
        parts.append(item['content'])
    if item.get('explanation'):
        parts.append(item['explanation'])
    if item.get('example'):
        parts.append(item['example'])
    return ' '.join(parts) if parts else ''

def find_missing_audio():
    """查找缺失音频的文件"""
    missing = []
    
    for grade in AGE_RANGE:
        grade_dir = OUTPUT_DIR / grade
        if not grade_dir.exists():
            continue
        
        # 遍历所有子目录找JSON文件
        for subject_dir in grade_dir.iterdir():
            if not subject_dir.is_dir():
                continue
            
            for json_file in subject_dir.glob('*.json'):
                # 检查是否有对应的音频文件
                # 音频可能在两个位置：
                # 1. 与JSON同级：{name}.mp3
                # 2. 在audio子目录：audio/audio.mp3
                mp3_file = json_file.with_suffix('.mp3')
                audio_dir = json_file.parent / 'audio'
                audio_mp3 = audio_dir / 'audio.mp3'
                
                if not mp3_file.exists() and not audio_mp3.exists():
                    missing.append({
                        'json_path': json_file,
                        'grade': grade,
                        'subject': subject_dir.name,
                        'item': None
                    })
    
    return missing

def load_item(json_path: Path) -> dict:
    """加载JSON文件内容"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

async def process_batch(batch: list, voice: str):
    """处理一批音频生成任务"""
    success = 0
    for item_info in batch:
        try:
            # 加载内容
            item = load_item(item_info['json_path'])
            
            # 获取文本
            text = get_text_for_audio(item)
            if not text or len(text.strip()) < 10:
                print(f"跳过: {item_info['json_path'].name} (内容太短)")
                continue
            
            # 确定音频保存路径（放在audio子目录）
            audio_dir = item_info['json_path'].parent / 'audio'
            audio_dir.mkdir(exist_ok=True)
            mp3_file = audio_dir / 'audio.mp3'
            
            # 生成音频
            await generate_audio(text, mp3_file, voice)
            
            print(f"✓ {item_info['json_path'].relative_to(OUTPUT_DIR)}")
            success += 1
            
        except Exception as e:
            print(f"✗ {item_info['json_path'].name}: {e}")
        
        # 控制RPM（每秒1个，留余量）
        await asyncio.sleep(0.1)
    
    return success

async def main():
    """主函数"""
    print("=" * 60)
    print("音频生成工具")
    print("=" * 60)
    
    # 查找缺失的音频
    print("\n正在扫描缺失的音频文件...")
    missing = find_missing_audio()
    print(f"发现 {len(missing)} 个缺失音频的知识点")
    
    if not missing:
        print("没有需要生成的音频！")
        return
    
    # 按年级分组
    by_grade = {}
    for item in missing:
        grade = item['grade']
        if grade not in by_grade:
            by_grade[grade] = []
        by_grade[grade].append(item)
    
    # 逐个年级生成
    for grade in AGE_RANGE:
        if grade not in by_grade:
            continue
        
        items = by_grade[grade]
        voice = VOICES.get(grade, 'zh-CN-XiaoxiaoNeural')
        
        print(f"\n{'='*60}")
        print(f"生成 {grade} 的音频 ({len(items)}个)...")
        print(f"音色: {voice}")
        print(f"{'='*60}")
        
        # 分批处理，每批30个
        batch_size = 30
        total_success = 0
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            print(f"\n处理批次 {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}...")
            
            success = await process_batch(batch, voice)
            total_success += success
            
            # 批次间暂停，控制RPM
            if i + batch_size < len(items):
                print(f"批次完成，暂停3秒...")
                time.sleep(3)
        
        print(f"\n{grade} 完成: {total_success}/{len(items)} 个音频生成成功")
    
    # 统计
    final_missing = find_missing_audio()
    print(f"\n{'='*60}")
    print(f"最终统计:")
    print(f"  - 已生成音频: {len(missing) - len(final_missing)} 个")
    print(f"  - 仍缺失: {len(final_missing)} 个")
    print(f"{'='*60}")
    
    # 保存日志
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"音频生成日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总数: {len(missing)}, 成功: {len(missing) - len(final_missing)}, 失败: {len(final_missing)}\n\n")
        for item in final_missing:
            f.write(f"缺失: {item['json_path'].relative_to(OUTPUT_DIR)}\n")

if __name__ == '__main__':
    asyncio.run(main())
