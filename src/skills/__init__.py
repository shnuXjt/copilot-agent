# src/skills/__init__.py
from .search_skill import SearchSkill
from .excel_skill import ExcelSkill
from .datetime_skill import DatetimeSkill  # 极简工具，直接加

MCP_TOOLS = [
    SearchSkill(),
    ExcelSkill(),
    DatetimeSkill()  # 无缝集成
]