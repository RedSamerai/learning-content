#!/usr/bin/env python3
"""生成完整的九年级知识点清单"""
import json
from pathlib import Path

# 人教版九年级完整知识点（基于2024最新教材）
JIUNIANJI_TOPICS = {
    # ===== 数学（上册） =====
    "math/九年级上": [
        {"topic_id": "math_ch1_equation", "name": "一元二次方程的概念与解法", "focus": "概念理解、三种解法"},
        {"topic_id": "math_ch1_discriminant", "name": "根的判别式与根的情况", "focus": "Δ判断根的个数"},
        {"topic_id": "math_ch1_vieta", "name": "根与系数的关系（韦达定理）", "focus": "韦达定理应用"},
        {"topic_id": "math_ch1_application", "name": "一元二次方程实际应用", "focus": "利润、面积、增长率问题"},
        {"topic_id": "math_ch2_function", "name": "二次函数的概念与图像", "focus": "抛物线性质"},
        {"topic_id": "math_ch2_vertex", "name": "二次函数的顶点与最值", "focus": "配方求顶点"},
        {"topic_id": "math_ch2_graph", "name": "二次函数图像性质", "focus": "开口方向、对称轴"},
        {"topic_id": "math_ch2_translation", "name": "二次函数图像平移", "focus": "平移规律"},
        {"topic_id": "math_ch2_application", "name": "二次函数实际应用", "focus": "最大利润、最大面积"},
        {"topic_id": "math_ch3_circle", "name": "圆的基本性质", "focus": "圆心角、弧、弦关系"},
        {"topic_id": "math_ch3_arc", "name": "弧长与扇形面积", "focus": "公式应用"},
        {"topic_id": "math_ch3_tangent", "name": "圆的切线性质", "focus": "切线判定与性质"},
        {"topic_id": "math_ch3_position", "name": "点、直线与圆的位置关系", "focus": "数量关系判定"},
        {"topic_id": "math_ch3_inscribed", "name": "圆的内接四边形", "focus": "对角互补性质"},
        {"topic_id": "math_ch4_probability", "name": "随机事件与概率", "focus": "列举法求概率"},
        {"topic_id": "math_ch4_list", "name": "列表法与树状图", "focus": "复杂概率计算"},
        {"topic_id": "math_ch4_simulation", "name": "频率估计概率", "focus": "大量重复试验"},
    ],
    
    # ===== 数学（下册） =====
    "math/九年级下": [
        {"topic_id": "math_ch5_similar", "name": "相似三角形的判定", "focus": "三种判定方法"},
        {"topic_id": "math_ch5_properties", "name": "相似三角形的性质", "focus": "对应边成比例"},
        {"topic_id": "math_ch5_app", "name": "相似三角形实际应用", "focus": "测量高度、宽度"},
        {"topic_id": "math_ch6_trig", "name": "锐角三角函数", "focus": "sin、cos、tan定义"},
        {"topic_id": "math_ch6_special", "name": "特殊角的三角函数值", "focus": "30°、45°、60°"},
        {"topic_id": "math_ch6_solution", "name": "解直角三角形", "focus": "已知边和角求其他元素"},
        {"topic_id": "math_ch6_angle", "name": "仰角与俯角", "focus": "解直角三角形应用"},
        {"topic_id": "math_ch7_inverse", "name": "反比例函数概念", "focus": "反比例函数定义"},
        {"topic_id": "math_ch7_graph", "name": "反比例函数图像与性质", "focus": "双曲线性质"},
        {"topic_id": "math_ch7_app", "name": "反比例函数实际应用", "focus": "力学、电学应用"},
        {"topic_id": "math_ch8_view", "name": "视图与投影", "focus": "三视图绘制"},
        {"topic_id": "math_ch8_center", "name": "中心投影与平行投影", "focus": "投影类型区分"},
        {"topic_id": "math_ch9_transformation", "name": "图形的旋转", "focus": "旋转性质与应用"},
        {"topic_id": "math_ch9_central", "name": "圆心角与圆周角", "focus": "角度关系"},
        {"topic_id": "math_ch10_coordinate", "name": "坐标与图形变换", "focus": "平移、旋转、对称"},
    ],
    
    # ===== 物理（全一册） =====
    "physics/九年级": [
        {"topic_id": "phys_ch1_heat", "name": "分子热运动", "focus": "分子动理论"},
        {"topic_id": "phys_ch1_internal", "name": "内能与热量", "focus": "内能改变方式"},
        {"topic_id": "phys_ch1_specific", "name": "比热容概念", "focus": "热量计算Q=cmΔt"},
        {"topic_id": "phys_ch2_engine", "name": "热机工作原理", "focus": "四冲程内燃机"},
        {"topic_id": "phys_ch2_efficiency", "name": "热机效率", "focus": "能量利用率"},
        {"topic_id": "phys_ch2_energy", "name": "能量转化与守恒", "focus": "能量守恒定律"},
        {"topic_id": "phys_ch3_charge", "name": "两种电荷与电流", "focus": "电荷相互作用"},
        {"topic_id": "phys_ch3_circuit", "name": "电路组成与连接", "focus": "串联并联区别"},
        {"topic_id": "phys_ch3_current", "name": "电流的测量", "focus": "电流表使用"},
        {"topic_id": "phys_ch4_voltage", "name": "电压与电阻", "focus": "电压概念、电阻性质"},
        {"topic_id": "phys_ch4_resistor", "name": "变阻器原理", "focus": "滑动变阻器"},
        {"topic_id": "phys_ch5_ohm", "name": "欧姆定律", "focus": "I=U/R及其应用"},
        {"topic_id": "phys_ch5_series", "name": "串联电路规律", "focus": "分压原理"},
        {"topic_id": "phys_ch5_parallel", "name": "并联电路规律", "focus": "分流原理"},
        {"topic_id": "phys_ch6_power", "name": "电能与电功", "focus": "W=UIt计算"},
        {"topic_id": "phys_ch6_power_calc", "name": "电功率概念与计算", "focus": "P=UI应用"},
        {"topic_id": "phys_ch6_joule", "name": "焦耳定律", "focus": "电热计算Q=I²Rt"},
        {"topic_id": "phys_ch6_safe", "name": "安全用电常识", "focus": "触电防护"},
        {"topic_id": "phys_ch7_magnet", "name": "磁现象与磁场", "focus": "磁极、磁场方向"},
        {"topic_id": "phys_ch7_electromagnet", "name": "电生磁与电磁铁", "focus": "奥斯特实验"},
        {"topic_id": "phys_ch7_motor", "name": "电动机原理", "focus": "通电导体受力"},
        {"topic_id": "phys_ch7_generator", "name": "电磁感应与发电机", "focus": "法拉第发现"},
        {"topic_id": "phys_ch8_info", "name": "信息的传递", "focus": "电磁波与应用"},
        {"topic_id": "phys_ch9_energy", "name": "能源与可持续发展", "focus": "能源分类与利用"},
    ],
    
    # ===== 化学（全一册） =====
    "chemistry/九年级": [
        {"topic_id": "chem_ch1_change", "name": "物质的变化与性质", "focus": "物理变化与化学变化"},
        {"topic_id": "chem_ch1_experiment", "name": "化学实验基本操作", "focus": "仪器使用与安全"},
        {"topic_id": "chem_ch2_air", "name": "空气的成分与用途", "focus": "氧气、氮气性质"},
        {"topic_id": "chem_ch2_oxygen", "name": "氧气的性质与制取", "focus": "实验室制法"},
        {"topic_id": "chem_ch2_air_pollution", "name": "空气的污染与防治", "focus": "有害气体与粉尘"},
        {"topic_id": "chem_ch3_atom", "name": "原子的构成", "focus": "原子结构模型"},
        {"topic_id": "chem_ch3_element", "name": "元素与元素周期表", "focus": "元素概念与应用"},
        {"topic_id": "chem_ch3_ion", "name": "离子与化学式", "focus": "离子形成与表示"},
        {"topic_id": "chem_ch4_water", "name": "水的组成与净化", "focus": "电解水实验"},
        {"topic_id": "chem_ch4_solution", "name": "溶液的形成", "focus": "溶质与溶剂"},
        {"topic_id": "chem_ch5_equation", "name": "质量守恒定律", "focus": "化学反应本质"},
        {"topic_id": "chem_ch5_equation_write", "name": "化学方程式的书写", "focus": "配平方法"},
        {"topic_id": "chem_ch5_equation_calc", "name": "根据化学方程式计算", "focus": "质量关系计算"},
        {"topic_id": "chem_ch6_carbon", "name": "碳的单质与性质", "focus": "金刚石、石墨、C60"},
        {"topic_id": "chem_ch6_co2", "name": "二氧化碳的制取与性质", "focus": "实验室制法"},
        {"topic_id": "chem_ch6_co", "name": "一氧化碳的性质", "focus": "毒性与还原性"},
        {"topic_id": "chem_ch7_fuel", "name": "燃烧与灭火", "focus": "燃烧条件与灭火原理"},
        {"topic_id": "chem_ch7_explosion", "name": "爆炸与燃料的利用", "focus": "安全常识"},
        {"topic_id": "chem_ch7_new_fuel", "name": "新能源开发与利用", "focus": "氢能、生物质能"},
        {"topic_id": "chem_ch8_solution", "name": "溶解度与饱和溶液", "focus": "溶解度曲线"},
        {"topic_id": "chem_ch8_concentration", "name": "溶质的质量分数", "focus": "浓度计算"},
        {"topic_id": "chem_ch8_crystal", "name": "结晶方法", "focus": "蒸发与降温结晶"},
        {"topic_id": "chem_ch9_acid", "name": "常见的酸", "focus": "盐酸、硫酸性质"},
        {"topic_id": "chem_ch9_base", "name": "常见的碱", "focus": "氢氧化钠、氢氧化钙"},
        {"topic_id": "chem_ch9_salt", "name": "盐的化学性质", "focus": "复分解反应"},
        {"topic_id": "chem_ch9_ph", "name": "溶液的酸碱度", "focus": "pH值测定与应用"},
        {"topic_id": "chem_ch10_material", "name": "金属材料", "focus": "合金性质与应用"},
        {"topic_id": "chem_ch10_corrosion", "name": "金属资源的利用与保护", "focus": "防锈方法"},
        {"topic_id": "chem_ch11_organic", "name": "有机化合物简介", "focus": "甲烷、乙醇、糖类"},
        {"topic_id": "chem_ch11_protein", "name": "化学与人体健康", "focus": "六大营养素"},
    ],
    
    # ===== 语文（上下册） =====
    "chinese/九年级上": [
        {"topic_id": "chinese_ch1_rock", "name": "沁园春·雪", "focus": "毛泽东词作赏析"},
        {"topic_id": "chinese_ch2_poem", "name": "我爱这土地", "focus": "艾青诗歌鉴赏"},
        {"topic_id": "chinese_ch2_modern", "name": "你是人间的四月天", "focus": "林徽因诗歌欣赏"},
        {"topic_id": "chinese_ch2_song", "name": "行路难", "focus": "李白诗作解读"},
        {"topic_id": "chinese_ch3_classical", "name": "岳阳楼记", "focus": "范仲淹名篇精读"},
        {"topic_id": "chinese_ch3_chu", "name": "醉翁亭记", "focus": "欧阳修散文赏析"},
        {"topic_id": "chinese_ch4_poem", "name": "诗词三首", "focus": "诗词鉴赏方法"},
        {"topic_id": "chinese_ch4_novel", "name": "智取生辰纲", "focus": "水浒传选段阅读"},
        {"topic_id": "chinese_ch5_novel", "name": "范进中举", "focus": "儒林外史讽刺手法"},
        {"topic_id": "chinese_ch5_read", "name": "小说阅读方法", "focus": "人物情节环境三要素"},
        {"topic_id": "chinese_ch6_letter", "name": "敬业与乐业", "focus": "梁启超演讲辞"},
        {"topic_id": "chinese_ch6_on_education", "name": "就英法联军远征中国致巴特勒上尉的信", "focus": "雨果反战思想"},
        {"topic_id": "chinese_ch7_essay", "name": "论教养", "focus": "利哈乔夫议论文"},
        {"topic_id": "chinese_ch7_speak", "name": "精神的三间小屋", "focus": "毕淑敏散文"},
        {"topic_id": "chinese_ch7_write", "name": "议论文写作指导", "focus": "论点论据论证"},
        {"topic_id": "chinese_ch8_classical", "name": "古诗词三首", "focus": "古诗词背诵积累"},
        {"topic_id": "chinese_ch8_pearl", "name": "湖心亭看雪", "focus": "张岱小品文"},
        {"topic_id": "chinese_ch8_bing", "name": "行路难（其一）", "focus": "李白诗再解读"},
        {"topic_id": "chinese_ch8_compose", "name": "演讲稿写作", "focus": "语言感染力训练"},
    ],
    
    "chinese/九年级下": [
        {"topic_id": "chinese_ch1_hero", "name": "祖国啊，我亲爱的祖国", "focus": "舒婷现代诗"},
        {"topic_id": "chinese_ch1_sky", "name": "立本", "focus": "当代诗歌鉴赏"},
        {"topic_id": "chinese_ch2_story", "name": "孔乙己", "focus": "鲁迅小说精读"},
        {"topic_id": "chinese_ch2_sell", "name": "变色龙", "focus": "契诃夫讽刺手法"},
        {"topic_id": "chinese_ch2_hat", "name": "溜索", "focus": "马识途小说"},
        {"topic_id": "chinese_ch2_read", "name": "小说阅读进阶", "focus": "人物形象分析"},
        {"topic_id": "chinese_ch3_play", "name": "屈原（节选）", "focus": "郭沫若历史剧"},
        {"topic_id": "chinese_ch3_drama", "name": "枣儿", "focus": "戏剧语言特点"},
        {"topic_id": "chinese_ch3_acting", "name": "戏剧表演基础", "focus": "台词与舞台"},
        {"topic_id": "chinese_ch3_write", "name": "戏剧剧本写作", "focus": "人物对话设计"},
        {"topic_id": "chinese_ch4_preqin", "name": "唐雎不辱使命", "focus": "战国策选读"},
        {"topic_id": "chinese_ch4_yuewang", "name": "隆中对", "focus": "三国志选读"},
        {"topic_id": "chinese_ch4_out", "name": "出师表", "focus": "诸葛亮名篇精读"},
        {"topic_id": "chinese_ch4_poem", "name": "诗词曲五首", "focus": "古诗词对比阅读"},
        {"topic_id": "chinese_ch4_classical", "name": "文言文翻译技巧", "focus": "实词虚词积累"},
        {"topic_id": "chinese_ch5_argue", "name": "谈读书", "focus": "培根随笔"},
        {"topic_id": "chinese_ch5_critique", "name": "不求甚解", "focus": "马南邨驳论文"},
        {"topic_id": "chinese_ch5_evidence", "name": "短文两篇", "focus": "议论文写法比较"},
        {"topic_id": "chinese_ch5_write", "name": "议论文写作进阶", "focus": "论证方法综合运用"},
        {"topic_id": "chinese_ch6_poem", "name": "诗词曲五首", "focus": "古诗词分类鉴赏"},
        {"topic_id": "chinese_ch6_flood", "name": "诗词曲五首", "focus": "古代诗歌吟诵"},
        {"topic_id": "chinese_ch6_exam", "name": "中考古诗文复习策略", "focus": "背诵默写技巧"},
    ],
    
    # ===== 英语 =====
    "english/九年级": [
        {"topic_id": "english_ch1_passive", "name": "被动语态详解", "focus": "一般现在时、过去时、将来时"},
        {"topic_id": "english_ch1_rel_clause", "name": "定语从句入门", "focus": "that/which/who用法"},
        {"topic_id": "english_ch2_conditional", "name": "条件状语从句", "focus": "if引导的条件句"},
        {"topic_id": "english_ch2_report", "name": "宾语从句", "focus": "陈述句、疑问句转述"},
        {"topic_id": "english_ch3_adv_clause", "name": "状语从句总结", "focus": "时间、地点、原因、条件"},
        {"topic_id": "english_ch3_compare", "name": "比较等级进阶", "focus": "最高级与比较级综合"},
        {"topic_id": "english_ch4_nonfinite", "name": "非谓语动词", "focus": "doing/to do/done用法"},
        {"topic_id": "english_ch4_word_form", "name": "词性转换技巧", "focus": "构词法与应用"},
        {"topic_id": "english_ch5_reading", "name": "阅读理解策略", "focus": "寻读、略读、推断"},
        {"topic_id": "english_ch5_vocabulary", "name": "中考高频词汇梳理", "focus": "核心词汇记忆"},
        {"topic_id": "english_ch6_writing", "name": "书面表达技巧", "focus": "句式升级与连贯"},
        {"topic_id": "english_ch6_email", "name": "应用文写作", "focus": "书信、通知、倡议书"},
        {"topic_id": "english_ch6_story", "name": "故事续写指导", "focus": "情节合理展开"},
    ],
    
    # ===== 历史 =====
    "history/九年级上": [
        {"topic_id": "hist_ch1_arab", "name": "阿拉伯帝国", "focus": "伊斯兰教兴起"},
        {"topic_id": "hist_ch2_byzantine", "name": "拜占庭帝国", "focus": "东罗马帝国兴衰"},
        {"topic_id": "hist_ch3_feudal", "name": "西欧庄园", "focus": "中世纪农村经济"},
        {"topic_id": "hist_ch3_city", "name": "中世纪城市", "focus": "城市的复兴"},
        {"topic_id": "hist_ch4_uni", "name": "文艺复兴", "focus": "人文主义兴起"},
        {"topic_id": "hist_ch4_columbus", "name": "新航路开辟", "focus": "地理大发现"},
        {"topic_id": "hist_ch5_america", "name": "早期殖民扩张", "focus": "葡萄牙、西班牙殖民"},
        {"topic_id": "hist_ch5_independence", "name": "美国独立战争", "focus": "独立与建国"},
        {"topic_id": "hist_ch6_france", "name": "法国大革命", "focus": "资产阶级革命"},
        {"topic_id": "hist_ch6_napoleon", "name": "拿破仑帝国", "focus": "法兰西第一帝国"},
        {"topic_id": "hist_ch7_industry", "name": "第一次工业革命", "focus": "蒸汽时代"},
        {"topic_id": "hist_ch7_marx", "name": "马克思主义诞生", "focus": "《共产党宣言》"},
    ],
    
    "history/九年级下": [
        {"topic_id": "hist_ch1_renaissance", "name": "文艺复兴运动", "focus": "思想解放先驱"},
        {"topic_id": "hist_ch1_columbus", "name": "哥伦布航海", "focus": "新大陆发现"},
        {"topic_id": "hist_ch1_global", "name": "世界市场雏形", "focus": "全球化开端"},
        {"topic_id": "hist_ch2_enlightenment", "name": "启蒙运动", "focus": "理性主义传播"},
        {"topic_id": "hist_ch2_american", "name": "美国独立战争", "focus": "1776年建国"},
        {"topic_id": "hist_ch2_french", "name": "法国大革命", "focus": "1789年革命"},
        {"topic_id": "hist_ch3_industrial", "name": "工业革命", "focus": "机械化生产"},
        {"topic_id": "hist_ch3_socialism", "name": "空想社会主义", "focus": "早期社会主义思潮"},
        {"topic_id": "hist_ch4_marx", "name": "马克思主义诞生", "focus": "1848年《宣言》"},
        {"topic_id": "hist_ch4_paris", "name": "巴黎公社", "focus": "无产阶级政权尝试"},
    ],
    
    # ===== 地理 =====
    "geography/九年级": [
        {"topic_id": "geo_ch1_asia", "name": "亚洲的自然环境", "focus": "地形、气候、河流"},
        {"topic_id": "geo_ch1_region", "name": "亚洲的分区", "focus": "东亚、东南亚、南亚等"},
        {"topic_id": "geo_ch2_japan", "name": "日本", "focus": "岛国特征与经济"},
        {"topic_id": "geo_ch2_india", "name": "印度", "focus": "人口与农业"},
        {"topic_id": "geo_ch3_middle", "name": "中东地区", "focus": "石油与水资源"},
        {"topic_id": "geo_ch3_europe", "name": "欧洲西部", "focus": "发达国家集中区"},
        {"topic_id": "geo_ch4_africa", "name": "撒哈拉以南非洲", "focus": "单一商品经济"},
        {"topic_id": "geo_ch4_latam", "name": "拉丁美洲", "focus": "种植业与矿产资源"},
        {"topic_id": "geo_ch5_russia", "name": "俄罗斯", "focus": "国土与资源"},
        {"topic_id": "geo_ch5_australia", "name": "澳大利亚", "focus": "骑在羊背上的国家"},
        {"topic_id": "geo_ch6_americas", "name": "美国", "focus": "发达国家代表"},
        {"topic_id": "geo_ch6_brazil", "name": "巴西", "focus": "发展中国家典型"},
        {"topic_id": "geo_ch7_antarctica", "name": "极地地区", "focus": "科学考察宝地"},
        {"topic_id": "geo_ch7_china", "name": "中国的区域差异", "focus": "四大地理区域"},
        {"topic_id": "geo_ch7_development", "name": "中国的经济发展", "focus": "工业与农业布局"},
    ],
    
    # ===== 道德与法治 =====
    "morality/九年级": [
        {"topic_id": "moral_ch1_achieve", "name": "踏上强国之路", "focus": "改革开放成就"},
        {"topic_id": "moral_ch1_reform", "name": "坚持改革开放", "focus": "改革的意义"},
        {"topic_id": "moral_ch1_china", "name": "中国担当", "focus": "大国责任与贡献"},
        {"topic_id": "moral_ch1_future", "name": "走向未来的中国", "focus": "两个百年目标"},
        {"topic_id": "moral_ch2_democracy", "name": "社会主义民主", "focus": "全过程人民民主"},
        {"topic_id": "moral_ch2_rule", "name": "法治中国建设", "focus": "全面依法治国"},
        {"topic_id": "moral_ch2_china", "name": "建设法治中国", "focus": "法治国家目标"},
        {"topic_id": "moral_ch3_opportunity", "name": "与世界紧相连", "focus": "经济全球化"},
        {"topic_id": "moral_ch3_open", "name": "谋求互利共赢", "focus": "对外开放战略"},
        {"topic_id": "moral_ch3_belt", "name": "一带一路倡议", "focus": "国际合作平台"},
        {"topic_id": "moral_ch4_culture", "name": "文化交流互鉴", "focus": "中华文化走出去"},
        {"topic_id": "moral_ch4_environment", "name": "构建人类命运共同体", "focus": "全球治理方案"},
    ],
}

def main():
    base_dir = Path("output")
    total = 0
    
    for key, topics in JIUNIANJI_TOPICS.items():
        subject = key.split("/")[0]
        grade = key.split("/")[1]
        
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
                "difficulty": 3,
                "created": "2026-09-18"
            }
            
            json_path = dir_path / f"{topic_id}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            
            total += 1
    
    print(f"✅ 已生成 {total} 个九年级知识点模板")
    print(f"\n分布:")
    for key, topics in JIUNIANJI_TOPICS.items():
        print(f"  {key}: {len(topics)}个")

if __name__ == "__main__":
    main()
