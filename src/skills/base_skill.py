from abc import abstractmethod

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE


class BaseSkill:
    """
    [通用技能基类]
    1. 封装所有重复逻辑
    2. 直接继承 Agent 执行能力
    3. 完全替代原来的worker
    """
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
    def run(self, task: str, context: str=""):
        full_task = f"上下午： {context}\n 任务：{task}" if context else task
        result = self.executor.invoke({"input": full_task })
        return result['output']