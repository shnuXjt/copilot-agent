# DAG任务结构
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

class TaskNode(BaseModel):
    task_id: int
    skill: str
    task: str
    depend_on: List[int] =Field(default_factory=list)
    params: Optional[Dict[str, Any]] = None
    result: Optional[str] = None


class TaskDAG(BaseModel):
    nodes: List[TaskNode] = Field(default_factory=list)
    