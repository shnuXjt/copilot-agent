from src.agent import create_search_agent, run_agent
from src.excel_agent import create_excel_agent, run_excel_agent

# ======= 运行 agent ======

if __name__ == "__main__":
    print("=" * 50)
    print("请选择Agent模式：")
    print("1 → 🌐 联网搜索Agent")
    print("2 → 📊 Excel数据分析Agent")
    print("=" * 50)
    choice = input("请输入数字 1/2 并回车")

    # ---- 模式1： 联网搜索 ----
    if choice == '1':
        # 1. 创建agent
        agent = create_search_agent()
        # 测试问题
        question = input("请输入你的问题")
        print(f"用户问题： {question}\n")

        # 执行agent
        answer = run_agent(agent, question)
    elif choice == '2':
        agent = create_excel_agent()
        question = input("\n请输入数据分析问题（包含文件路径，如：data/test.xlsx）：")
        answer = run_excel_agent(agent, question)
    else:
        print("输入错误！")
        exit()

        # 输出结果
    print("\n" + "=" * 50)
    print("📌 最终结果：")
    print(answer)