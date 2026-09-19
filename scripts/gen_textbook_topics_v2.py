#!/usr/bin/env python3
"""
基于人教版教材真实目录生成知识点清单
数据来源：公开教材目录
"""
import json
from pathlib import Path
from datetime import datetime

# 人教版教材知识点清单（基于2024最新教材目录）
TEXTBOOK_TOPICS = {
    # ===== 幼儿园（3-6岁，五大领域）=====
    "kindergarten": {
        "health": ["认识五官", "保护眼睛", "正确洗手", "安全常识", "情绪管理"],
        "language": ["听故事", "讲故事", "看图说话", "诗歌朗诵", "前识字准备"],
        "social": ["认识自己", "家庭关系", "幼儿园规则", "朋友相处", "传统节日"],
        "science": ["数数1-10", "比较大小", "认识形状", "季节变化", "动植物观察"],
        "art": ["涂鸦绘画", "涂色", "撕纸", "黏土手工", "音乐律动"]
    },
    
    # ===== 幼小衔接 =====
    "kindergarten_transition": {
        "math": ["10以内数数", "10以内加减法", "认识图形", "比较长短", "分类排序"],
        "chinese": ["认识基本汉字", "拼音认读", "看图说话", "简单表达", "书写姿势"],
        "science": ["观察植物", "观察动物", "天气变化", "简单实验", "安全教育"]
    },
    
    # ===== 小学数学（1-6年级，基于人教版目录）=====
    "primary_math": {
        "一年级上": ["数一数", "比一比", "1-5的认识", "认识物体", "6-10的认识", "11-20各数", "认识钟表", "20以内进位加法"],
        "一年级下": ["位置", "20以内退位减法", "图形的拼组", "100以内数的认识", "认识人民币", "100以内加减法", "认识时间", "找规律", "统计"],
        "二年级上": ["长度单位", "100以内加减法", "角的初步认识", "表内乘法一", "观察物体", "表内乘法二", "统计", "数学广角"],
        "二年级下": ["解决问题", "表内除法一", "图形与变换", "表内除法二", "万以内数的认识", "克与千克", "万以内加减法", "统计", "找规律"],
        "三年级上": ["测量", "万以内加减法二", "四边形", "有余数的除法", "时分值秒", "多位数乘一位数", "分数的初步认识", "可能性", "数学广角"],
        "三年级下": ["位置与方向", "除数是一位数的除法", "统计", "年月日", "两位数乘两位数", "面积", "小数的初步认识", "数学广角"],
        "四年级上": ["大数的认识", "角的度量", "三位数乘两位数", "平行四边形和梯形", "除数是两位数的除法", "统计", "数学广角", "数学广角"],
        "四年级下": ["四则运算", "观察物体二", "运算定律", "小数的意义和性质", "三角形", "小数的加法和减法", "图形的运动", "平均数与条形统计图", "数学广角", "数学广角"],
        "五年级上": ["小数乘法", "位置", "小数除法", "可能性", "整数混合运算", "简易方程", "多边形的面积", "植树问题"],
        "五年级下": ["观察物体三", "因数与倍数", "长方体和正方体", "分数的意义和性质", "图形的运动三", "分数的加法和减法", "找次品", "数学广角"],
        "六年级上": ["分数乘法", "位置与方向", "分数除法", "比", "圆", "百分数", "扇形统计图", "数学广角", "数学广角"],
        "六年级下": ["负数", "百分数二", "圆柱与圆锥", "比例", "数学广角", "整理与复习"]
    },
    
    # ===== 初中数学（7-9年级）=====
    "junior_math": {
        "七年级上": ["有理数", "整式的加减", "一元一次方程", "几何图形初步"],
        "七年级下": ["相交线与平行线", "实数", "平面直角坐标系", "二元一次方程组", "不等式与不等式组", "数据的收集、整理与描述"],
        "八年级上": ["三角形", "全等三角形", "轴对称", "整式的乘法与因式分解", "分式"],
        "八年级下": ["二次根式", "勾股定理", "平行四边形", "一次函数", "数据的分析"],
        "九年级上": ["一元二次方程", "二次函数", "旋转", "圆", "概率初步"],
        "九年级下": ["反比例函数", "相似", "锐角三角函数", "投影与视图"]
    },
    
    # ===== 初中语文（7-9年级）=====
    "junior_chinese": {
        "七年级上": ["春", "济南的冬天", "雨的四季", "古代诗歌四首", "寓言四则", "《论语》十二章", "写作：学会记事", "综合性学习：有朋自远方来"],
        "七年级下": ["邓稼先", "闻一多先生的说和做", "黄河颂", "最后一课", "阿长与《山海经》", "写作：写出人物的个性", "综合性学习：天下国家"],
        "八年级上": ["消息二则", "首届国际电影节报道", "一着惊海天", "《史记》二则", "诗词五首", "写作：学会仿写", "综合性学习：怎样搜集资料"],
        "八年级下": ["社戏", "回延安", "灯笼", "《诗经》二首", "写作：模仿写作", "综合性学习：古诗苑漫步"],
        "九年级上": ["沁园春·雪", "我爱这土地", "乡愁", "你是人间的四月天", "我看", "写作：审题立意", "修辞与语法", "名著导读：艾青诗选"],
        "九年级下": ["祖国啊，我亲爱的祖国", "梅岭三章", "短诗五首", "写作：创意表达", "综合性学习：岁月如歌"]
    },
    
    # ===== 初中英语（7-9年级）=====
    "junior_english": {
        "七年级上": ["Starter Units", "Unit 1-4 (自我介绍、家庭、物品、日常活动)"],
        "七年级下": ["Unit 5-12 (爱好、地点、食物、时间、 Clothes、季节、天气、节日)"],
        "八年级上": ["Unit 1-10 (形容词比较级、动词不定式、现在完成时、条件状语从句)"],
        "八年级下": ["Unit 11-18 (过去进行时、定语从句、宾语从句、反意疑问句)"],
        "九年级全一册": ["Unit 1-15 (宾语从句、定语从句、过去完成时、被动语态、感叹句、动词不定式)"]
    },
    
    # ===== 初中物理（8-9年级）=====
    "junior_physics": {
        "八年级上": ["机械运动", "声现象", "物态变化", "光现象", "透镜及其应用", "质量与密度"],
        "八年级下": ["力", "牛顿第一定律", "压强", "浮力", "功和机械能", "简单机械"],
        "九年级全一册": ["内能", "电热", "家庭电路", "能源与可持续发展"]
    },
    
    # ===== 初中化学（9年级）=====
    "junior_chemistry": {
        "九年级上": ["化学是一门以实验为基础的科学", "我们周围的空气", "物质构成的奥秘", "自然界的水", "化学方程式", "碳和碳的氧化物", "燃料及其利用"],
        "九年级下": ["金属和金属材料", "酸和碱", "盐 化肥", "化学与生活"]
    },
    
    # ===== 初中生物（7-9年级）=====
    "junior_biology": {
        "七年级上": ["植物细胞", "动物细胞", "细胞的生活", "细胞分裂分化", "没有细胞结构的病毒", "生物圈", "生物体的结构层次", "植物的一生", "动物的一生"],
        "七年级下": ["人的由来", "人体的营养", "人体的呼吸", "人体内物质的运输", "人体废物的排出", "人体生命活动的调节", "人类活动对生物圈的影响"],
        "八年级上": ["微生物", "动物的运动", "动物的行为", "生物的多样性", "生物技术"],
        "八年级下": ["生殖发育遗传", "生命的起源与进化", "健康地生活", "传染病与免疫", "用药与急救", "了解自己增进健康"]
    },
    
    # ===== 初中历史（7-9年级）=====
    "junior_history": {
        "七年级上": ["史前时期", "夏商周", "秦汉", "三国两晋南北朝"],
        "七年级下": ["隋唐", "宋元", "明清"],
        "八年级上": ["近代探索", "新民主主义革命", "社会主义建设", "改革开放"],
        "八年级下": ["新中国成立", "社会主义制度建立", "建设道路探索", "改革开放"],
        "九年级上": ["古代文明", "中古世界", "资本主义萌芽", "启蒙运动"],
        "九年级下": ["两次世界大战", "冷战", "战后世界", "现代文明"]
    },
    
    # ===== 初中道德与法治（7-9年级）=====
    "junior_civics": {
        "七年级上": ["成长的节拍", "友谊的天空", "师长情谊", "生命的思考"],
        "七年级下": ["青春时光", "情绪管理", "情感培育", "法律意识"],
        "八年级上": ["社会生活", "责任与担当", "社会规则", "秩序维护"],
        "八年级下": ["宪法精神", "公民权利", "国家机构", "法治建设"],
        "九年级上": ["国情国策", "民主政治", "文化传承", "生态文明建设"],
        "九年级下": ["少年当自强", "世界舞台", "中国担当", "未来选择"]
    },
    
    # ===== 初中地理（7-9年级）=====
    "junior_geography": {
        "七年级上": ["地球地图", "陆地海洋", "天气气候", "居民聚落"],
        "七年级下": ["亚洲", "东南亚", "中东", "欧洲西部", "撒哈拉以南", "极地"],
        "八年级上": ["中国地理", "自然环境", "自然资源", "经济发展"],
        "八年级下": ["区域差异", "北方地区", "南方地区", "西北地区", "青藏地区"]
    },
    
    # ===== 小学科学（3-6年级）=====
    "primary_science": {
        "三年级": ["植物的生长", "动物的生活", "水的三态", "磁铁的性质", "声音的产生", "光现象", "材料分类", "简单电路"],
        "四年级": ["植物繁殖", "昆虫世界", "天气观测", "岩石矿物", "电磁现象", "人体系统", "简单机械", "声音与光"],
        "五年级": ["生态系统", "生物适应", "太阳系", "地球运动", "能源转换", "环境保护", "杠杆滑轮", "遗传变异"],
        "六年级": ["宇宙探索", "地球变化", "能源危机", "生态环境", "人工智能", "新材料", "航天技术", "可持续发展"]
    }
}

