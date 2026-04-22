# main_60.py
from core.control.core_controller import core_controller
from core.protocol.adapter.legacy_adapter import legacy_adapter


def main():
    print("🚀 启动成功！")
    print("📌 支持指令：/list（查看会话） /new（新建会话） /switch 前缀（切换会话） /exit（退出）")

    # 默认会话
    sessions = legacy_adapter.memory.list_sessions()
    session_id = sessions[0][0] if sessions else legacy_adapter.memory.create_session("默认会话")
    core_controller.set_session(session_id)

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
                core_controller.set_session(session_id)
                print(f"✅ 新会话：{session_id[:8]}")
            elif cmd == "/switch":
                if len(user_input.split()) < 2:
                    print("❌ 请输入会话ID前缀，例如：/switch a1b2")
                    continue
                prefix = user_input.split()[1]
                session_id = legacy_adapter.memory.get_session_by_prefix(prefix)
                if session_id:
                    core_controller.set_session(session_id)
                    print(f"✅ 已切换会话：{session_id[:8]}")
            elif user_input == "exit":
                print("👋 再见！")
                break
            continue

        print("AI: ", end="", flush=True)
        full_reply = ""
        for chunk in core_controller.chat_stream(user_input):
            print(chunk, end="", flush=True)
            full_reply += chunk

        # 保存AI回复到短期记忆
        if legacy_adapter.memory:
            legacy_adapter.memory.save_ai_message(core_controller.session_id, full_reply)
        print()


if __name__ == "__main__":
    main()