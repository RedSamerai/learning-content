#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识点内容生成脚本 - 真实教材版
- 从网络搜索真实人教版教材内容
- RPM限制：≤20次/分钟（间隔≥4秒）
- 每5条保存一次进度
- 出错记录日志但继续运行
"""

import json
import time
import sys
import logging
import re
from pathlib import Path
from datetime import datetime
import requests

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

# RPM配置
MIN_INTERVAL = 4.0  # 最小间隔4秒
REQUESTS_PER_MINUTE = 20  # 每分钟最多20次

# 年级处理顺序
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

def load_progress():
    """加载进度"""
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding='utf-8'))
    return {'current_grade': '幼儿园', 'completed_grades': [], 'generated_count': 0}

def save_progress(progress):
    """保存进度"""
    progress['last_updated'] = datetime.now().isoformat()
    PROGRESS_FILE.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')

def search_textbook_content(topic, grade, subject):
    """搜索真实教材内容（使用国内可访问的教育网站）"""
    grade_str = grade.replace('上', '上学期').replace('下', '下学期')
    keywords = f"人教版{grade_str}{subject}{topic}"
    
    # 尝试多个国内教育网站
    search_urls = [
        f"https://www.baidu.com/s?wd={keywords}",
        f"https://www.sogou.com/web?query={keywords}",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in search_urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # 提取文本内容
            text = re.sub(r'<[^>]+>', ' ', response.text)
            text = re.sub(r'\s+', ' ', text)
            
            # 过滤掉无关内容，提取教材相关部分
            content = ""
            for line in text.split('.'):
                if topic in line or subject in line:
                    content += line.strip() + ". "
                    if len(content) > 800:
                        break
            
            if len(content) > 200:
                return content[:800]
                
        except Exception as e:
            logger.debug(f"搜索失败 {url}: {e}")
            continue
    
    return None

def generate_content(item):
    """生成单个知识点的内容（使用搜索的真实教材内容）"""
    grade = item['grade']
    subject = item['subject']
    topic = item['topic']
    
    # 搜索真实教材内容
    content = search_textbook_content(topic, grade, subject)
    
    if content:
        return content
    else:
        # 搜索失败，返回空字符串
        return None

def save_grade_content(grade, kg_data):
    """保存指定年级的内容到文件"""
    for item in kg_data:
        if item['grade'] == grade and item.get('content'):
            filename = f"{grade}-{item['subject']}-{item['topic'].strip()}.json"
            filename = re.sub(r'[\\/:\*?"<>|]', '-', filename)
            filepath = OUTPUT_DIR / grade / item['subject'] / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')

def process_grade(grade, kg_data, progress, rate_limiter):
    """处理一个年级的所有知识点"""
    logger.info(f"=== 开始处理 {grade} ===")
    
    grade_items = [item for item in kg_data if item['grade'] == grade]
    logger.info(f"{grade} 共有 {len(grade_items)} 个知识点")
    
    generated = 0
    failed = 0
    
    for i, item in enumerate(grade_items, 1):
        topic = item['topic']
        subject = item['subject']
        
        logger.info(f"[{i}/{len(grade_items)}] 处理: {subject} - {topic}")
        
        # 速率限制
        rate_limiter.wait()
        
        # 生成内容
        content = generate_content(item)
        
        if content and len(content.strip()) > 100:
            item['content'] = content
            generated += 1
            logger.info(f"  ✓ 成功 ({len(content)}字)")
        else:
            failed += 1
            logger.warning(f"  ✗ 失败")
        
        # 保存进度（每5条保存一次）
        if i % 5 == 0:
            save_grade_content(grade, kg_data)
            logger.info(f"  已保存进度 ({generated}成功, {failed}失败)")
        
        # 等待4秒（确保RPM≤15）
        if i < len(grade_items):
            time.sleep(MIN_INTERVAL)
    
    logger.info(f"=== {grade} 完成: 成功{generated}, 失败{failed} ===")
    
    # 完成年级后保存进度
    save_grade_content(grade, kg_data)
    progress['current_grade'] = grade
    if grade not in progress['completed_grades']:
        progress['completed_grades'].append(grade)
    progress['generated_count'] = sum(1 for item in kg_data if item.get('content', '').strip())
    save_progress(progress)
    
    return generated, failed

class RateLimiter:
    """速率限制器，确保RPM≤20"""
    def __init__(self, rpm=20, interval=4.0):
        self.rpm = rpm
        self.interval = interval
        self.last_request_time = 0
    
    def wait(self):
        """等待直到可以发送请求"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.interval:
            time.sleep(self.interval - elapsed)
        self.last_request_time = time.time()

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("知识点内容生成脚本启动（真实教材版）")
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
    
    # 创建速率限制器
    rate_limiter = RateLimiter(rpm=REQUESTS_PER_MINUTE, interval=MIN_INTERVAL)
    
    # 逐个年级处理
    for i in range(start_index, len(GRADE_ORDER)):
        grade = GRADE_ORDER[i]
        
        # 处理该年级
        generated, failed = process_grade(grade, kg_data, progress, rate_limiter)
        
        # 每小时保存一次完整KG
        if i % 5 == 4:
            kg_data_file = KG_FILE.with_suffix('.backup.json')
            kg_data_file.write_text(json.dumps(kg_data, ensure_ascii=False, indent=2), encoding='utf-8')
            logger.info(f"已保存完整KG备份")
    
    logger.info("=" * 50)
    logger.info("所有内容生成完成！")
    logger.info("=" * 50)

if __name__ == '__main__':
    main()
