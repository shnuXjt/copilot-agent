from datetime import datetime

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
import pandas as pd
from langchain_core.tools import StructuredTool
from langchain_experimental.tools import PythonREPLTool


# 封装工具

# 封装联网搜索工具
def get_search_tool():
    return DuckDuckGoSearchRun()

# 计算器工具
@tool
def calculator(expesstion: str) -> str:
    '''计算器，输入数字表达式，返回计算结果'''
    try:
        return str(eval(expesstion))
    except:
        return '计算失败'

# 导出所有工具
def get_all_tools():
    return [get_search_tool(), calculator]


# ============================ Excel数据分析工具 ===============================

def get_excel_reader_tool():
    '''读取Excel文件，返回表格结构信息'''
    def excel_reader(file_path: str) -> str:
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
            info = f"""
✅ Excel读取成功！
文件路径： {file_path}
行数： {len(df)}
列名： {list(df.columns)}
头部数据：
{df.head().to_string()}
数据类型：
{df.dtypes.to_string()}
基础统计：
{df.describe().to_string()}
"""
            return info
        except Exception as e:
            return f"❌ 读取Excel失败： {str(e)}"
    # 包装为langchain工具
    return StructuredTool.from_function(
        name="excel_reader",
        description="用于读取Excel文件， 获取数据结构，前几行，基础统计信息",
        func=excel_reader
    )

def get_python_analyze_tool():
    '''Python 代码执行工具（用于pandas数据分析，计算）'''
    return PythonREPLTool()

# excel 工具出口
def get_excel_tools():
    return [get_excel_reader_tool(), get_python_analyze_tool()]

# ==================== 🔥 超级工具集合（全部整合） =========================
def get_super_agent_tools():
    return [
        get_search_tool(),
        calculator,
        get_excel_reader_tool(),
        get_python_analyze_tool()
    ]

# ================== 时间日期工具 ===========================
@tool
def get_current_datetime() -> str:
    """
    获取当前系统日期，时间，星期几
    用于需要知道今天日期，时间，时间计算的场景
    :return:
    """
    now = datetime.now()
    weekday = ['一', '二', '三', '四', '五', '六', '日'][now.weekday()]
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')} 星期{weekday}"

def get_datetime_tool():
    return get_current_datetime