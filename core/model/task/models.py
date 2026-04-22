from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from config_loader import config_loader

# 从配置读取任务参数
task_config = config_loader.model_config["task"]["dag"]

class TaskNode(BaseModel):
    """DAG任务节点模型： 适配配置化参数"""
    task_id: int
    skill: str
    task: str
    depend_on: List[int] = Field(default_factory=list)
    params: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    timeout: int = Field(default=task_config["node_timeout"])

class TaskDAG(BaseModel):
    """DAG任务图模型： 适配配置化并行数量"""
    nodes: List[TaskNode] = Field(default_factory=list)
    max_parallel: int = Field(default=task_config["max_parallel"])

