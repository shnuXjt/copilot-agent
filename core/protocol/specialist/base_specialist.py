from config_loader import config_loader

# 从配置读取接口规范
interface_config = config_loader.protocol_config["interface"]

class BaseSpecialist:
    """专家子智能体基类：标准化接口，适配配置"""
    name = "base"
    description = "基础专家"

    # 标准化调用接口（配置指定接口名）
    def __call__(self, task: str, session_id: str, context: str = "") -> str:
        return self.run(task, session_id, context)

    def run(self, task: str, session_id: str, context: str = "") -> str:
        """标准化运行接口，子类必须实现"""
        raise NotImplementedError("子类必须实现 run 方法")
