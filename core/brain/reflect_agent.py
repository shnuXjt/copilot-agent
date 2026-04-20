# 反思智能体
from adapter import legacy_adapter


class ReflectAgent:
    """反思曾： 纠错 + 优化 + 防幻觉"""
    def refine(self, skill_type: str, task: str, raw_result: str) -> str:
        # 自检
        pass_flag, msg = legacy_adapter.checker.full_check(skill_type, task, raw_result)
        if not pass_flag:
            return f"⚠️ 结果优化：{raw_result}\n（校验提示：{msg}）"

        return raw_result