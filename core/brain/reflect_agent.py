# 反思智能体
from adapter import legacy_adapter


class ReflectAgent:
    """反思曾： 纠错 + 优化 + 防幻觉"""
    def refine(self, skill_type: str, task: str, raw_result: str, retry = 1) -> str:
        # 自检
        pass_flag, msg = legacy_adapter.checker.full_check(skill_type, task, raw_result)
        if not pass_flag and retry > 0:

            try:
                skill = legacy_adapter.get_skill(skill_type)
                if skill:
                    new_result = skill.run(task)
                    return self.refine(skill_type, task, new_result, retry = 0)
            except:
                pass

        if not pass_flag:
            return f"⚠️ 结果可能异常：{raw_result}\n提示：{msg}"

        return raw_result