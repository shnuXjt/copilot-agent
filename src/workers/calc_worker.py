from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.config import *
from src.tools import calculator

def get_calc_worker():
    llm = ChatOpenAI(model=MODEL_NAME, api_key=MODEL_API_KEY, base_url=MODEL_BASE_URL, temperature=0)
    tools = [calculator]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是计算专员，只做精确数学计算，不编造答案"),
        ("user", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=VERBOSE, handle_parsing_errors=True)