# 生成完整知识点清单
def generate_all_topics():
    """生成所有知识点"""
    all_topics = []
    
    # 幼儿园
    for area, topics in TEXTBOOK_TOPICS["kindergarten"].items():
        for topic in topics:
            all_topics.append({
                "id": f"kind_{area}_{len([t for t in all_topics if t.get('subject')==area])}",
                "grade": "幼儿园",
                "level": "幼儿园",
                "subject": area,
                "topic": topic,
                "content": ""
            })
    
    # 幼小衔接
    for area, topics in TEXTBOOK_TOPICS["kindergarten_transition"].items():
        for topic in topics:
            all_topics.append({
                "id": f"kt_{area}_{len([t for t in all_topics if t.get('subject')==area])}",
                "grade": "幼小衔接",
                "level": "幼小衔接",
                "subject": area,
                "topic": topic,
                "content": ""
            })
    
    # 小学数学
    for grade, topics in TEXTBOOK_TOPICS["primary_math"].items():
        for topic in topics:
            all_topics.append({
                "id": f"pm_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "数学",
                "topic": topic,
                "content": ""
            })
    
    # 初中数学
    for grade, topics in TEXTBOOK_TOPICS["junior_math"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jm_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "数学",
                "topic": topic,
                "content": ""
            })
    
    # 初中语文
    for grade, topics in TEXTBOOK_TOPICS["junior_chinese"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jc_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "语文",
                "topic": topic,
                "content": ""
            })
    
    # 初中英语
    for grade, topics in TEXTBOOK_TOPICS["junior_english"].items():
        for topic in topics:
            all_topics.append({
                "id": f"je_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "英语",
                "topic": topic,
                "content": ""
            })
    
    # 初中物理
    for grade, topics in TEXTBOOK_TOPICS["junior_physics"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jp_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "物理",
                "topic": topic,
                "content": ""
            })
    
    # 初中化学
    for grade, topics in TEXTBOOK_TOPICS["junior_chemistry"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jch_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "化学",
                "topic": topic,
                "content": ""
            })
    
    # 初中生物
    for grade, topics in TEXTBOOK_TOPICS["junior_biology"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jb_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "生物",
                "topic": topic,
                "content": ""
            })
    
    # 初中历史
    for grade, topics in TEXTBOOK_TOPICS["junior_history"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jh_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "历史",
                "topic": topic,
                "content": ""
            })
    
    # 初中道德与法治
    for grade, topics in TEXTBOOK_TOPICS["junior_civics"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jci_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "道德与法治",
                "topic": topic,
                "content": ""
            })
    
    # 初中地理
    for grade, topics in TEXTBOOK_TOPICS["junior_geography"].items():
        for topic in topics:
            all_topics.append({
                "id": f"jg_{grade.replace('年级','')}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "地理",
                "topic": topic,
                "content": ""
            })
    
    # 小学科学
    for grade, topics in TEXTBOOK_TOPICS["primary_science"].items():
        for topic in topics:
            all_topics.append({
                "id": f"ps_{grade}_{topic[:2]}",
                "grade": grade,
                "level": grade,
                "subject": "科学",
                "topic": topic,
                "content": ""
            })
    
    return all_topics

# 主程序
if __name__ == "__main__":
    topics = generate_all_topics()
    
    # 保存
    output_path = Path("knowledge_graph_textbook.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生成完成: {len(topics)} 个知识点")
    print(f"\n分布统计:")
    grade_count = {}
    for t in topics:
        g = t["grade"]
        grade_count[g] = grade_count.get(g, 0) + 1
    for g, c in sorted(grade_count.items()):
        print(f"  {g}: {c}个")
