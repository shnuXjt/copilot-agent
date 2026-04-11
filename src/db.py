# SQLite 会话记忆数据库（内置，无需安装）
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

    # 会话表
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                    (session_id TEXT PRIMARY KEY, create_time REAL)''')

    # 消息表 role:  user/ai/tool
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     role TEXT, 
                     content TEXT,
                     create_time REAL)''')

    conn.commit()
    conn.close()
    logger.info("✅ 记忆数据库初始化完成")

# 基础操作
def create_session(session_id: str = None):
    """创建会话，自动生成唯一ID"""
    if not session_id:
        session_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO sessions VALUES (?, ?)", (session_id, time.time()))
    conn.commit()
    conn.close()
    return session_id

def add_message(session_id: str, role:str, content: str):
    """添加一条对话记录"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, create_time) VALUES (?, ?, ?, ?)",
              (session_id, role, content, time.time()))
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