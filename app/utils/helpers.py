"""
工具函数模块
"""
from datetime import datetime


def generate_plan_number():
    """
    生成采购计划编号

    格式：PP-YYYYMMDD-XXXX
    PP: Procurement Plan 前缀
    YYYYMMDD: 日期
    XXXX: 四位序号

    Returns:
        str: 采购计划编号
    """
    now = datetime.utcnow()
    date_prefix = now.strftime('%Y%m%d')
    # 简单实现，实际应用中应该从数据库获取当日最大序号
    import random
    seq = str(random.randint(1000, 9999))
    return f"PP-{date_prefix}-{seq}"


def format_currency(amount, currency='CNY'):
    """
    格式化货币显示

    Args:
        amount: 金额
        currency: 币种

    Returns:
        str: 格式化后的货币字符串
    """
    symbols = {
        'CNY': '¥',
        'USD': '$',
        'EUR': '€'
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_date(date_obj, format_str='%Y-%m-%d'):
    """
    格式化日期

    Args:
        date_obj: 日期对象
        format_str: 格式字符串

    Returns:
        str: 格式化后的日期字符串
    """
    if date_obj is None:
        return ''
    return date_obj.strftime(format_str)


def format_datetime(datetime_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """
    格式化日期时间

    Args:
        datetime_obj: 日期时间对象
        format_str: 格式字符串

    Returns:
        str: 格式化后的日期时间字符串
    """
    if datetime_obj is None:
        return ''
    return datetime_obj.strftime(format_str)


def number_to_chinese(amount):
    """
    将数字转换为中文大写金额

    Args:
        amount: 数字金额

    Returns:
        str: 中文大写金额
    """
    if amount is None or amount == 0:
        return '零元整'

    CHINESE_NUMS = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    CHINESE_UNITS = ['', '拾', '佰', '仟']
    CHINESE_BIG_UNITS = ['', '万', '亿', '兆']

    # 处理负数
    negative = amount < 0
    amount = abs(amount)

    # 分离整数和小数部分
    integer_part = int(amount)
    decimal_part = round((amount - integer_part) * 100)

    if integer_part == 0 and decimal_part == 0:
        return '零元整'

    def convert_integer(num):
        """转换整数部分"""
        if num == 0:
            return ''

        result = ''
        unit_pos = 0
        need_zero = False

        while num > 0:
            section = num % 10000
            if need_zero:
                result = CHINESE_NUMS[0] + result
            section_str = ''
            section_need_zero = False

            for i in range(4):
                digit = section % 10
                if digit == 0:
                    section_need_zero = True
                else:
                    if section_need_zero:
                        section_str = CHINESE_NUMS[0] + section_str
                    section_str = CHINESE_NUMS[digit] + CHINESE_UNITS[i] + section_str
                    section_need_zero = False
                section //= 10

            if section_str:
                section_str += CHINESE_BIG_UNITS[unit_pos]
                result = section_str + result

            need_zero = section_need_zero
            num //= 10000
            unit_pos += 1

        return result

    # 转换整数部分
    chinese_integer = convert_integer(integer_part)
    if chinese_integer:
        chinese_integer += '元'

    # 转换小数部分
    chinese_decimal = ''
    if decimal_part > 0:
        jiao = decimal_part // 10
        fen = decimal_part % 10
        if jiao > 0:
            chinese_decimal += CHINESE_NUMS[jiao] + '角'
        if fen > 0:
            chinese_decimal += CHINESE_NUMS[fen] + '分'
        elif jiao > 0:
            chinese_decimal += '整'
    else:
        chinese_decimal = '整'

    result = ('负' if negative else '') + chinese_integer + chinese_decimal
    return result if result != '整' else '零元整'


def now():
    """返回当前时间，用于模板中调用"""
    return datetime.utcnow()
