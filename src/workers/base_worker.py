from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE


class BaseWorker:
    """
    【通用Worker基类】
    封装所有Agent Worker的重复逻辑： LLM初始化， prompt构建，Agent构建
    子类只需要传入： 工具列表 + 系统提示词
    """
    def __init__(self, tools: list, system_prompt: str):
        # 构建LLM
        self.llm = ChatOpenAI(
            model=MODEL_NAME,
            api_key=MODEL_API_KEY,
            base_url=MODEL_BASE_URL,
            temperature=0
        )

        # 子类传入tools
        self.tools = tools
        # 子类传入专属提示词
        self.system_prompt = system_prompt

        # 统一创建Agent
        self.agent_executor = self.create_agent()


    def _create_agent(self) -> AgentExecutor:
        """【私有方法】统一构建Prompt + Agent + Executor"""
        # 通用prompt模板
        prompt =ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # 创建agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        # 返回执行器
        return AgentExecutor(
            agent = agent,
            tools = self.tools,
            verbose=VERBOSE,
            handle_parsing_errors=True
        )

    def get_worker(self) -> AgentExecutor:
        """对外暴露： 获取Worker执行器"""
        return self.agent_executor