#!/usr/bin/env python3
"""生成高质量教科书式讲解内容 - 干净版"""
import asyncio, aiohttp, json, time, os
from pathlib import Path
import edge_tts

AGNES_API_KEY = os.environ.get('AGNES_API_KEY', '')
REQUEST_DELAY = 4

async def generate_explanation(topic):
    """生成详细讲解内容"""
    prompt = f"""你是一个专业的K12教育内容专家。请为以下知识点生成详细的教科书式讲解内容。

知识点：{topic['topic']}
学科：{topic['subject']}
年级：{topic['grade']}
章节：{topic.get('chapter', '')}

要求：
1. 用通俗易懂的语言解释概念
2. 包含生活实际例子
3. 说明公式、定理或规则
4. 指出常见误区
5. 字数不少于500字
6. 适合学生自学理解

请直接输出讲解内容，不要标题。"""

    payload = {
        'model': 'agnes-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7,
        'max_tokens': 2000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://apihub.agnes-ai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {AGNES_API_KEY}', 'Content-Type': 'application/json'},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    print(f"  ❌ API错误: {resp.status}")
                    return None
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None

async def generate_audio(topic_id, topic_name, grade):
    """生成音频 - 使用更简单的方式"""
    try:
        voice = "zh-CN-XiaoyiNeural" if grade in ["幼儿园", "幼小衔接"] else "zh-CN-YunxiNeural"
        communicate = edge_tts.Communicate(topic_name, voice)
        audio_path = Path(f"output/{topic_id}.mp3")
        # 使用更短的超时
        await asyncio.wait_for(communicate.save(str(audio_path)), timeout=20.0)
        return str(audio_path)
    except Exception as e:
        print(f"  ⚠️ 音频跳过: {e}")
        return None

async def process_topic(topic):
    """处理单个知识点"""
    topic_id = topic["id"]
    # 生成安全的文件名
    safe_id = topic_id.replace("/", "_").replace("\\", "_").replace(" ", "_")
    
    # 创建目录
    output_dir = Path(f"output/{topic['grade']}/{topic['subject']}/{safe_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = output_dir / f"{safe_id}.json"
    
    # 检查是否已存在
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if existing.get("explanation") and len(existing["explanation"]) > 500:
            return True
    
    print(f"\n📚 {topic['grade']} - {topic['subject']} - {topic['topic']}")
    
    # 生成讲解
    print("  📝 生成讲解...")
    explanation = await generate_explanation(topic)
    if not explanation:
        return False
    
    # 生成音频 - 只给幼儿园和小学1-3年级
    need_audio = topic['grade'] in ["幼儿园", "幼小衔接", 
                                    "一年级上", "一年级下",
                                    "二年级上", "二年级下",
                                    "三年级上", "三年级下"]
    
    audio_path = ""
    audio_status = "⏭"
    if need_audio:
        try:
            print("  🔊 生成音频...")
            audio_path = await asyncio.wait_for(
                generate_audio(safe_id, topic["topic"], topic["grade"]),
                timeout=30.0
            )
            audio_status = "✅" if audio_path else "❌"
        except asyncio.TimeoutError:
            print("  ⏭ 音频超时，跳过")
            audio_path = ""
        except Exception as e:
            print(f"  ⏭ 音频错误: {e}")
            audio_path = ""
    
    # 保存
    data = {
        "id": topic_id,
        "grade": topic["grade"],
        "subject": topic["subject"],
        "chapter": topic.get("chapter", ""),
        "topic": topic["topic"],
        "description": topic.get("description", ""),
        "explanation": explanation,
        "audio": audio_path if audio_path else ""
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  {audio_status} 完成 ({len(explanation)}字)")
    return True

async def main():
    # 加载知识点清单
    with open("knowledge_graph_complete.json", "r", encoding="utf-8") as f:
        topics = json.load(f)
    
    print(f"共 {len(topics)} 个知识点待生成")
    
    start_time = time.time()
    completed = 0
    failed = 0
    
    for i, topic in enumerate(topics):
        success = await process_topic(topic)
        if success:
            completed += 1
        else:
            failed += 1
        
        # 进度报告
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed * 3600
            print(f"\n⏸ 进度: {i+1}/{len(topics)} ({elapsed/60:.1f}分钟, 预计剩余: {(len(topics)-i-1)/rate:.1f}分钟)")
        
        # RPM控制
        await asyncio.sleep(REQUEST_DELAY)
    
    elapsed = time.time() - start_time
    print(f"\n✅ 完成!")
    print(f"  成功: {completed}")
    print(f"  失败: {failed}")
    print(f"  总耗时: {elapsed/60:.1f}分钟")

if __name__ == "__main__":
    asyncio.run(main())
