import json
from abc import ABC, abstractmethod

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE
from src.memory import agent_memory
from src.self_checker import self_checker
from src.logger import logger
import re

# 抽象基类： 自动初始化，子类无需写任何__init__
class BaseSkill(ABC):
    """
    [通用技能基类]
    1. 封装所有重复逻辑
    2. 直接继承 Agent 执行能力
    3. 完全替代原来的worker
    """

    # 子类只需要定义这个类属性， 自动生效
    skill_type: str

    def __init__(self):
        # 统一LLM
        self.llm = ChatOpenAI(
            model=MODEL_NAME,
            api_key=MODEL_API_KEY,
            base_url=MODEL_BASE_URL,
            temperature=0
        )

        # 制动创建执行器（ Skill自己就是可执行单元）
        self.executor = self._create_executor()

        self.skill_type = self.skill_type # 技能类型： search/excel/calc/datetime

    @property
    @abstractmethod
    def tools(self):
        """子类必须实现： 技能需要的工具"""
        pass

    @property
    @abstractmethod
    def system_prompt(self):
        """子类必须实现： 技能专业提示词"""
        pass

    # ============================= 技能参数规范化 ====================================
    @property
    def parameters(self) -> dict:
        """
        【参数规范】每个技能重写此方法， 定义入参JSON Schema
        格式： {"name": 参数名, "type": 类型, "required": 是否必选， “desc"： m描述}
        无参技能返回空列表即可
        """
        return []

    def validate_parameters(self, task_input: str) -> tuple[bool, str, dict | str]:
        """
        【自动校验】 解析并校验任务参数是否符合当前技能规范
        返回： （是否通过，提示信息， 解析后的参数清单）
        """
        try:
            params = {}
            params_schema = self.parameters
            required_params = [p["name"] for p in params_schema if p.get("required")]

            # 无参数技能： 直接通过
            if not params_schema:
                return True, "无参数要求", {}

            # 构建参数提取prompt （让LLM按照Schema提取参数)
            schema_str = "\n".join([
                f"- {p['name']}：{p['desc']}（类型：{p['type']}，必选：{p['required']}）"
                for p in params_schema
            ])

            extract_prompt= f"""
            任务： 从用户输入中提取指定参数， 仅返回标准JSON，无任何多余文字
            参数定义：
            {schema_str}
            用户输入： {task_input}
            输出格式： {{"{params_schema[0]['name']}": "提取结果“}}
            """

            # LLM提取参数
            llm_response = self.llm.invoke(extract_prompt).content.strip()
            # 清理LLM返回的多余字符
            llm_response = re.sub(r"```(json)?|```","", llm_response).strip()
            extracted_params = json.loads(llm_response)

            # 赋值并校验参数
            for param in params_schema:
                name = param["name"]
                # 从LLM提取结果并复制
                params[name] = extracted_params.get(name, "").strip()
                # 必选参数非空检验
                if param.get("required") and not params[name]:
                    return False, f"缺少必选参数：{name}（{param['desc']}）", {}
            return True, "参数校验通过", params
        except Exception as e:
            return False, f"参数解析失败： {str(e)}", {}

    def _create_executor(self) -> AgentExecutor:
        """统一创建Agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=VERBOSE,
            handle_parsing_errors=True
        )
    # 技能直接可以运行，不需要worker
    def run(self, task: str, context: str="", session_id: str = None) -> str:
        logger.info(f"[{self.skill_type}] 执行任务： {task}")

        # 参数自动校验（新增）
        valid, msg, params = self.validate_parameters(task)
        logger.info(f"参数校验：{valid}, {msg}, {params}")
        if not valid:
            err = f"❌ 参数错误：{msg}"
            logger.error(err)
            return err

        # 获取对话历史
        history_prompt = agent_memory.get_history_prompt(session_id)
        full_task = f"{history_prompt}\n当前任务：{task}\n上下文： {context} " if context else task
        retry = 0

        # 自动重试机制
        while retry <= self_checker.max_retry:
            # 1. 执行技能
            result = self.executor.invoke({"input": full_task})["output"]
            logger.info(f"📌 第{retry+1}次执行结果：{result[:50]}...")

            # 2. 三级自检
            is_pass, msg = self_checker.full_check(
                skill_type=self.skill_type,
                task=full_task,
                result=result
            )

            # 3. 校验通过 -> 返回结果
            if is_pass:
                return result

            # 4. 不通过 -> 重试
            retry += 1
            logger.warning(f"❌ 自检失败，第{retry}次重试...")

        # 最大重试后仍失败
        return "⚠️ 多次校验失败，无法保证结果正确性，请重试任务"