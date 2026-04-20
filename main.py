from adapter import legacy_adapter
from src.agent import create_search_agent, run_agent
from src.db import get_session_name, list_all_sessions, create_session, del_session, update_session_name
from src.excel_agent import create_excel_agent, run_excel_agent
from src.manager_agent import run_manager_agent, chat_with_agent, chat_with_agent_stream
from src.memory import agent_memory
import os
from core.brain.core_brain import core_brain

def print_session_status():
    '''打印当前会话状态'''
    sid = agent_memory.current_session_id
    name = get_session_name(sid)
    print(f"\n📌 当前会话：[{sid[:8]}] {name}")

def process_command(user_input: str) -> bool:
    """处理会话指令，返回True表示是指令"""
    sid = agent_memory.current_session_id
    cmd = user_input.strip()

    if cmd == "/list":
        print("\n 📋 所有会话列表：")
        sessions = list_all_sessions()
        for i, (s_id, s_name, s_time) in enumerate(sessions):
            print(f"{i+1}. [{s_id[:8]}] {s_name} | 创建时间：{s_time}")
        return True
    elif cmd == "/new":
        new_sid = create_session()
        agent_memory.current_session_id = new_sid
        print(f"✅ 新建会话：[{new_sid[:8]}] 未命名会话")
        return True
    elif cmd.startswith("/swtich "):
        target = cmd.split()[1]
        sessions = list_all_sessions()
        for s_id, _, _ in sessions:
            if s_id.startswith(target):
                agent_memory.current_session_id = s_id
                print(f"✅ 切换到：[{s_id[:8]}] {s_name}")
                return True
        print("❌ 会话不存在")
        return True
    elif cmd.startswith("/del "):
        target = cmd.split()[1]
        sessions = list_all_sessions()
        for s_id, _, _ in sessions:
            if s_id.startswith(target):
                del_session(s_id)
                print(f"🗑️ 已删除会话：[{s_id[:8]}]")
                return True
        print("❌ 会话不存在")
        return True
    elif cmd.startswith("/rename "):
        new_name = cmd.replace("/rename ", "")
        update_session_name(sid, new_name)
        print(f"✅ 会话已重命名为：{new_name}")
        return True
    elif cmd == "/clear":
        os.system("cls" if os.name == "nt" else "clear")
        return True

    return False

# ======= 运行 agent ======

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print("🌊 智能多会话 Agent")
    print("指令：/list /new /switch id /del id /rename 名称 /clear")
    print("=" * 60)

    sessions = legacy_adapter.memory.list_sessions()
    session_id = sessions[0][0] if sessions else legacy_adapter.memory.create_session("默认会话")
    core_brain.set_session(session_id)


    # print_session_status()

    # 循环对话
    while True:
        user_input = input("\n你：")
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("👋 再见！")
            break

        # 执行任务
        # answer = chat_with_agent
        # print("\n" + "=" * 50)
        # print("📌 结果：")
        # print(answer)

        # 处理绘话指令
        if process_command(user_input):
            continue

        # 流式输出
        sid = agent_memory.current_session_id
        print("AI:", end="", flush=True)
        full_ans = ""
        try:
            for chunk in chat_with_agent_stream(user_input, sid):
                print(chunk, end="", flush=True)
                full_ans += chunk
        except Exception as e:
            full_ans = f"异常： {str(e)}"
            print(full_ans)
        print()
        # 保存完整答案
        agent_memory.save_ai_message(sid, full_ans)


