# K12学习 CONTENT 知识库

> 面向幼儿园到初中的离线学习内容库
> 年龄段分级：幼儿园 / 小学低年级 / 小学高年级 / 初中
> 语音支持：幼儿园必须，1-2年级推荐，3年级以上可选

---

## 📁 目录结构

```
learning-content/
├── kindergarten/          # 幼儿园（3-6岁）
│   ├── math/             # 数学
│   │   ├── number_recognition.json      # 认识数字
│   │   ├── counting.json                # 数数
│   │   └── simple_addition.json         # 10以内加法
│   ├── chinese/          # 语文
│   └── science/          # 科学
├── grade1/               # 一年级
│   ├── math/
│   ├── chinese/
│   └── ...
├── grade2/               # 二年级
├── grade3/               # 三年级
├── grade4/               # 四年级
├── grade5/               # 五年级
├── grade6/               # 六年级
├── grade7/               # 七年级（初中）
├── grade8/               # 八年级
├── grade9/               # 九年级
├── scripts/              # 生成脚本
│   ├── curriculum_bot.py    # 课程设计Bot
│   ├── visual_bot.py        # 视觉设计Bot
│   ├── audio_bot.py         # 语音设计Bot
│   └── qa_bot.py            # 质检Bot
├── knowledge_graph.json  # 知识点总图谱
└── README.md
```

---

## 🎯 年龄段内容策略

### 幼儿园（3-6岁）

| 特点 | 策略 |
|------|------|
| 认知水平 | 具象思维为主，需要大量图像和声音 |
| 学习内容 | 基本概念、生活常识、简单游戏 |
| 语音要求 | ✅ **必须**所有文本都需语音 |
| 界面风格 | 大按钮、鲜艳颜色、动画反馈 |
| 题目类型 | 选择题、连线题、拖拽题 |
| 学习时长 | 单次10-15分钟 |

**示例知识点**：
- 认识数字1-10
- 数数（1-20）
- 形状认知（圆形、正方形、三角形）
- 颜色认知（红黄蓝绿）

---

### 小学低年级（1-2年级）

| 特点 | 策略 |
|------|------|
| 认知水平 | 从具象向抽象过渡，需要图像辅助 |
| 学习内容 | 基础概念、简单运算、识字写字 |
| 语音要求 | ✅ **推荐**核心概念语音辅助 |
| 界面风格 | 彩色、鼓励性动画、游戏化 |
| 题目类型 | 选择题、填空题、简单的看图题 |
| 学习时长 | 单次20-30分钟 |

**示例知识点**：
- 10以内加减法
- 20以内加减法
- 认识时间
- 基础汉字（一、二、三...）

---

### 小学高年级（3-6年级）

| 特点 | 策略 |
|------|------|
| 认知水平 | 抽象思维发展，能理解复杂概念 |
| 学习内容 | 系统知识、逻辑推理、解题技巧 |
| 语音要求 | ⚠️ **可选**用户可开关 |
| 界面风格 | 简洁专业、信息密度适中 |
| 题目类型 | 选择题、填空题、计算题、应用题 |
| 学习时长 | 单次30-45分钟 |

**示例知识点**：
- 分数运算
- 小数运算
- 几何图形面积周长
- 基础英语语法

---

### 初中（7-9年级）

| 特点 | 策略 |
|------|------|
| 认知水平 | 抽象逻辑思维成熟，能处理复杂问题 |
| 学习内容 | 系统化知识、应试技巧、深度理解 |
| 语音要求 | ❌ **不需要** |
| 界面风格 | 严肃高效、减少干扰元素 |
| 题目类型 | 选择题、填空题、解答题、证明题 |
| 学习时长 | 单次45-60分钟 |

**示例知识点**：
- 一元二次方程
- 函数基础
- 几何证明
- 物理力学基础

---

## 📋 知识点JSON格式规范

### 核心字段

```json
{
  "id": "math_kg_number_recognition",
  "version": "1.0.0",
  "created_at": "2026-09-16",
  "updated_at": "2026-09-16",
  
  "metadata": {
    "subject": "math",
    "grade_level": "kindergarten",
    "chapter": "数字认知",
    "topic": "认识数字1-10",
    "keywords": ["数字", "计数", "识别"]
  },
  
  "age_appropriate": {
    "min_age": 3,
    "max_age": 6,
    "cognitive_level": "concrete",
    "learning_style": "visual_auditory",
    "attention_span_minutes": 10
  },
  
  "learning_objectives": [
    "能识别数字1-10的形状",
    "能将数字与对应数量匹配",
    "能按顺序读出数字1-10"
  ],
  
  "content": {
    "concept": "数字是用来表示数量的符号...",
    "explanation": "每个数字都有独特的形状...",
    "examples": [
      {
        "text": "1个苹果",
        "image": "examples/1-apple.png",
        "audio": "audio/examples/1-apple.mp3"
      }
    ],
    "common_mistakes": ["把6和9搞混"],
    "tips": ["用手指指着数可以帮助记忆"]
  },
  
  "practice": [
    {
      "id": "p001",
      "type": "multiple_choice",
      "difficulty": 1,
      "question": "下面哪个是数字3？",
      "options": ["1", "2", "3", "4"],
      "answer": "3",
      "explanation": "数字3的形状像半个耳朵",
      "feedback": {
        "correct": "太棒了！你认识数字3了！",
        "incorrect": "再仔细看哦，数字3像半个耳朵"
      }
    }
  ],
  
  "gamification": {
    "badge": "数字小达人",
    "points": 10,
    "streak_bonus": 1.5,
    "tip": "你已经认识了数字1-10！"
  },
  
  "accessibility": {
    "audio_required": true,
    "audio_languages": ["zh-CN"],
    "text_size": "large",
    "contrast": "high"
  },
  
  "prerequisites": [],
  "related_topics": ["math_kg_counting"],
  "estimated_time_minutes": 5
}
```

