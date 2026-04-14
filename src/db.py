# SQLite 会话记忆数据库（内置，无需安装）
from datetime import datetime
import sqlite3
import uuid
import time
from src.logger import logger

# 数据库文件（自动生成）
DB_PATH = "agent_memory.db"

def init_db():
    """初始化数据库： 创建，会话表 + 消息表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 会话表：新增session_name, update_time
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                    (session_id TEXT PRIMARY KEY,
                     session_name TEXT DEFAULT "未命名会话", 
                     create_time TEXT,
                     update_time TEXT)''')

    # 消息表 role:  user/ai/tool
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     role TEXT, 
                     content TEXT,
                     create_time TEXT)''')

    conn.commit()
    conn.close()
    logger.info("✅ 记忆数据库初始化完成")

# 基础操作
def create_session(session_name: str = "未命名会话"):
    """创建会话，自动生成唯一ID"""
    session_id = str(uuid.uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",
              (session_id, session_name, now, now))
    conn.commit()
    conn.close()
    return session_id
def update_session_name(session_id: str, session_name: str):
    conn = sqlite3.connect(DB_PATH)
    c=conn.cursor()
    c.execute("UPDATE sessions SET session_name=?, update_time=? WHERE session_id=?",
              (session_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session_id))
    conn.commit()
    conn.close()

def list_all_sessions() -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT session_id, session_name, create_time FROM sessions ORDER BY update_time DESC")
    sessions = c.fetchall()
    conn.close()
    return sessions

def del_session(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE session_id=?",(session_id,))
    c.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()

def get_session_name(session_id: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT session_name FROM sessions WHERE session_id=?", (session_id,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else "未知会话"

def add_message(session_id: str, role:str, content: str):
    """添加一条对话记录"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, create_time) VALUES (?, ?, ?, ?)",
              (session_id, role, content, time.time()))
    c.execute("UPDATE sessions SET update_time=? WHERE session_id=?", (now, session_id,))
    conn.commit()
    conn.close()

def get_session_history(session_id: str, limit: int = 10):
    """获取最近N条对话历史"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT role, content FROM messages 
    WHERE session_id=? 
    ORDER BY create_time ASC
    LIMIT ?''', (session_id, limit))

    rows = c.fetchall()
    conn.close()
    return rows

# 初始化
init_db()