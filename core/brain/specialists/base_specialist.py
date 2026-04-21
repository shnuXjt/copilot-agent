class BaseSpecialist:
    name = "base"
    description = "专家基类"

    def run(self, task: str, session_id: str, context: str="") -> str:
        raise NotImplementedError