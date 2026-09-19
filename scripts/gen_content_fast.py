#!/usr/bin/env python3
"""快速内容生成器 - 只生成文本，跳过音频"""
import asyncio, aiohttp, json, time
from pathlib import Path

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
REQUEST_DELAY = 2  # 2秒间隔，加快速度

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

async def process_topic(topic):
    """处理单个知识点 - 只生成内容"""
    topic_id = topic["id"]
    safe_id = topic_id.replace("/", "_").replace("\\", "_").replace(" ", "_")
    
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
    
    # 保存（不生成音频）
    data = {
        "id": topic_id,
        "grade": topic["grade"],
        "subject": topic["subject"],
        "chapter": topic.get("chapter", ""),
        "topic": topic["topic"],
        "description": topic.get("description", ""),
        "explanation": explanation,
        "audio": ""
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 完成 ({len(explanation)}字)")
    return True

async def main():
    # 加载知识点清单
    with open("knowledge_graph_complete.json", "r", encoding="utf-8") as f:
        topics = json.load(f)
    
    print(f"共 {len(topics)} 个知识点待生成")
    
    # 过滤出已完成的内容，找出未完成的
    completed_ids = set()
    for p in Path("output").rglob("*.json"):
        if p.parent.name in ['image', 'audio']:
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("explanation") and len(data["explanation"]) > 500:
                    completed_ids.add(data["id"])
        except:
            pass
    
    pending_topics = [t for t in topics if t["id"] not in completed_ids]
    print(f"待生成: {len(pending_topics)} 个知识点")
    
    start_time = time.time()
    completed = 0
    failed = 0
    
    for i, topic in enumerate(pending_topics):
        success = await process_topic(topic)
        if success:
            completed += 1
        else:
            failed += 1
        
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            print(f"\n⏸ 进度: {i+1}/{len(pending_topics)} ({elapsed/60:.1f}分钟)")
        
        await asyncio.sleep(REQUEST_DELAY)
    
    print(f"\n✅ 完成!")
    print(f"  成功: {completed}")
    print(f"  失败: {failed}")
    print(f"  总耗时: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}")

if __name__ == "__main__":
    asyncio.run(main())
