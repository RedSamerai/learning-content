#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补全二年级知识图谱 - 添加缺失的科目和知识点
"""
import json
import time
from pathlib import Path
from collections import defaultdict

base = Path('D:/WorkBuddy/learning-app-research/learning-content')

# 加载现有知识图谱
with open(base / 'knowledge_graph_complete.json', 'r', encoding='utf-8') as f:
    all_topics = json.load(f)

# 检查已有二年级ID
existing_ids = {t['id'] for t in all_topics if '二年级' in t.get('grade', '')}
print(f"已有二年级知识点: {len(existing_ids)}个")

# 人教版二年级上册参考（基于公开教材目录）
# https://www.pep.com.cn/ 人教版教材目录

NEW_TOPICS = []

# ===== 二年级上册 =====
# 语文扩展
chinese_2g1_extra = [
    ("语文二年级上", "语文", "二年级上", "字词进阶", "部首查字法", "学习使用部首查字法查找生字，理解部首含义"),
    ("语文二年级上", "语文", "二年级上", "词语积累", "近义词反义词", "积累常见近义词和反义词，理解词义变化"),
    ("语文二年级上", "语文", "二年级上", "阅读技巧", "分段概括", "学习给文章分段，概括段落大意"),
    ("语文二年级上", "语文", "二年级上", "写作入门", "看图写话进阶", "观察图片，写出完整连贯的话"),
    ("语文二年级上", "语文", "二年级上", "古诗", "绝句赏析", "学习杜甫《绝句》，理解诗意"),
    ("语文二年级上", "语文", "二年级上", "古诗", "望庐山瀑布", "学习李白《望庐山瀑布》，感受山水之美"),
    ("语文二年级上", "语文", "二年级上", "口语交际", "打电话", "学习礼貌用语，学会打电话"),
    ("语文二年级上", "语文", "二年级上", "语文园地", "日积月累", "积累成语、名言警句"),
    # 新增更多知识点
    ("语文二年级上", "语文", "二年级上", "识字", "旋转门识字法", "学习'闷、问、闻'等会意字"),
    ("语文二年级上", "语文", "二年级上", "课文", "场景歌", "学习量词的准确使用"),
    ("语文二年级上", "语文", "二年级上", "课文", "树之歌", "认识树木名称，积累词语"),
    ("语文二年级上", "语文", "二年级上", "课文", "拍手歌", "了解动物习性，保护野生动物"),
    ("语文二年级上", "语文", "二年级上", "课文", "田家四季歌", "了解农家四季生活"),
    ("语文二年级上", "语文", "二年级上", "课文", "坐井观天", "理解寓言故事寓意"),
    ("语文二年级上", "语文", "二年级上", "课文", "寒号鸟", "学习做事要趁早"),
    ("语文二年级上", "语文", "二年级上", "课文", "我要的是葫芦", "理解事物之间的联系"),
    ("语文二年级上", "语文", "二年级上", "课文", "小骆驼", "认识自身价值"),
    ("语文二年级上", "语文", "二年级上", "课文", "雾在哪里", "感受雾天的神秘"),
    ("语文二年级上", "语文", "二年级上", "课文", "雪孩子", "学习乐于助人"),
    ("语文二年级上", "语文", "二年级上", "课文", "狐假虎威", "理解成语寓意"),
]

# 数学扩展
math_2g1_extra = [
    ("数学二年级上", "数学", "二年级上", "几何", "线段认识", "认识线段，会用尺子量长度"),
    ("数学二年级上", "数学", "二年级上", "计算", "进位加法", "掌握两位数加两位数的进位算法"),
    ("数学二年级上", "数学", "二年级上", "计算", "退位减法", "掌握两位数减两位数的退位算法"),
    ("数学二年级上", "数学", "二年级上", "几何", "直角认识", "认识直角，会判断直角"),
    ("数学二年级上", "数学", "二年级上", "计算", "乘法口诀", "背诵1-9的乘法口诀"),
    ("数学二年级上", "数学", "二年级上", "应用", "乘法应用题", "解决生活中的乘法问题"),
    ("数学二年级上", "数学", "二年级上", "几何", "观察物体", "从不同角度观察物体"),
    ("数学二年级上", "数学", "二年级上", "时间", "时分秒进阶", "理解时、分、秒的关系"),
    ("数学二年级上", "数学", "二年级上", "数学广角", "搭配问题", "学习简单的排列组合"),
    ("数学二年级上", "数学", "二年级上", "数学广角", "推理问题", "学习简单的逻辑推理"),
]

# 新增科学科目
science_2g1 = [
    ("科学二年级上", "科学", "二年级上", "植物", "植物生长条件", "了解植物生长需要水、阳光、空气"),
    ("科学二年级上", "科学", "二年级上", "植物", "根茎叶功能", "认识植物根茎叶的作用"),
    ("科学二年级上", "科学", "二年级上", "动物", "常见动物分类", "学习动物的基本分类"),
    ("科学二年级上", "科学", "二年级上", "动物", "动物生活环境", "了解动物与其环境的关系"),
    ("科学二年级上", "科学", "二年级上", "天气", "天气观察记录", "学习观察和记录天气"),
    ("科学二年级上", "科学", "二年级上", "材料", "材料性质", "认识常见材料的性质"),
    ("科学二年级上", "科学", "二年级上", "生活", "节约用水", "了解水资源保护"),
    ("科学二年级上", "科学", "二年级上", "生活", "安全用电", "学习安全用电常识"),
]

# 新增数学科目扩展
math_2g1_more = [
    ("数学二年级上", "数学", "二年级上", "计算", "混合运算", "学习加减混合运算"),
    ("数学二年级上", "数学", "二年级上", "几何", "角的认识", "认识角，比较角的大小"),
    ("数学二年级上", "数学", "二年级上", "应用", "解决问题", "综合运用所学知识解决问题"),
    ("数学二年级上", "数学", "二年级上", "复习", "期中复习", "期中知识梳理"),
    ("数学二年级上", "数学", "二年级上", "复习", "期末复习", "期末知识梳理"),
]

# ===== 二年级下册 =====
chinese_2g2_extra = [
    ("语文二年级下", "语文", "二年级下", "识字", "春天主题识字", "学习关于春天的字词"),
    ("语文二年级下", "语文", "二年级下", "课文", "神州谣", "了解祖国地理概况"),
    ("语文二年级下", "语文", "二年级下", "课文", "传统节日", "了解中国传统节日"),
    ("语文二年级下", "语文", "二年级下", "课文", "贝的故事", "了解汉字文化"),
    ("语文二年级下", "语文", "二年级下", "课文", "中国美食", "了解中华美食文化"),
    ("语文二年级下", "语文", "二年级下", "课文", "彩色的梦", "发挥想象写梦境"),
    ("语文二年级下", "语文", "二年级下", "课文", "枫树上的枫叶", "学习童话写法"),
    ("语文二年级下", "语文", "二年级下", "古诗", "晓出净慈寺送林子方", "学习描写西湖的诗句"),
    ("语文二年级下", "语文", "二年级下", "古诗", "队队家", "学习描写农村风光"),
    ("语文二年级下", "语文", "二年级下", "写话", "写自己喜欢的动物", "学习观察和描写动物"),
    ("语文二年级下", "语文", "二年级下", "口语交际", "推荐一部动画片", "学习清楚表达推荐理由"),
    ("语文二年级下", "语文", "二年级下", "语文园地", "汉字文化", "了解汉字演变"),
]

math_2g2_extra = [
    ("数学二年级下", "数学", "二年级下", "计算", "表内除法", "掌握用乘法口诀求商"),
    ("数学二年级下", "数学", "二年级下", "几何", "图形的运动", "认识平移和旋转"),
    ("数学二年级下", "数学", "二年级下", "数与代数", "万以内数的认识", "认识更大的数"),
    ("数学二年级下", "数学", "二年级下", "计算", "万以内加减法", "掌握万以内数的加减"),
    ("数学二年级下", "数学", "二年级下", "量与计量", "克和千克", "认识质量单位"),
    ("数学二年级下", "数学", "二年级下", "统计", "数据收集整理", "学习简单的统计方法"),
    ("数学二年级下", "数学", "二年级下", "数学广角", "找规律", "发现图形和数字的规律"),
    ("数学二年级下", "数学", "二年级下", "应用", "解决问题", "综合运用除法解决问题"),
]

science_2g2 = [
    ("科学二年级下", "科学", "二年级下", "植物", "种子发芽", "观察种子发芽过程"),
    ("科学二年级下", "科学", "二年级下", "植物", "植物生长记录", "学习制作生长记录表"),
    ("科学二年级下", "科学", "二年级下", "动物", "蚕宝宝", "观察养蚕过程"),
    ("科学二年级下", "科学", "二年级下", "动物", "动物本领", "了解动物的生存本领"),
    ("科学二年级下", "科学", "二年级下", "物质", "溶解", "认识溶解现象"),
    ("科学二年级下", "科学", "二年级下", "物质", "分离与混合", "学习分离混合物的方法"),
    ("科学二年级下", "科学", "二年级下", "地球", "磁铁魔法", "认识磁铁的性质"),
    ("科学二年级下", "科学", "二年级下", "技术", "做指南针", "动手制作指南针"),
]

# 合并所有新知识点
all_new = chinese_2g1_extra + math_2g1_extra + science_2g1 + math_2g1_more + chinese_2g2_extra + math_2g2_extra + science_2g2

print(f"\n准备添加 {len(all_new)} 个新知识点")
print("二年级上语文补充:", len(chinese_2g1_extra))
print("二年级上数学补充:", len(math_2g1_extra) + len(math_2g1_more))
print("二年级上科学新增:", len(science_2g1))
print("二年级下语文补充:", len(chinese_2g2_extra))
print("二年级下数学补充:", len(math_2g2_extra))
print("二年级下科学新增:", len(science_2g2))

# 生成新知识点ID
max_id_2g1 = max((int(t['id'].split('_')[-1]) for t in all_topics if '二年级上' in t.get('grade', '') and t['id'].startswith('语文')), default=0)
max_id_2g2 = max((int(t['id'].split('_')[-1]) for t in all_topics if '二年级下' in t.get('grade', '') and t['id'].startswith('语文')), default=0)
max_math_2g1 = max((int(t['id'].split('_')[-1]) for t in all_topics if '二年级上' in t.get('grade', '') and t['id'].startswith('数学')), default=0)
max_math_2g2 = max((int(t['id'].split('_')[-1]) for t in all_topics if '二年级下' in t.get('grade', '') and t['id'].startswith('数学')), default=0)
max_science_2g1 = max((int(t['id'].split('_')[-1]) for t in all_topics if '二年级上' in t.get('grade', '') and t['id'].startswith('科学')), default=0)
max_science_2g2 = max((int(t['id'].split('_')[-1]) for t in all_topics if '二年级下' in t.get('grade', '') and t['id'].startswith('科学')), default=0)

print(f"\n当前最大ID: 语文2g1={max_id_2g1}, 语文2g2={max_id_2g2}, 数学2g1={max_math_2g1}, 数学2g2={max_math_2g2}, 科学2g1={max_science_2g1}, 科学2g2={max_science_2g2}")

# 添加新知识点到知识图谱
counter_2g1_chinese = max_id_2g1
counter_2g2_chinese = max_id_2g2
counter_2g1_math = max_math_2g1
counter_2g2_math = max_math_2g2
counter_2g1_science = max_science_2g1
counter_2g2_science = max_science_2g2

for topic in all_new:
    prefix, subject, grade, chapter, title, description = topic
    
    if '二年级上' in grade and subject == '语文':
        counter_2g1_chinese += 1
        new_id = f"{subject}二年级上{counter_2g1_chinese:04d}"
    elif '二年级上' in grade and subject == '数学':
        counter_2g1_math += 1
        new_id = f"{subject}二年级上{counter_2g1_math:04d}"
    elif '二年级上' in grade and subject == '科学':
        counter_2g1_science += 1
        new_id = f"{subject}二年级上{counter_2g1_science:04d}"
    elif '二年级下' in grade and subject == '语文':
        counter_2g2_chinese += 1
        new_id = f"{subject}二年级下{counter_2g2_chinese:04d}"
    elif '二年级下' in grade and subject == '数学':
        counter_2g2_math += 1
        new_id = f"{subject}二年级下{counter_2g2_math:04d}"
    elif '二年级下' in grade and subject == '科学':
        counter_2g2_science += 1
        new_id = f"{subject}二年级下{counter_2g2_science:04d}"
    else:
        continue
    
    # 检查是否已存在
    if new_id in existing_ids:
        print(f"跳过已存在: {new_id}")
        continue
    
    new_topic = {
        "id": new_id,
        "subject": subject,
        "grade": grade,
        "chapter": chapter,
        "topic": title,
        "description": description,
        "explanation": "",
        "example": "",
        "key_points": ""
    }
    
    all_topics.append(new_topic)
    existing_ids.add(new_id)

# 保存更新后的知识图谱
output_path = base / 'knowledge_graph_complete_updated.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_topics, f, ensure_ascii=False, indent=2)

print(f"\n✅ 知识图谱已更新:")
print(f"   原始: {len(all_topics) - len(all_new)} 个知识点")
print(f"   新增: {len(all_new)} 个知识点")
print(f"   总计: {len(all_topics)} 个知识点")

# 统计更新后的二年级数量
updated_2g = [t for t in all_topics if '二年级' in t.get('grade', '')]
by_subject = defaultdict(int)
for t in updated_2g:
    by_subject[t.get('subject', '未知')] += 1

print(f"\n更新后二年级分布:")
for subject, count in sorted(by_subject.items()):
    print(f"  {subject}: {count}个")
print(f"  总计: {len(updated_2g)}个")
