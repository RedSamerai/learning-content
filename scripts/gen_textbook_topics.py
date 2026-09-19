#!/usr/bin/env python3
"""
基于人教版教材真实目录生成知识点
数据来源：公开教材目录
"""
import json
from pathlib import Path
from datetime import datetime

# 基于人教版教材真实目录的知识点清单
TEXTBOOK_TOPICS = {
    # ===== 小学数学（基于人教版目录） =====
    "math/一年级上": [
        {"topic_id": "math_g1_count", "name": "数一数", "focus": "1-5数字认识"},
        {"topic_id": "math_g1_compare", "name": "比多少", "focus": "一一对应比较"},
        {"topic_id": "math_g1_recognize", "name": "1-5的认识", "focus": "读写与大小"},
        {"topic_id": "math_g1_add", "name": "1-5的加减法", "focus": "加法减法计算"},
        {"topic_id": "math_g1_shape", "name": "认识图形", "focus": "长方体正方体"},
        {"topic_id": "math_g1_position", "name": "位置", "focus": "上下前后左右"},
        {"topic_id": "math_g1_clock", "name": "认识钟表", "focus": "整时半时"},
        {"topic_id": "math_g1_20calc", "name": "20以内进位加法", "focus": "凑十法"},
    ],
    "math/一年级下": [
        {"topic_id": "math_g1_shape2", "name": "认识图形(二)", "focus": "三角形平行四边形"},
        {"topic_id": "math_g1_sub", "name": "20以内退位减法", "focus": "破十法"},
        {"topic_id": "math_g1_sort", "name": "分类与整理", "focus": "分类统计"},
        {"topic_id": "math_g1_num100", "name": "100以内数的认识", "focus": "数数读写"},
        {"topic_id": "math_g1_money", "name": "认识人民币", "focus": "元角分"},
        {"topic_id": "math_g1_add100", "name": "100以内加减法", "focus": "口算笔算"},
        {"topic_id": "math_g1_pattern", "name": "找规律", "focus": "图形与数字规律"},
    ],
    "math/二年级上": [
        {"topic_id": "math_g2_length", "name": "长度单位", "focus": "厘米米"},
        {"topic_id": "math_g2_add", "name": "100以内加法", "focus": "进位加法"},
        {"topic_id": "math_g2_angle", "name": "角的初步认识", "focus": "直角锐角钝角"},
        {"topic_id": "math_g2_multi", "name": "表内乘法(一)", "focus": "乘法口诀前半"},
        {"topic_id": "math_g2_observe", "name": "观察物体", "focus": "从不同方向看"},
        {"topic_id": "math_g2_multi2", "name": "表内乘法(二)", "focus": "乘法口诀后半"},
        {"topic_id": "math_g2_time", "name": "认识时间", "focus": "时分秒"},
        {"topic_id": "math_g2_combo", "name": "数学广角搭配", "focus": "排列组合入门"},
    ],
    "math/二年级下": [
        {"topic_id": "math_g2_data", "name": "数据收集整理", "focus": "统计图表"},
        {"topic_id": "math_g2_div1", "name": "表内除法(一)", "focus": "除法意义"},
        {"topic_id": "math_g2_move", "name": "图形的运动", "focus": "平移旋转对称"},
        {"topic_id": "math_g2_div2", "name": "表内除法(二)", "focus": "用口诀求商"},
        {"topic_id": "math_g2_mixed", "name": "混合运算", "focus": "四则混合"},
        {"topic_id": "math_g2_remain", "name": "有余数的除法", "focus": "余数概念"},
        {"topic_id": "math_g2_num1000", "name": "万以内数的认识", "focus": "大数认识"},
        {"topic_id": "math_g2_weight", "name": "克和千克", "focus": "质量单位"},
        {"topic_id": "math_g2_reason", "name": "数学广角推理", "focus": "简单推理"},
    ],
    "math/三年级上": [
        {"topic_id": "math_g3_time", "name": "时、分、秒", "focus": "时间单位换算"},
        {"topic_id": "math_g3_add1", "name": "万以内的加法", "focus": "三位数加法"},
        {"topic_id": "math_g3_sub1", "name": "万以内的减法", "focus": "三位数减法"},
        {"topic_id": "math_g3_measure", "name": "测量", "focus": "毫米千米吨"},
        {"topic_id": "math_g3_mul", "name": "多位数乘一位数", "focus": "乘法计算"},
        {"topic_id": "math_g3_shape", "name": "长方形正方形", "focus": "周长计算"},
        {"topic_id": "math_g3_frac", "name": "分数的初步认识", "focus": "几分之一"},
        {"topic_id": "math_g3_set", "name": "数学广角集合", "focus": "集合思想"},
    ],
    "math/三年级下": [
        {"topic_id": "math_g3_pos", "name": "位置与方向", "focus": "东南西北"},
        {"topic_id": "math_g3_div1", "name": "除数是一位数的除法", "focus": "口算笔算"},
        {"topic_id": "math_g3_stat", "name": "复式统计表", "focus": "数据整理"},
        {"topic_id": "math_g3_mul2", "name": "两位数乘两位数", "focus": "乘法进阶"},
        {"topic_id": "math_g3_area", "name": "面积", "focus": "面积概念计算"},
        {"topic_id": "math_g3_date", "name": "年、月、日", "focus": "时间单位"},
        {"topic_id": "math_g3_dec", "name": "小数的初步认识", "focus": "小数读写"},
        {"topic_id": "math_g3_match", "name": "数学广角搭配", "focus": "排列组合"},
    ],
    "math/四年级上": [
        {"topic_id": "math_g4_big", "name": "大数的认识", "focus": "亿以内数"},
        {"topic_id": "math_g4_unit", "name": "公顷和平方千米", "focus": "面积单位"},
        {"topic_id": "math_g4_angle", "name": "角的度量", "focus": "量角画角"},
        {"topic_id": "math_g4_mul", "name": "三位数乘两位数", "focus": "乘法计算"},
        {"topic_id": "math_g4_para", "name": "平行四边形和梯形", "focus": "图形特征"},
        {"topic_id": "math_g4_div", "name": "除数是两位数的除法", "focus": "除法计算"},
        {"topic_id": "math_g4_bar", "name": "条形统计图", "focus": "统计图表"},
        {"topic_id": "math_g4_optimize", "name": "数学广角优化", "focus": "优化思想"},
    ],
    "math/四年级下": [
        {"topic_id": "math_g4_calc", "name": "四则运算", "focus": "运算顺序"},
        {"topic_id": "math_g4_view", "name": "观察物体(二)", "focus": "视图"},
        {"topic_id": "math_g4_law", "name": "运算定律", "focus": "加减乘除定律"},
        {"topic_id": "math_g4_dec", "name": "小数的意义和性质", "focus": "小数概念"},
        {"topic_id": "math_g4_triangle", "name": "三角形", "focus": "特性分类"},
        {"topic_id": "math_g4_decimal", "name": "小数的加法和减法", "focus": "小数计算"},
        {"topic_id": "math_g4_motion", "name": "图形的运动(二)", "focus": "轴对称平移"},
        {"topic_id": "math_g4_avg", "name": "平均数与条形统计图", "focus": "数据统计"},
        {"topic_id": "math_g4_hare", "name": "数学广角鸡兔同笼", "focus": "假设法"},
    ],
    "math/五年级上": [
        {"topic_id": "math_g5_decimal", "name": "小数乘法", "focus": "小数乘法规则"},
        {"topic_id": "math_g5_position", "name": "位置", "focus": "数对"},
        {"topic_id": "math_g5_decimal_div", "name": "小数除法", "focus": "小数除法计算"},
        {"topic_id": "math_g5_simple", "name": "简易方程", "focus": "用字母表示数"},
        {"topic_id": "math_g5_poly", "name": "多边形面积", "focus": "平行四边形三角形梯形"},
        {"topic_id": "math_g5_可能性", "name": "可能性", "focus": "事件概率"},
        {"topic_id": "math_g5_search", "name": "数学广角植树问题", "focus": "间隔问题"},
    ],
    "math/五年级下": [
        {"topic_id": "math_g5_fraction", "name": "分数的意义和性质", "focus": "分数概念"},
        {"topic_id": "math_g5_calc", "name": "分数的加法和减法", "focus": "分数计算"},
        {"topic_id": "math_g5_volume", "name": "长方体和正方体", "focus": "体积表面积"},
        {"topic_id": "math_g5_mass", "name": "分数的乘法和除法", "focus": "分数乘除"},
        {"topic_id": "math_g5_ratio", "name": "比和比例", "focus": "比的意义"},
        {"topic_id": "math_g5_motion", "name": "图形的运动(三)", "focus": "旋转"},
        {"topic_id": "math_g5_stat", "name": "统计", "focus": "折线统计图"},
        {"topic_id": "math_g5_number", "name": "数学广角找次品", "focus": "优化思想"},
    ],
    "math/六年级上": [
        {"topic_id": "math_g6_frac", "name": "分数乘法", "focus": "分数乘法意义"},
        {"topic_id": "math_g6_pos", "name": "位置与方向", "focus": "方向距离"},
        {"topic_id": "math_g6_frac_div", "name": "分数除法", "focus": "分数除法计算"},
        {"topic_id": "math_g6_ratio", "name": "比", "focus": "比的意义性质"},
        {"topic_id": "math_g6_circle", "name": "圆", "focus": "周长面积"},
        {"topic_id": "math_g6_percent", "name": "百分数", "focus": "百分数意义"},
        {"topic_id": "math_g6_stat", "name": "扇形统计图", "focus": "统计图选择"},
        {"topic_id": "math_g6_number", "name": "数学广角数与形", "focus": "数形结合"},
    ],
    "math/六年级下": [
        {"topic_id": "math_g6_neg", "name": "负数", "focus": "负数认识"},
        {"topic_id": "math_g6_ratio2", "name": "比例", "focus": "比例性质应用"},
        {"topic_id": "math_g6_geometry", "name": "立体几何", "focus": "圆柱圆锥"},
        {"topic_id": "math_g6_stat", "name": "统计与概率", "focus": "统计推断"},
        {"topic_id": "math_g6_review", "name": "小学数学总复习", "focus": "知识梳理"},
    ],
    
    # ===== 初中数学（基于人教版目录） =====
    "math/七年级上": [
        {"topic_id": "math_j7_rational", "name": "有理数", "focus": "正负数加减乘除"},
        {"topic_id": "math_j7_introduce", "name": "整式的加减", "focus": "合并同类项"},
        {"topic_id": "math_j7_linear", "name": "一元一次方程", "focus": "解方程应用题"},
        {"topic_id": "math_j7_geometry", "name": "几何图形初步", "focus": "点线面体"},
    ],
    "math/七年级下": [
        {"topic_id": "math_j7_real", "name": "实数", "focus": "平方立方根"},
        {"topic_id": "math_j7_system", "name": "二元一次方程组", "focus": "消元法"},
        {"topic_id": "math_j7_ineq", "name": "不等式与不等式组", "focus": "不等式性质解法"},
        {"topic_id": "math_j7_coordinate", "name": "平面直角坐标系", "focus": "坐标点位置"},
        {"topic_id": "math_j7_translation", "name": "平移与旋转", "focus": "图形变换"},
    ],
    "math/八年级上": [
        {"topic_id": "math_j8_triangle", "name": "三角形", "focus": "内角外角性质"},
        {"topic_id": "math_j8_congruent", "name": "全等三角形", "focus": "判定与性质"},
        {"topic_id": "math_j8_ineq", "name": "轴对称与等腰三角形", "focus": "对称性质"},
        {"topic_id": "math_j8_pow", "name": "整式的乘除与因式分解", "focus": "乘法公式"},
        {"topic_id": "math_j8_frac", "name": "分式", "focus": "分式运算"},
        {"topic_id": "math_j8_root", "name": "二次根式", "focus": "根式化简"},
    ],
    "math/八年级下": [
        {"topic_id": "math_j8_linear", "name": "一次函数", "focus": "正比例与一次函数"},
        {"topic_id": "math_j8_pythagoras", "name": "勾股定理", "focus": "直角三角形三边关系"},
        {"topic_id": "math_j8_quad", "name": "平行四边形", "focus": "判定与性质"},
        {"topic_id": "math_j8_special", "name": "特殊平行四边形", "focus": "矩形菱形正方形"},
        {"topic_id": "math_j8_var", "name": "反比例函数", "focus": "图像与性质"},
    ],
    "math/九年级上": [
        {"topic_id": "math_j9_equation", "name": "一元二次方程", "focus": "解法与应用"},
        {"topic_id": "math_j9_discriminant", "name": "根的判别式", "focus": "根的情况判断"},
        {"topic_id": "math_j9_vieta", "name": "根与系数关系", "focus": "韦达定理"},
        {"topic_id": "math_j9_quadratic", "name": "二次函数", "focus": "图像性质最值"},
        {"topic_id": "math_j9_circle", "name": "圆", "focus": "圆的性质与计算"},
        {"topic_id": "math_j9_rotation", "name": "旋转", "focus": "图形旋转"},
        {"topic_id": "math_j9_prob", "name": "概率", "focus": "列举法求概率"},
    ],
    "math/九年级下": [
        {"topic_id": "math_j9_trig", "name": "锐角三角函数", "focus": "sin cos tan"},
        {"topic_id": "math_j9_similar", "name": "相似三角形", "focus": "判定与性质"},
        {"topic_id": "math_j9_circles", "name": "圆与圆的位置关系", "focus": "相交相切"},
        {"topic_id": "math_j9_view", "name": "投影与视图", "focus": "三视图"},
        {"topic_id": "math_j9_review", "name": "中考总复习", "focus": "综合应用"},
    ],
    
    # ===== 小学语文（基于部编版目录） =====
    "chinese/一年级上": [
        {"topic_id": "chinese_g1_pinyin", "name": "汉语拼音", "focus": "声母韵母整体认读"},
        {"topic_id": "chinese_g1_stroke", "name": "汉字笔画", "focus": "基本笔画写法"},
        {"topic_id": "chinese_g1_read", "name": "识字写字", "focus": "常用汉字认识"},
        {"topic_id": "chinese_g1_poem", "name": "古诗诵读", "focus": "简短古诗背诵"},
        {"topic_id": "chinese_g1_listen", "name": "听说话", "focus": "倾听表达"},
        {"topic_id": "chinese_g1_read_text", "name": "课文阅读", "focus": "短文朗读理解"},
    ],
    "chinese/一年级下": [
        {"topic_id": "chinese_g1_pinyin2", "name": "汉语拼音巩固", "focus": "拼读练习"},
        {"topic_id": "chinese_g1_word", "name": "词语积累", "focus": "常用词汇"},
        {"topic_id": "chinese_g1_sentence", "name": "句子练习", "focus": "造句说话"},
        {"topic_id": "chinese_g1_poem2", "name": "古诗积累", "focus": "必背古诗"},
        {"topic_id": "chinese_g1_read2", "name": "阅读理解", "focus": "短文理解"},
    ],
    "chinese/二年级上": [
        {"topic_id": "chinese_g2_pinyin", "name": "拼音巩固", "focus": "多音字辨析"},
        {"topic_id": "chinese_g2_word", "name": "词语积累", "focus": "近义词反义词"},
        {"topic_id": "chinese_g2_sentence", "name": "句式训练", "focus": "把字句被字句"},
        {"topic_id": "chinese_g2_read", "name": "阅读欣赏", "focus": "短文阅读"},
        {"topic_id": "chinese_g2_write", "name": "看图写话", "focus": "简单写作"},
        {"topic_id": "chinese_g2_poem", "name": "古诗诵读", "focus": "必背古诗"},
    ],
    "chinese/二年级下": [
        {"topic_id": "chinese_g2_word2", "name": "词语积累二", "focus": "词语运用"},
        {"topic_id": "chinese_g2_reading", "name": "阅读理解二", "focus": "段落理解"},
        {"topic_id": "chinese_g2_write2", "name": "写话练习", "focus": "简单日记"},
        {"topic_id": "chinese_g2_poem2", "name": "古诗积累二", "focus": "必背篇目"},
    ],
    "chinese/三年级上": [
        {"topic_id": "chinese_g3_read", "name": "阅读理解", "focus": "抓住主要内容"},
        {"topic_id": "chinese_g3_write", "name": "习作入门", "focus": "观察写话"},
        {"topic_id": "chinese_g3_word", "name": "词语积累", "focus": "成语积累"},
        {"topic_id": "chinese_g3_poem", "name": "古诗文", "focus": "古诗背诵默写"},
        {"topic_id": "chinese_g3_oral", "name": "口语交际", "focus": "完整表达"},
    ],
    "chinese/三年级下": [
        {"topic_id": "chinese_g3_read2", "name": "阅读理解二", "focus": "体会情感"},
        {"topic_id": "chinese_g3_write2", "name": "习作练习", "focus": "段落写作"},
        {"topic_id": "chinese_g3_accumulate", "name": "积累运用", "focus": "词句段运用"},
    ],
    "chinese/四年级上": [
        {"topic_id": "chinese_g4_read", "name": "阅读理解", "focus": "把握文章结构"},
        {"topic_id": "chinese_g4_write", "name": "习作训练", "focus": "写人记事"},
        {"topic_id": "chinese_g4_classical", "name": "古诗文阅读", "focus": "文言文入门"},
        {"topic_id": "chinese_g4_poem", "name": "古诗词背诵", "focus": "必背篇目"},
    ],
    "chinese/四年级下": [
        {"topic_id": "chinese_g4_read2", "name": "阅读理解二", "focus": "品味语言"},
        {"topic_id": "chinese_g4_write2", "name": "习作二", "focus": "写景状物"},
        {"topic_id": "chinese_g4_poem2", "name": "古诗词二", "focus": "必背篇目"},
    ],
    "chinese/五年级上": [
        {"topic_id": "chinese_g5_read", "name": "阅读理解", "focus": "体会思想感情"},
        {"topic_id": "chinese_g5_write", "name": "习作训练", "focus": "写具体写生动"},
        {"topic_id": "chinese_g5_classical", "name": "文言文", "focus": "简单文言文阅读"},
        {"topic_id": "chinese_g5_poem", "name": "古诗词积累", "focus": "必背篇目"},
    ],
    "chinese/五年级下": [
        {"topic_id": "chinese_g5_read2", "name": "阅读理解二", "focus": "领悟表达方法"},
        {"topic_id": "chinese_g5_write2", "name": "习作二", "focus": "想象作文"},
        {"topic_id": "chinese_g5_poem2", "name": "古诗词二", "focus": "必背篇目"},
    ],
    "chinese/六年级上": [
        {"topic_id": "chinese_g6_read", "name": "阅读理解", "focus": "揣摩作者思路"},
        {"topic_id": "chinese_g6_write", "name": "习作训练", "focus": "真情实感"},
        {"topic_id": "chinese_g6_classical", "name": "古诗文", "focus": "古诗词文言"},
        {"topic_id": "chinese_g6_poem", "name": "古诗词积累", "focus": "必背篇目"},
    ],
    "chinese/六年级下": [
        {"topic_id": "chinese_g6_read2", "name": "阅读理解二", "focus": "综合理解"},
        {"topic_id": "chinese_g6_write2", "name": "习作二", "focus": "难忘经历"},
        {"topic_id": "chinese_g6_poem2", "name": "古诗词二", "focus": "必背篇目"},
        {"topic_id": "chinese_g6_review", "name": "小升初复习", "focus": "知识梳理"},
    ],
    
    # ===== 初中语文（部编版） =====
    "chinese/七年级上": [
        {"topic_id": "chinese_j7_prose", "name": "散文阅读", "focus": "抓住特点写具体"},
        {"topic_id": "chinese_j7_poem", "name": "古诗词诵读", "focus": "意境情感"},
        {"topic_id": "chinese_j7_classical", "name": "文言文入门", "focus": "实词虚词积累"},
        {"topic_id": "chinese_j7_narrative", "name": "记叙文阅读", "focus": "六要素"},
        {"topic_id": "chinese_j7_write", "name": "作文训练", "focus": "写人记事"},
    ],
    "chinese/七年级下": [
        {"topic_id": "chinese_j7_prose2", "name": "散文阅读二", "focus": "抒情手法"},
        {"topic_id": "chinese_j7_classical2", "name": "文言文进阶", "focus": "语法现象"},
        {"topic_id": "chinese_j7_poem2", "name": "古诗词二", "focus": "对比阅读"},
    ],
    "chinese/八年级上": [
        {"topic_id": "chinese_j8_news", "name": "新闻阅读", "focus": "消息特写"},
        {"topic_id": "chinese_j8_argument", "name": "议论文入门", "focus": "论点论据论证"},
        {"topic_id": "chinese_j8_classical", "name": "文言文精读", "focus": "名篇赏析"},
        {"topic_id": "chinese_j8_poem", "name": "古诗词鉴赏", "focus": "意象意境"},
        {"topic_id": "chinese_j8_write", "name": "作文训练", "focus": "议论文写作"},
    ],
    "chinese/八年级下": [
        {"topic_id": "chinese_j8_prose2", "name": "散文精读", "focus": "托物言志"},
        {"topic_id": "chinese_j8_classical2", "name": "文言文深化", "focus": "古今异义"},
        {"topic_id": "chinese_j8_poem2", "name": "古诗词二", "focus": "专题阅读"},
    ],
    "chinese/九年级上": [
        {"topic_id": "chinese_j9_poem", "name": "古诗词鉴赏", "focus": "中考必背"},
        {"topic_id": "chinese_j9_classical", "name": "文言文阅读", "focus": "迁移运用"},
        {"topic_id": "chinese_j9_argument", "name": "议论文写作", "focus": "论证方法"},
        {"topic_id": "chinese_j9_novel", "name": "小说阅读", "focus": "人物情节环境"},
        {"topic_id": "chinese_j9_exam", "name": "中考复习策略", "focus": "知识点梳理"},
    ],
    "chinese/九年级下": [
        {"topic_id": "chinese_j9_drama", "name": "戏剧文学", "focus": "剧本阅读"},
        {"topic_id": "chinese_j9_review", "name": "中考总复习", "focus": "专项突破"},
    ],
    
    # ===== 初中物理 =====
    "physics/八年级上": [
        {"topic_id": "phys_ch1_sound", "name": "声现象", "focus": "声音的产生传播"},
        {"topic_id": "phys_ch2_light", "name": "光现象", "focus": "反射折射色散"},
        {"topic_id": "phys_ch3_lens", "name": "透镜及其应用", "focus": "凸透镜成像规律"},
        {"topic_id": "phys_ch4_matter", "name": "物质物理属性", "focus": "密度质量"},
        {"topic_id": "phys_ch5_force", "name": "力与运动", "focus": "力的概念惯性"},
    ],
    "physics/八年级下": [
        {"topic_id": "phys_ch6_pressure", "name": "压强", "focus": "固体液体压强"},
        {"topic_id": "phys_ch7_buoyancy", "name": "浮力", "focus": "阿基米德原理"},
        {"topic_id": "phys_ch8_work", "name": "功与机械能", "focus": "功率动能势能"},
        {"topic_id": "phys_ch9_simple", "name": "简单机械", "focus": "杠杆滑轮"},
    ],
    "physics/九年级": [
        {"topic_id": "phys_ch10_heat", "name": "内能热机", "focus": "分子热运动"},
        {"topic_id": "phys_ch11_circuit", "name": "电路与电流", "focus": "串并联电路"},
        {"topic_id": "phys_ch12_voltage", "name": "电压电阻", "focus": "欧姆定律基础"},
        {"topic_id": "phys_ch13_ohm", "name": "欧姆定律", "focus": "I=U/R应用"},
        {"topic_id": "phys_ch14_power", "name": "电功率", "focus": "P=UI计算"},
        {"topic_id": "phys_ch15_safety", "name": "安全用电", "focus": "触电防护"},
        {"topic_id": "phys_ch16_magnet", "name": "电与磁", "focus": "电磁感应"},
        {"topic_id": "phys_ch17_info", "name": "信息的传递", "focus": "电磁波"},
        {"topic_id": "phys_ch18_energy", "name": "能源与可持续发展", "focus": "能源分类"},
    ],
    
    # ===== 初中化学 =====
    "chemistry/九年级": [
        {"topic_id": "chem_ch1_intro", "name": "化学入门", "focus": "实验基本操作"},
        {"topic_id": "chem_ch2_air", "name": "空气氧气", "focus": "空气组成制取"},
        {"topic_id": "chem_ch3_atom", "name": "原子分子离子", "focus": "物质构成"},
        {"topic_id": "chem_ch4_water", "name": "爱护水资源", "focus": "水的组成净化"},
        {"topic_id": "chem_ch5_equation", "name": "化学方程式", "focus": "质量守恒配平"},
        {"topic_id": "chem_ch6_carbon", "name": "碳和碳的氧化物", "focus": "CO2性质制取"},
        {"topic_id": "chem_ch7_fuel", "name": "燃料及其利用", "focus": "燃烧灭火"},
        {"topic_id": "chem_ch8_solution", "name": "溶液", "focus": "溶解度浓度"},
        {"topic_id": "chem_ch9_acid_base", "name": "酸碱盐", "focus": "化学性质"},
        {"topic_id": "chem_ch10_material", "name": "金属与金属材料", "focus": "性质利用防锈"},
        {"topic_id": "chem_ch11_organic", "name": "有机化合物", "focus": "甲烷乙醇糖类"},
        {"topic_id": "chem_ch12_health", "name": "化学与生活", "focus": "营养素安全"},
    ],
    
    # ===== 初中历史 =====
    "history/七年级上": [
        {"topic_id": "hist_ch1_prehistory", "name": "史前时期", "focus": "远古居民"},
        {"topic_id": "hist_ch2_dynasty", "name": "夏商周", "focus": "早期国家"},
        {"topic_id": "hist_ch3_warring", "name": "秦汉统一", "focus": "大一统帝国"},
        {"topic_id": "hist_ch4_split", "name": "三国两晋南北朝", "focus": "政权分立"},
    ],
    "history/七年级下": [
        {"topic_id": "hist_ch5_sui_tang", "name": "隋唐时期", "focus": "繁荣开放"},
        {"topic_id": "hist_ch6_song_yuan", "name": "宋元时期", "focus": "民族融合"},
        {"topic_id": "hist_ch7_ming_qing", "name": "明清时期", "focus": "君主专制强化"},
    ],
    "history/八年级上": [
        {"topic_id": "hist_ch8_opium", "name": "鸦片战争", "focus": "屈辱开始"},
        {"topic_id": "hist_ch9_modern", "name": "近代探索", "focus": "救亡图存"},
        {"topic_id": "hist_ch10_republic", "name": "辛亥革命", "focus": "民主革命"},
        {"topic_id": "hist_ch11_new_culture", "name": "新文化运动", "focus": "思想解放"},
        {"topic_id": "hist_ch12_cpc", "name": "中国共产党成立", "focus": "开天辟地"},
        {"topic_id": "hist_ch13_njr", "name": "抗日战争", "focus": "民族救亡"},
        {"topic_id": "hist_ch14_解放", "name": "解放战争", "focus": "新中国诞生"},
    ],
    "history/八年级下": [
        {"topic_id": "hist_ch15_new_china", "name": "新中国成立", "focus": "站起来"},
        {"topic_id": "hist_ch16_socialism", "name": "社会主义建设", "focus": "探索曲折"},
        {"topic_id": "hist_ch17_reform", "name": "改革开放", "focus": "富起来"},
        {"topic_id": "hist_ch18_modern", "name": "新时代", "focus": "强起来"},
    ],
    "history/九年级上": [
        {"topic_id": "hist_ch19_ancient", "name": "古代文明", "focus": "两河流域埃及希腊罗马"},
        {"topic_id": "hist_ch20_feudal", "name": "封建时代", "focus": "中世纪欧洲"},
        {"topic_id": "hist_ch21_renaissance", "name": "文艺复兴", "focus": "思想解放"},
        {"topic_id": "hist_ch22_new_route", "name": "新航路开辟", "focus": "世界联系"},
        {"topic_id": "hist_ch23_revolution", "name": "资产阶级革命", "focus": "英美法革命"},
        {"topic_id": "hist_ch24_industrial", "name": "工业革命", "focus": "蒸汽时代"},
    ],
    "history/九年级下": [
        {"topic_id": "hist_ch25_modern", "name": "近代世界", "focus": "资本主义发展"},
        {"topic_id": "hist_ch26_wars", "name": "两次世界大战", "focus": "战争与和平"},
        {"topic_id": "hist_ch27_cold", "name": "冷战时期", "focus": "两极格局"},
        {"topic_id": "hist_ch28_modern_world", "name": "现代世界", "focus": "多极化全球化"},
    ],
    
    # ===== 初中地理 =====
    "geography/七年级上": [
        {"topic_id": "geo_ch1_earth", "name": "地球与地图", "focus": "地球形状运动"},
        {"topic_id": "geo_ch2_map", "name": "地图阅读", "focus": "比例尺方向"},
        {"topic_id": "geo_ch3_continent", "name": "大洲大洋", "focus": "海陆分布"},
        {"topic_id": "geo_ch4_climate", "name": "天气气候", "focus": "气温降水分布"},
        {"topic_id": "geo_ch5_population", "name": "人口与人种", "focus": "人口分布"},
    ],
    "geography/七年级下": [
        {"topic_id": "geo_ch6_asia", "name": "亚洲", "focus": "自然环境特征"},
        {"topic_id": "geo_ch7_japan", "name": "日本", "focus": "岛国特征"},
        {"topic_id": "geo_ch8_india", "name": "印度", "focus": "人口农业"},
        {"topic_id": "geo_ch9_middle", "name": "中东", "focus": "石油水资源"},
        {"topic_id": "geo_ch10_europe", "name": "欧洲西部", "focus": "发达国家"},
        {"topic_id": "geo_ch11_africa", "name": "撒哈拉以南非洲", "focus": "单一商品经济"},
        {"topic_id": "geo_ch12_latam", "name": "拉丁美洲", "focus": "殖民历史"},
    ],
    "geography/八年级上": [
        {"topic_id": "geo_ch13_russia", "name": "俄罗斯", "focus": "国土资源"},
        {"topic_id": "geo_ch14_australia", "name": "澳大利亚", "focus": "骑在羊背上的国家"},
        {"topic_id": "geo_ch15_americas", "name": "美国", "focus": "发达国家代表"},
        {"topic_id": "geo_ch16_brazil", "name": "巴西", "focus": "发展中国家"},
        {"topic_id": "geo_ch17_antarctica", "name": "极地地区", "focus": "科学考察"},
    ],
    "geography/八年级下": [
        {"topic_id": "geo_ch18_china_region", "name": "中国的区域差异", "focus": "四大地理区域"},
        {"topic_id": "geo_ch19_north", "name": "北方地区", "focus": "自然特征农业"},
        {"topic_id": "geo_ch20_south", "name": "南方地区", "focus": "水乡特征"},
        {"topic_id": "geo_ch21_northwest", "name": "西北地区", "focus": "干旱特征"},
        {"topic_id": "geo_ch22_xizang", "name": "青藏地区", "focus": "高寒特征"},
        {"topic_id": "geo_ch23_development", "name": "中国的经济发展", "focus": "工业农业布局"},
    ],
    
    # ===== 初中生物 =====
    "biology/七年级上": [
        {"topic_id": "bio_ch1_cell", "name": "细胞结构与功能", "focus": "动植物细胞对比"},
        {"topic_id": "bio_ch2_division", "name": "细胞分裂分化", "focus": "生长发育基础"},
        {"topic_id": "bio_ch3_tissue", "name": "器官系统", "focus": "结构层次"},
        {"topic_id": "bio_ch4_plant", "name": "绿色植物", "focus": "光合作用呼吸作用"},
        {"topic_id": "bio_ch5_animal", "name": "动物类群", "focus": "主要类群特征"},
    ],
    "biology/七年级下": [
        {"topic_id": "bio_ch6_human", "name": "人体生理", "focus": "消化系统呼吸系统"},
        {"topic_id": "bio_ch7_circulation", "name": "循环系统", "focus": "心脏血管血液"},
        {"topic_id": "bio_ch8_excretion", "name": "排泄系统", "focus": "尿液形成"},
        {"topic_id": "bio_ch9_nerve", "name": "神经系统", "focus": "调节功能"},
        {"topic_id": "bio_ch10_endocrine", "name": "内分泌系统", "focus": "激素调节"},
    ],
    "biology/八年级上": [
        {"topic_id": "bio_ch11_invertebrate", "name": "无脊椎动物", "focus": "主要类群"},
        {"topic_id": "bio_ch12_fish_amphibian", "name": "鱼类两栖类", "focus": "水生适应"},
        {"topic_id": "bio_ch13_reptile_bird", "name": "爬行类鸟类", "focus": "陆生适应"},
        {"topic_id": "bio_ch14_mammal", "name": "哺乳动物", "focus": "高等特征"},
        {"topic_id": "bio_ch15_microbe", "name": "微生物", "focus": "细菌真菌病毒"},
        {"topic_id": "bio_ch16_genetics", "name": "遗传变异", "focus": "基因染色体"},
    ],
    "biology/八年级下": [
        {"topic_id": "bio_ch17_evolution", "name": "生物进化", "focus": "自然选择"},
        {"topic_id": "bio_ch18_ecology", "name": "生态系统", "focus": "食物链食物网"},
        {"topic_id": "bio_ch19_environment", "name": "环境保护", "focus": "生物多样性"},
        {"topic_id": "bio_ch20_health", "name": "健康生活", "focus": "免疫预防"},
    ],
    
    # ===== 初中道德与法治 =====
    "morality/七年级上": [
        {"topic_id": "moral_ch1_school", "name": "中学时代", "focus": "适应新环境"},
        {"topic_id": "moral_ch2_friendship", "name": "友谊的天空", "focus": "人际交往"},
        {"topic_id": "moral_ch3_family", "name": "亲情之爱", "focus": "家庭关系"},
        {"topic_id": "moral_ch4_life", "name": "珍爱生命", "focus": "生命安全教育"},
    ],
    "morality/七年级下": [
        {"topic_id": "moral_ch5_emotion", "name": "情绪管理", "focus": "青春期情绪"},
        {"topic_id": "moral_ch6_collective", "name": "集体生活", "focus": "班集体建设"},
        {"topic_id": "moral_ch7_law", "name": "法律基础", "focus": "未成年人保护法"},
    ],
    "morality/八年级上": [
        {"topic_id": "moral_ch8_social", "name": "社会生活", "focus": "网络与社会"},
        {"topic_id": "moral_ch9_rights", "name": "权利义务", "focus": "公民基本权利"},
        {"topic_id": "moral_ch10_national", "name": "国家机构", "focus": "政府性质职能"},
        {"topic_id": "moral_ch11_constitution", "name": "宪法", "focus": "根本大法"},
    ],
    "morality/八年级下": [
        {"topic_id": "moral_ch12_rights", "name": "公民权利", "focus": "平等权政治权利"},
        {"topic_id": "moral_ch13_obligation", "name": "公民义务", "focus": "基本义务"},
        {"topic_id": "moral_ch14_gov", "name": "政府", "focus": "依法行政"},
        {"topic_id": "moral_ch15_society", "name": "社会公平", "focus": "公平正义"},
    ],
    "morality/九年级": [
        {"topic_id": "moral_ch16_achieve", "name": "富强与创新", "focus": "改革开放成就"},
        {"topic_id": "moral_ch17_democracy", "name": "民主与法治", "focus": "全过程人民民主"},
        {"topic_id": "moral_ch18_culture", "name": "文明与文化", "focus": "中华文化传承"},
        {"topic_id": "moral_ch19_nature", "name": "人与自然", "focus": "生态文明建设"},
        {"topic_id": "moral_ch20_future", "name": "走向未来", "focus": "中国梦青年担当"},
    ],
    
    # ===== 初中英语 =====
    "english/七年级上": [
        {"topic_id": "eng_ch1_greet", "name": "问候与介绍", "focus": "日常交际用语"},
        {"topic_id": "eng_ch2_family", "name": "家庭与朋友", "focus": "名词所有格"},
        {"topic_id": "eng_ch3_hobby", "name": "兴趣爱好", "focus": "like doing"},
        {"topic_id": "eng_ch4_food", "name": "饮食与健康", "focus": "可数不可数名词"},
        {"topic_id": "eng_ch5_time", "name": "时间与日程", "focus": "时间表达"},
        {"topic_id": "eng_ch6_shopping", "name": "购物与价格", "focus": "how much"},
    ],
    "english/七年级下": [
        {"topic_id": "eng_ch7_weather", "name": "天气与季节", "focus": "描述天气"},
        {"topic_id": "eng_ch8_daily", "name": "日常生活", "focus": "现在进行时"},
        {"topic_id": "eng_ch9_travel", "name": "旅行与交通", "focus": "过去时态"},
        {"topic_id": "eng_ch10_culture", "name": "节日与文化", "focus": "中西节日对比"},
    ],
    "english/八年级上": [
        {"topic_id": "eng_ch11_health", "name": "健康与运动", "focus": "建议句型"},
        {"topic_id": "eng_ch12_problem", "name": "问题解决", "focus": "should用法"},
        {"topic_id": "eng_ch13_future", "name": "未来计划", "focus": "将来时态"},
        {"topic_id": "eng_ch14_climate", "name": "环境与气候", "focus": "比较级最高级"},
    ],
    "english/八年级下": [
        {"topic_id": "eng_ch15_experience", "name": "生活经历", "focus": "现在完成时"},
        {"topic_id": "eng_ch16_volunteer", "name": "志愿服务", "focus": "情态动词"},
        {"topic_id": "eng_ch17_robots", "name": "科技与未来", "focus": "定语从句入门"},
        {"topic_id": "eng_ch18_nature", "name": "自然与环境", "focus": "环保话题"},
    ],
    "english/九年级": [
        {"topic_id": "eng_ch19_passive", "name": "被动语态", "focus": "一般现在过去将来时"},
        {"topic_id": "eng_ch20_clause", "name": "复合句", "focus": "宾语从句定语从句"},
        {"topic_id": "eng_ch21_reading", "name": "阅读策略", "focus": "猜词推断主旨"},
        {"topic_id": "eng_ch22_writing", "name": "写作技巧", "focus": "书信通知议论文"},
        {"topic_id": "eng_ch23_review", "name": "中考复习", "focus": "语法词汇专项"},
    ],
}

