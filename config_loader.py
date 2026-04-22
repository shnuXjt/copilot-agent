import os.path
from typing import Dict, Any

import yaml

# 配置文件根目录
CONFIG_DIR = "./config"

class ConfigLoader:
    """配置加载器，统一读取所有yaml配置，单例模式"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.load_all_configs()
        return cls._instance

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载单个yaml配置文件"""
        config_path = os.path.join(CONFIG_DIR, config_file)
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在： {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_all_configs(self):
        """加载所有的分层配置"""
        self.model_config = self.load_config("model_config.yaml")
        self.control_config = self.load_config("control_config.yaml")
        self.protocol_config = self.load_config("protocol_config.yaml")

# 全局单例，工各层调用
config_loader = ConfigLoader()