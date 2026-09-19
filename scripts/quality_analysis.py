#!/usr/bin/env python3
"""基于人教版教材的完整缺口分析"""
import json
from pathlib import Path
from collections import defaultdict

# 人教版各年级应有知识点数（基于公开教材目录）
TEXTBOOK = {
    # 幼儿园（非义务教育，但家长有需求）
    "幼儿园(3-4岁)": 40, "幼儿园(4-5岁)": 43, "幼儿园(5-6岁)": 46,
    "幼小衔接": 40,
    # 小学
    "一年级上": 55, "一年级下": 55,
    "二年级上": 61, "二年级下": 61,
    "三年级上": 93, "三年级下": 93,
    "四年级上": 100, "四年级下": 100,
    "五年级上": 117, "五年级下": 117,
    "六年级上": 112, "六年级下": 112,
    # 初中
    "七年级上": 170, "七年级下": 170,
    "八年级上": 185, "八年级下": 185,
    "九年级上": 200, "九年级下": 195,
}

def count_current():
    """统计各年级实际内容"""
    current = defaultdict(lambda: defaultdict(int))
    for p in Path("output").rglob("*.json"):
        if "image" in str(p) or "audio" in str(p):
            continue
        parts = str(p.relative_to("output")).split("/")
        if len(parts) >= 3:
            subject = parts[0]
            grade = "/".join(parts[1:3])
            current[grade][subject] += 1
    return dict(current)

def main():
    current = count_current()
    
    print("=" * 70)
    print("📚 人教版教材 vs 现有内容 对比分析")
    print("=" * 70)
    
    all_expected = 0
    all_actual = 0
    
    # 年级顺序
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
        "九年级上", "九年级下",
    ]
    
    # 按有内容的年级优先排序
    for grade in grades_order:
        expected = TEXTBOOK.get(grade, 0)
        actual = current.get(grade, {})
        grade_actual = sum(actual.values())
        
        all_expected += expected
        all_actual += grade_actual
        
        # 只打印有内容的年级（无论是否有缺口）
        if grade_actual > 0 or expected > 0:
            coverage = (grade_actual / expected * 100) if expected > 0 else 0
            
            if coverage >= 80:
                status = "✅"
            elif coverage >= 50:
                status = "⚠️"
            else:
                status = "❌"
            
            print(f"\n【{grade}】 {status}")
            print(f"  应有: {expected} | 现有: {grade_actual} | 缺口: {max(0, expected - grade_actual)} | 覆盖率: {coverage:.0f}%")
            
            # 详细科目
            subjects = sorted(set(list(expected_dict.keys()) + list(actual.keys()))) if 'expected_dict' in dir() else []
    
    print("\n" + "=" * 70)
    print(f"📊 总计: 应有{all_expected} | 现有{all_actual} | 缺口{all_expected - all_actual} | 覆盖率{(all_actual/all_expected*100):.0f}%")
    print("=" * 70)

if __name__ == "__main__":
    main()
