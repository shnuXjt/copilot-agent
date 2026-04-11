from src.agent import create_search_agent, run_agent
from src.excel_agent import create_excel_agent, run_excel_agent
from src.manager_agent import run_manager_agent
from src.memory import agent_memory
from src.super_agent import create_super_agent, run_super_agent

# ======= 运行 agent ======

if __name__ == "__main__":
    print("=" * 50)
    print("🤝 Manager + Worker 多智能体协作系统")
    print("支持：任务自动拆解 → 分工执行 → 汇总结果")
    print("=" * 50)

    # 使用默认会话
    current_session = agent_memory.default_session

    # 循环对话
    while True:
        user_input = input("\n请输入复杂任务（exit退出）：")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 再见！")
            break

        # 执行任务
        answer = run_manager_agent(user_input, current_session)

        print("\n" + "=" * 50)
        print("📌 结果：")
        print(answer)

