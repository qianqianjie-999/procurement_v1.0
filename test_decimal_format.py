#!/usr/bin/env python3
"""
测试数量字段的小数格式化
"""
from decimal import Decimal

def test_decimal_formatting():
    """测试小数格式化"""
    test_cases = [
        (Decimal('10'), '10.0'),
        (Decimal('10.5'), '10.5'),
        (Decimal('10.55'), '10.6'),  # 四舍五入到1位小数
        (Decimal('0'), '0.0'),
        (None, '-'),
    ]
    
    print("🧪 测试数量字段1位小数格式化:")
    for value, expected in test_cases:
        if value is not None:
            formatted = f"{value:.1f}"
            status = "✅" if formatted == expected else "❌"
            print(f"   {status} {value} → {formatted} (期望: {expected})")
        else:
            formatted = '-'
            status = "✅" if formatted == expected else "❌"
            print(f"   {status} None → {formatted} (期望: {expected})")

if __name__ == '__main__':
    test_decimal_formatting()
    print("\n🎉 所有测试完成！")