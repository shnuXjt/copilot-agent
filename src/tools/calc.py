from langchain.tools import tool
import re

# 原生函数
def extract_math_expression(text: str) -> str:
    pattern = r'[\d\+\-\*/\(\)\.]+'
    matches = re.findall(pattern, text)
    return max(matches, key=len) if matches else text

def calculate_math(expression: str) -> str:
    try:
        return str(eval(expression.strip()))
    except:
        return "计算错误"

# Agent 工具
@tool
def calculator(expression: str) -> str:
    """计算器工具，用于数学计算"""
    return calculate_math(extract_math_expression(expression))