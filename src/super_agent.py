from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE
from src.tools import get_super_agent_tools
from src.logger import logger


def create_super_agent():
    """创建全能超级Agent: 支持搜索 + Excel + 计算器 + 代码执行"""
    # LLM模型
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=MODEL_API_KEY,
        base_url=MODEL_BASE_URL,
        temperature=0
    )

    # 工具
    tools = get_super_agent_tools()

    # 提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是一个**全能超级智能体（Super Agent)**, 拥有以下能力：
        1. 联网搜索: 获取实时/最新消息
        2. 计算器： 精确数学计算
        3. Excel分析： 读取并分析Excel文件
        4. Python单吗执行： 编写并运行代码处理复杂逻辑
        
        规则：
        - 先判断任务类型，自主选择合适的工具
        - 需要最新信息 → 用搜索
        - 需要纯计算 → 用计算器
        - 需要处理表格 → 用Excel
        - 需要复杂逻辑/批量计算 → 用Python代码
        - 多部任务可以连续调用多个工具
        - 回答简洁、准确、不编造数据
        - 分析数据时先读取Excel，再给出结论
        """),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # 4.创建agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=VERBOSE,
        handle_parsing_errors=True,
        max_iterations=10, # 允许多步思考
        max_execution_time=30
    )

    logger.info("✅ 全能超级Agent 启动成功")
    return agent_executor

def run_super_agent(agent_executor, query: str) -> str:
    try:
        logger.info(f"用户任务： {query}")
        result = agent_executor.invoke({"input": query})
        return result["output"]
    except Exception as e:
        logger.error(f"执行失败： {str(e)}")
        return f"任务执行出错： {str(e)}"