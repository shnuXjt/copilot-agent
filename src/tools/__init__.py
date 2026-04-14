import importlib.util
import os
from src.logger import logger
from langchain.tools import BaseTool
# 全局工具注册中心（单例）
class ToolRegistry:
    _instance = None
    _tools = {} # 存储所欲呕工具：{tool_name: tool_func}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._auto_discover()
        return cls._instance

    @classmethod
    def _auto_discover(cls):
        """自动扫描tools目录下所有工具文件夹，动态注册"""
        current_dir = os.path.dirname(__file__)
        # 遍历目录下所有的.py文件
        for filename in os.listdir(current_dir):
            if filename.endswith(".py") and filename not in ["__init__.py"]:
                module_name = filename[:-3]
                module_path = os.path.join(current_dir, filename)
                cls._load_module(module_name, module_path)
        logger.info(f"✅ 工具自动发现完成，共加载 {len(cls._tools)} 个工具")

    @classmethod
    def _load_module(cls, module_name: str, module_path: str):
        """动态加载模块并注册带@tool装饰的函数"""
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 自动提取模块中所有 LangChain Tool对象
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, BaseTool):
                    cls._tools[attr_name] = attr
                    logger.debug(f"🔍 发现工具：{attr_name}")
        except Exception as e:
            logger.warning(f"⚠️ 加载工具 {module_name} 失败：{str(e)}")

    @classmethod
    def get_tool(cls, tool_name: str):
        """根据名称获取工具"""
        return cls._tools.get(tool_name)

    @classmethod
    def get_all_tools(cls):
        """获取所有工具"""
        return list(cls._tools.values())

# 初始化全局注册中心
tool_registry  = ToolRegistry()
