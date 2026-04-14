from langchain.tools import tool
from datetime import datetime

# 原生函数（自检专用）
def get_current_datetime_raw() -> str:
    now = datetime.now()
    weekday = ['一', '二', '三', '四', '五', '六', '日'][now.weekday()]
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{weekday}"

# Agent 工具（自动被注册中心发现）
@tool
def get_current_datetime() -> str:
    """获取当前系统日期、时间、星期几"""
    return get_current_datetime_raw()