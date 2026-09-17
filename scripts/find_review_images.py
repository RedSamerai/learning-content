#!/usr/bin/env python3
"""找出需要人工审核的图片"""
import json
import os

# 加载所有JSON文件
def find_topics_needing_review():
    reviewed_topics = []
    
    for root, dirs, files in os.walk('output'):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 检查是否有图片路径
                    topic_id = data.get('topic_id', '')
                    subject = data.get('subject', '')
                    age_group = data.get('age_group', '')
                    
                    image_path = f"{root}/{topic_id}/image.png"
                    if os.path.exists(image_path):
                        reviewed_topics.append({
                            'id': topic_id,
                            'name': data.get('name', ''),
                            'subject': subject,
                            'age': age_group,
                            'image': image_path
                        })
                except:
                    pass
    
    return reviewed_topics

# 获取质检结果
def check_qa_status():
    topics = find_topics_needing_review()
    
    print("=== 幼儿园知识点图片状态 ===\n")
    
    passed = []
    needs_review = []
    
    for topic in topics:
        # 检查是否通过质检（文件大小>100KB通常表示有内容）
        img_size = os.path.getsize(topic['image']) if os.path.exists(topic['image']) else 0
        
        # 根据之前生成的日志，以下主题图片需人工审核
        review_list = [
            'health_kg_express_emotion',
            'sci_kg_animal',
            'math_kg_shape_find',
            'math_kg_count_10',
            'math_kg_count_20',
            'art_kg_draw',
            'art_kg_beauty'
        ]
        
        if topic['id'] in review_list:
            needs_review.append(topic)
        else:
            passed.append(topic)
    
    print(f"✅ 通过质检: {len(passed)} 张\n")
    print("=== 需要人工审核的图片 ===\n")
    
    for i, topic in enumerate(needs_review, 1):
        print(f"{i}. {topic['id']}")
        print(f"   名称: {topic['name']}")
        print(f"   学科: {topic['subject']} | 年龄: {topic['age']}")
        print(f"   路径: {topic['image']}")
        print()
    
    print(f"\n共 {len(needs_review)} 张图片需要人工审核")

if __name__ == '__main__':
    check_qa_status()
