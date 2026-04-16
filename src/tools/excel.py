import pandas as pd
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


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

class ExcelInput(BaseModel):
    file_path: str = Field(description="Excel文件路径，如：data/sales.xlsx")
# 自动被注册中心发现
excel_analyzer = StructuredTool(
    name="excel_analyzer",
    description="分析Excel表格，支持读取、统计、求和、查看列名",
    func=excel_reader,
    args_schema=ExcelInput
)
