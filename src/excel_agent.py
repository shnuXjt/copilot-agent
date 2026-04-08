from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE
from src.tools import get_excel_tools
from src.logger import logger


def create_excel_agent():
    '''创建excel数据分析agent'''
    # 1. 初始化llm
    llm = ChatOpenAI(
        model=MODEL_NAME,
        api_key=MODEL_API_KEY,
        base_url=MODEL_BASE_URL,
        temperature=0
    )

    # 2. 加载Excel专用tools
    tools = get_excel_tools()

    # 3. 专业提示词
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是专业的Excel数据分析师，严格按步骤执行：
1. 先用 excel_reader 读取Excel文件
2. 查看数据结构、列名、数据类型
3. 使用 Python + pandas 完成数据分析
4. 用自然语言给出清晰、准确的结论
5. 禁止编造数据，所有结果基于真实Excel数据
        """),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # 4. 创建agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=VERBOSE,
        handle_parsing_errors=True,
        max_iterations=5 # 限制分析部署，避免死循环
    )

    logger.info("✅ Excel数据分析Agent创建成功")
    return agent_executor

def run_excel_agent(agent_excutor, question: str) -> str:
    '''运行Excel Agent'''
    try:
        logger.info(f"📊 数据分析请求：{question}")
        result = agent_excutor.invoke({"input": question})
        return result["output"]
    except Exception as e:
        logger.error(f"❌ 分析失败：{str(e)}")
        return f"分析出错：{str(e)}"