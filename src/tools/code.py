from langchain_experimental.tools import PythonREPLTool


# ====================== 原生函数 ==============================
def python_analyze_raw(query: str) -> str:
    try:
        analyze = PythonREPLTool()
        return analyze.run(query)
    except Exception as e:
        return  f"❌ PythonREPLTool 失败：{str(e)}"

# ============ 工具暴露 ================
code_analyze = PythonREPLTool()