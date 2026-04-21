# main_60.py
from core.brain.core_brain import core_brain
from adapter import legacy_adapter


def main():
    print("🚀 启动成功！")
    print("指令：/list /new /switch /del /rename /clear exit")

    # 默认会话
    sessions = legacy_adapter.memory.list_sessions()
    session_id = sessions[0][0] if sessions else legacy_adapter.memory.create_session("默认会话")
    core_brain.set_session(session_id)

    while True:
        user_input = input(f"\n你[{session_id[:8]}]: ").strip()
        if not user_input: continue

        # 会话指令（完全复用旧逻辑）
        if user_input.startswith("/"):
            cmd = user_input.split()[0]
            if cmd == "/list":
                for sid, name in legacy_adapter.memory.list_sessions():
                    print(f"- {sid[:8]} | {name}")
            elif cmd == "/new":
                session_id = legacy_adapter.memory.create_session("新会话")
                core_brain.set_session(session_id)
                print(f"✅ 新会话：{session_id[:8]}")
            elif cmd == "/switch":
                prefix = user_input.split()[1]
                session_id = legacy_adapter.memory.get_session_by_prefix(prefix)
                core_brain.set_session(session_id)
                print(f"✅ 切换会话：{session_id[:8]}")
            elif user_input == "exit":
                print("👋 再见！")
                break
            continue

        print("AI: ", end="", flush=True)
        full_reply = ""
        for chunk in core_brain.chat(user_input):
            print(chunk, end="", flush=True)
            full_reply += chunk

        legacy_adapter.memory.save_ai_message(session_id, full_reply)


if __name__ == "__main__":
    main()