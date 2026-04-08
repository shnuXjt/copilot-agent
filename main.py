from src.agent import create_search_agent, run_agent
from src.excel_agent import create_excel_agent, run_excel_agent
from src.super_agent import create_super_agent, run_super_agent

# ======= 运行 agent ======

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 全能超级Agent 已启动")
    print("支持：联网搜索 | Excel分析 | 计算器 | Python代码执行")
    print("=" * 50)

    super_agent = create_super_agent()
    # 循环对话
    while True:
        user_input = input("\n请输入你的任务（输入exit退出）：")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 再见！")
            break

        # 执行任务
        answer = run_super_agent(super_agent, user_input)

        print("\n" + "=" * 50)
        print("📌 结果：")
        print(answer)

