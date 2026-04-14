from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE
from src.tools import tool_registry
from src.logger import logger


def create_search_agent():
    '''创建联网搜搜Agent'''
    # 1.初始化LLM
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=MODEL_API_KEY,
        base_url=MODEL_BASE_URL,
        temperature=0
    )

    # 2. 获取工具
    tools = tool_registry.get_all_tools()

    # 3. 提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是专业的联网搜索助手，必须调用搜索获取最新信息， 准确简洁回答"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # 4. 创建Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent = agent,
        tools = tools,
        verbose=VERBOSE,
        handle_parsing_errors=True
    )

    logger.info("搜索Agent创建成功")
    return agent_executor

def run_agent(agent_executor, question:str) -> str:
    '''执行Agent并返回结果'''
    try:
        logger.info(f"用户提问： {question}")
        result = agent_executor.invoke({"input": question})
        return result["output"]
    except Exception as e:
        logger.error(f"Agent执行失败： {str(e)}")
        return f"执行出错： {str(e)}"