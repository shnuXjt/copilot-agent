from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool

# ===================== 原生函数（自检/调用逻辑） =====================
def duckduckgo_search_raw(query: str, max_results: int = 3) -> str:
    """
    DuckDuckGo 联网搜索原生函数
    用于：自检、直接调用、业务逻辑
    """
    try:
        search = DuckDuckGoSearchRun(max_results=max_results)
        return search.run(query)
    except Exception as e:
        return f"❌ DuckDuckGo 搜索失败：{str(e)}"

# ===================== 工具暴露（自动被注册中心发现） =====================
# 直接实例化官方 Tool，自动被 ToolRegistry 扫描注册
duckduckgo_search = DuckDuckGoSearchRun()
# 重命名工具名（可选，方便识别）
duckduckgo_search.name = "duckduckgo_search"
duckduckgo_search.description = "联网搜索工具，使用DuckDuckGo查询实时新闻、资讯、知识、数据"