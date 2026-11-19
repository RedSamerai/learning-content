#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成知识点内容脚本
- 每次只处理一个年级
- 每完成一年自动保存进度
- 出错时记录日志但继续运行
- RPM限制：每4秒一个请求
"""

import json
import time
import sys
import logging
from pathlib import Path
from datetime import datetime

# 配置
BASE_DIR = Path('D:/WorkBuddy/learning-app-research/learning-content')
KG_FILE = BASE_DIR / 'knowledge_graph_complete.json'
OUTPUT_DIR = BASE_DIR / 'output'
LOG_FILE = BASE_DIR / 'content_generation.log'
PROGRESS_FILE = BASE_DIR / 'progress.json'

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# AGNES API配置
import httpx

AGNES_API_KEY = "sk-IoSSbiUZN7jLgeCldgAC3S2JBvocciRQpSfYxWqSry5r0FZk"
AGNES_BASE_URL = "https://apihub.agnes-ai.com/v1/chat/completions"

# 年级处理顺序（从幼儿园开始）
GRADE_ORDER = [
    '幼儿园',
    '一年级上', '一年级下',
    '二年级上', '二年级下',
    '三年级上', '三年级下',
    '四年级上', '四年级下',
    '五年级上', '五年级下',
    '六年级上', '六年级下',
    '七年级上', '七年级下',
    '八年级上', '八年级下',
    '九年级上', '九年级下',
]

# 科目关键词（用于提示词）
SUBJECT_GUIDE = {
    '语文': '语文教科书风格，注重阅读理解、写作技巧和古诗文鉴赏',
    '数学': '数学科目标准表述，公式定理准确，例题解析清晰',
    '英语': '英语教材风格，注重语法准确性和实用表达',
    '物理': '物理概念准确，实验描述清晰，公式推导严谨',
    '化学': '化学方程式准确，实验安全规范，概念定义严谨',
    '生物': '生物学术语准确，生命现象描述客观',
    '历史': '历史事件准确，时间线清晰，人物评价客观',
    '地理': '地理术语准确，地图描述清晰，气候地形描述客观',
    '道德与法治': '价值观正确，法律条文准确，案例贴近生活',
    '体育': '运动规范准确，安全提示到位，技巧描述清晰',
    '音乐': '音乐术语准确，作品描述客观，欣赏引导恰当',
    '美术': '美术术语准确，作品描述客观，技法描述清晰',
    '科学': '科学概念准确，实验描述清晰，观察记录客观',
}

def load_progress():
    """加载进度"""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
    return {'current_grade': '幼儿园', 'completed_grades': [], 'generated_count': 0}

def save_progress(progress):
    """保存进度"""
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')

def generate_content(item):
    """生成单个知识点的內容"""
    grade = item['grade']
    subject = item['subject']
    topic = item['topic']
    
    prompt = f"""请为小学{grade.replace('上','上学期').replace('下','下学期')}的{subject}课程生成知识点"{topic}"的教学内容。

要求：
1. 内容要像标准人教版教材的风格
2. 包含：知识点讲解、生活例子、公式/定理（如有）、常见误区提醒
3. 字数至少700字（如果是教材1000字的标准）
4. 语言简洁准确，不添加臆想内容
5. 分段落，层次清晰