---

## 🔧 生成流程（多Bot工作流）

```
Phase 1: CurriculumBot（课程设计）
  → AGNES-2.5-flash 生成文本内容
  → 包含：概念讲解、例子、练习题
  
Phase 2: VisualBot（视觉设计）
  → AGNES-image-2.1-flash 生成配图
  → 为每个例子生成对应插图
  
Phase 3: AudioBot（语音合成）
  → Edge-TTS 生成语音
  → 幼儿园/1-2年级必须
  → 音色：小班用温柔女声，高年级用中性男声
  
Phase 4: QA bot（质检）
  → AGNES-3.0-flash 审核内容
  → 检查：正确性、难度、格式、版权
  
Phase 5: SyncBot（同步）
  → GitHub API 提交到知识库
  → 学习机端检测更新并下载
```

---

## 🎨 年龄适配规则

### 语言风格

| 年龄段 | 语言特点 | 示例 |
|--------|---------|------|
| 幼儿园 | 简单短句、重复强调、拟人化 | "数字1像铅笔，直直的站那里" |
| 小学低 | 通俗易懂、生活化例子 | "就像你有2个苹果，妈妈又给你3个..." |
| 小学高 | 规范表述、逻辑清晰 | "加法是将两个数合并成一个数的运算" |
| 初中 | 专业术语、严谨表述 | "一元二次方程是指含有一个未知数..." |

### 题目难度

| 年龄段 | 难度梯度 | 题目数量 |
|--------|---------|---------|
| 幼儿园 | 1级（基础识别） | 3-5道 |
| 小学低 | 1-2级（基础+简单应用） | 5-8道 |
| 小学高 | 1-3级（基础+应用+提升） | 8-12道 |
| 初中 | 1-4级（基础+应用+提升+挑战） | 10-15道 |

### 语音配置

```python
VOICE_CONFIG = {
    'kindergarten': {
        'voice': 'zh-CN-XiaoxiaoNeural',
        'required': True,
        'speed': 0.9,  # 稍慢，适合幼儿
        'pitch': 1.1   # 稍高，更亲切
    },
    'grade1': {
        'voice': 'zh-CN-XiaoxiaoNeural',
        'required': True,
        'speed': 0.95,
        'pitch': 1.05
    },
    'grade2': {
        'voice': 'zh-CN-YunxiNeural',
        'required': False,  # 可选
        'speed': 1.0,
        'pitch': 1.0
    },
    'grade3-9': {
        'voice': 'zh-CN-YunxiNeural',
        'required': False,
        'speed': 1.0,
        'pitch': 1.0
    }
}
```

---

## 📚 学习内容来源

### 官方公开资料（可用）

| 来源 | 内容 | 使用方式 |
|------|------|---------|
| 教育部课程标准 | 知识点大纲 | 参考框架，不直接引用原文 |
| 国家中小学智慧教育平台 | 教学案例 | 参考教学设计，原创内容 |
| Marble Curriculum | 知识点图谱 | CC BY-SA 4.0，可商用 |

## 📚 版权说明

### 可以用的
- 自己写的知识点讲解
- 生活中的例子（比如苹果、小鸟、花朵）
- AI生成的练习题
- 教育部公开的课标框架

### 不能用的
- 直接复制教材原文
- 网上找的受版权保护的图
- 盗版题库

---

## 🚀 下一步

| 任务 | 状态 |
|------|------|
| 创建仓库 | ✅ 完成 |
| 设计格式 | ✅ 完成 |
| 写生成脚本 | ✅ 完成 |
| 生成示例 | ✅ 已完成（认识数字1-3） |
| 批量生成更多 | ⏳ 待做 |

**本周目标**：
- 幼儿园数学：10个知识点
- 小学1-2年级：5个知识点
- 验证完整流程（生成→语音→质检→入库）

---

## 📝 如何添加新知识点

1. 在 `knowledge_graph.json` 加条目
2. 跑脚本：`python scripts/generate.py --topic=<id>`
3. 人工检查质量
4. 提交PR

**审核标准**：
- 内容对不对？
- 难度适不适合这个年龄？
- 语言自然吗？
- 题目有答案和解释吗？
- 语音清楚吗（需要的话）？

---

**仓库链接**：https://github.com/RedSamerai/learning-content