def main():
    base_dir = Path("output")
    total = 0
    
    for key, topics in TEXTBOOK_TOPICS.items():
        subject, grade = key.split("/")
        
        for topic in topics:
            topic_id = topic["topic_id"]
            name = topic["name"]
            focus = topic["focus"]
            
            dir_path = base_dir / subject / grade / topic_id
            dir_path.mkdir(parents=True, exist_ok=True)
            
            content = {
                "topic_id": topic_id,
                "name": name,
                "grade": grade,
                "subject": subject,
                "focus": focus,
                "explanation": "",
                "quiz": "",
                "image": "image.png",
                "audio": ["audio.mp3"],
                "tags": [subject, grade],
                "difficulty": 1,
                "created": datetime.now().strftime("%Y-%m-%d")
            }
            
            json_path = dir_path / f"{topic_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            total += 1
    
    print(f"✅ 已生成 {total} 个知识点模板")
    
    # 统计分布
    print("\n📊 分布统计:")
    grade_counts = {}
    for key in TEXTBOOK_TOPICS.keys():
        grade = key.split("/")[1]
        grade_counts[grade] = grade_counts.get(grade, 0) + len(TEXTBOOK_TOPICS[key])
    
    for grade, count in sorted(grade_counts.items()):
        print(f"  {grade}: {count}个")

if __name__ == "__main__":
    main()