请直接输出教学内容，不要解释。"""
    
    payload = {
        "model": "agnes-2.5-flash",
        "messages": [
            {"role": "system", "content": "你是资深人教版教材编写专家，擅长将教学内容精炼润色。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    headers = {
        "Authorization": f"Bearer {AGNES_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(AGNES_BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        return None

def process_grade(grade, kg_data):
    """处理一个年级的所有知识点"""
    logger.info(f"=== 开始处理 {grade} ===")
    
    # 找出该年级的所有条目
    grade_items = [item for item in kg_data if item['grade'] == grade]
    logger.info(f"{grade} 共有 {len(grade_items)} 个知识点")
    
    generated = 0
    failed = 0
    
    for i, item in enumerate(grade_items, 1):
        topic = item['topic']
        subject = item['subject']
        
        logger.info(f"[{i}/{len(grade_items)}] 处理: {subject} - {topic}")
        
        # 生成内容
        content = generate_content(item)
        
        if content:
            item['content'] = content
            item['explanation'] = content  # 暂时用content填充
            generated += 1
            logger.info(f"  ✓ 成功 ({len(content)}字)")
        else:
            failed += 1
            logger.warning(f"  ✗ 失败")
        
        # 保存进度（每5条保存一次KG和output）
        if i % 5 == 0:
            save_grade_content(grade, kg_data)
            logger.info(f"  已保存进度 ({generated}成功, {failed}失败)")
        
        # 间隔4秒
        if i < len(grade_items):
            time.sleep(4)
    
    logger.info(f"=== {grade} 完成: 成功{generated}, 失败{failed} ===")
    
    # 完成年级后保存进度
    save_grade_content(grade, kg_data)
    progress['current_grade'] = grade
    if grade not in progress['completed_grades']:
        progress['completed_grades'].append(grade)
    progress['generated_count'] = sum(1 for item in kg_data if item.get('content', '').strip())
    save_progress(progress)
    
    return generated, failed

def save_grade_content(grade, kg_data):
    """保存指定年级的内容到文件"""
    for item in kg_data:
        if item['grade'] == grade and item.get('content'):
            filename = f"{grade}-{item['subject']}-{item['topic'].strip()}.json"
            filename = __import__('re').sub(r'[\/\\:*?"<>|]', '-', filename)
            filepath = OUTPUT_DIR / grade / item['subject'] / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')

def review_grade(grade, kg_data):
    """审查一个年级的内容"""
    logger.info(f"=== 审查 {grade} 的内容 ===")
    
    grade_items = [item for item in kg_data if item['grade'] == grade]
    
    issues = []
    for item in grade_items:
        content = item.get('content', '')
        topic = item['topic']
        
        # 检查字数
        if content and len(content) < 500:
            issues.append(f"{item['subject']} - {topic}: 字数不足 ({len(content)}字)")
        elif not content:
            issues.append(f"{item['subject']} - {topic}: 无内容")
    
    if issues:
        logger.warning(f"发现 {len(issues)} 个问题:")
        for issue in issues[:10]:
            logger.warning(f"  - {issue}")
    else:
        logger.info("所有内容审查通过")
    
    return len(issues) == 0

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("知识点内容生成脚本启动")
    logger.info("=" * 50)
    
    # 加载KG
    kg_data = json.load(open(KG_FILE, encoding='utf-8'))
    logger.info(f"KG总条目: {len(kg_data)}")
    
    # 加载进度
    progress = load_progress()
    logger.info(f"当前进度: {progress['current_grade']}")
    logger.info(f"已完成年级: {progress['completed_grades']}")
    
    # 确定起始年级
    start_index = 0
    if progress['completed_grades'] and len(progress['completed_grades']) < len(GRADE_ORDER):
        start_index = GRADE_ORDER.index(progress['completed_grades'][-1]) + 1
    else:
        # 如果进度显示所有年级都完成，但KG还有空内容，从第一个有空内容的年级开始
        for idx, grade in enumerate(GRADE_ORDER):
            grade_items = [item for item in kg_data if item['grade'] == grade]
            has_empty = any(not item.get('content', '').strip() for item in grade_items)
            if has_empty:
                start_index = idx
                break
    
    logger.info(f"从第 {start_index} 个年级开始: {GRADE_ORDER[start_index]}")
    
    # 逐个年级处理
    for i in range(start_index, len(GRADE_ORDER)):
        grade = GRADE_ORDER[i]
        
        # 处理该年级
        generated, failed = process_grade(grade, kg_data)
        
        # 审查
        review_grade(grade, kg_data)
        
        # 更新进度
        progress['current_grade'] = grade
        progress['completed_grades'].append(grade)
        progress['generated_count'] += generated
        save_progress(progress)
        
        logger.info(f"已保存到进度: {grade}")
        
        # 每小时保存一次完整KG
        if i % 5 == 4:
            json.dump(kg_data, open(KG_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            logger.info(f"已保存完整KG ({i+1}/{len(GRADE_ORDER)}年级)")
    
    logger.info("=" * 50)
    logger.info("所有内容生成完成！")
    logger.info("=" * 50)

if __name__ == '__main__':
    main()
