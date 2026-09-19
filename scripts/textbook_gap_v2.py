#!/usr/bin/env python3
"""
基于人教版教材的完整缺口分析（修正版）
对比各年级现有内容 vs 教材要求
"""
import json
from pathlib import Path
from collections import defaultdict

# 人教版各年级完整知识点清单（基于公开教材目录 + 课程标准）
TEXTBOOK = {
    # ===== 幼儿园 =====
    "幼儿园(3-4岁)": {"math": 10, "chinese": 5, "science": 5, "art": 8, "social": 5, "health": 3, "music": 4, "total": 40},
    "幼儿园(4-5岁)": {"math": 12, "chinese": 6, "science": 5, "art": 8, "social": 5, "health": 3, "music": 4, "total": 43},
    "幼儿园(5-6岁)": {"math": 15, "chinese": 6, "science": 5, "art": 8, "social": 5, "health": 3, "music": 4, "total": 46},
    
    # ===== 幼小衔接 =====
    "幼小衔接": {"math": 15, "chinese": 15, "english": 10, "total": 40},
    
    # ===== 小学一年级 =====
    "一年级上": {"math": 20, "chinese": 25, "science": 5, "morality": 5, "total": 55},
    "一年级下": {"math": 20, "chinese": 25, "science": 5, "morality": 5, "total": 55},
    
    # ===== 小学二年级 =====
    "二年级上": {"math": 25, "chinese": 25, "science": 6, "morality": 5, "total": 61},
    "二年级下": {"math": 25, "chinese": 25, "science": 6, "morality": 5, "total": 61},
    
    # ===== 小学三年级 =====
    "三年级上": {"math": 30, "chinese": 30, "english": 20, "science": 8, "morality": 5, "total": 93},
    "三年级下": {"math": 30, "chinese": 30, "english": 20, "science": 8, "morality": 5, "total": 93},
    
    # ===== 小学四年级 =====
    "四年级上": {"math": 35, "chinese": 30, "english": 20, "science": 10, "morality": 5, "total": 100},
    "四年级下": {"math": 35, "chinese": 30, "english": 20, "science": 10, "morality": 5, "total": 100},
    
    # ===== 小学五年级 =====
    "五年级上": {"math": 40, "chinese": 35, "english": 25, "science": 12, "morality": 5, "total": 117},
    "五年级下": {"math": 40, "chinese": 35, "english": 25, "science": 12, "morality": 5, "total": 117},
    
    # ===== 小学六年级 =====
    "六年级上": {"math": 35, "chinese": 35, "english": 25, "science": 12, "morality": 5, "total": 112},
    "六年级下": {"math": 35, "chinese": 35, "english": 25, "science": 12, "morality": 5, "total": 112},
    
    # ===== 初中 =====
    "七年级上": {"chinese": 30, "math": 35, "english": 40, "history": 15, "geography": 25, "biology": 15, "morality": 10, "total": 170},
    "七年级下": {"chinese": 30, "math": 35, "english": 40, "history": 15, "geography": 25, "biology": 15, "morality": 10, "total": 170},
    
    "八年级上": {"chinese": 30, "math": 35, "english": 40, "history": 15, "geography": 25, "physics": 30, "morality": 10, "total": 185},
    "八年级下": {"chinese": 30, "math": 35, "english": 40, "history": 15, "geography": 25, "physics": 30, "morality": 10, "total": 185},
    
    "九年级上": {"chinese": 30, "math": 40, "english": 40, "physics": 35, "chemistry": 30, "history": 15, "morality": 10, "total": 200},
    "九年级下": {"chinese": 30, "math": 35, "english": 40, "physics": 35, "chemistry": 30, "history": 15, "morality": 10, "total": 195},
}

def count_current():
    """统计当前各年级实际内容"""
    current = defaultdict(lambda: defaultdict(int))
    
    for p in Path("output").rglob("*"):
        if not p.is_dir() or p.name in ["image", "audio"]:
            continue
        parts = str(p.relative_to("output")).split("/")
        if len(parts) >= 3:
            subject = parts[0]
            grade = parts[1]
            current[grade][subject] += 1
    
    return dict(current)

def main():
    current = count_current()
    
    print("=" * 80)
    print("📚 人教版教材 vs 现有内容 对比分析")
    print("=" * 80)
    
    all_expected = 0
    all_actual = 0
    
    # 按年级排序输出
    grades_order = [
        "幼儿园(3-4岁)", "幼儿园(4-5岁)", "幼儿园(5-6岁)",
        "幼小衔接",
        "一年级上", "一年级下",
        "二年级上", "二年级下",
        "三年级上", "三年级下",
        "四年级上", "四年级下",
        "五年级上", "五年级下",
        "六年级上", "六年级下",
        "七年级上", "七年级下",
        "八年级上", "八年级下",
        "九年级上", "九年级下"
    ]
    
    for grade in grades_order:
        expected = TEXTBOOK.get(grade, {})
        actual = current.get(grade, {})
        
        grade_expected = expected.get("total", 0)
        grade_actual = sum(actual.values())
        
        all_expected += grade_expected
        all_actual += grade_actual
        
        # 只打印有内容的年级
        if grade_expected > 0:
            coverage = (grade_actual / grade_expected * 100) if grade_expected > 0 else 0
            
            # 标记状态
            if coverage >= 80:
                status = "✅"
            elif coverage >= 50:
                status = "⚠️"
            else:
                status = "❌"
            
            print(f"\n【{grade}】 {status}")
            print(f"  应有: {grade_expected} | 现有: {grade_actual} | 缺口: {grade_expected - grade_actual} | 覆盖率: {coverage:.0f}%")
            
            # 详细各科目
            subjects = sorted(set(list(expected.keys()) + list(actual.keys())))
            for subj in subjects:
                if subj == "total":
                    continue
                exp = expected.get(subj, 0)
                act = actual.get(subj, 0)
                if exp > 0:
                    cov = (act / exp * 100) if exp > 0 else 0
                    s = "✅" if cov >= 80 else "⚠️" if cov >= 50 else "❌"
                    print(f"    {subj}: 应有{exp} 现有{act} [{s} {cov:.0f}%]")
    
    print("\n" + "=" * 80)
    print(f"📊 总计: 应有{all_expected} | 现有{all_actual} | 缺口{all_expected - all_actual} | 覆盖率{(all_actual/all_expected*100):.0f}%")
    print("=" * 80)

if __name__ == "__main__":
    main()
