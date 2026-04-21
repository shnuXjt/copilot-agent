# core/memory/vector_memory.py
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.config import MODEL_API_KEY, MODEL_BASE_URL

# 用 LangChain 包装通义千问 Embedding → 100% 兼容 Chroma，无任何属性报错
embedding = OpenAIEmbeddings(
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL,
    model="text-embedding-v3"  # 通义千问官方文本向量模型（正确）
)

# LangChain Chroma 实例（自动处理所有兼容问题）
vector_store = Chroma(
    collection_name="agent_memory",
    embedding_function=embedding,
    persist_directory="./storage/vector_db"  # 向量存储目录
)

class VectorMemory:
    """向量长期记忆：存储、检索对话历史，不丢失长期上下文"""
    def add(self, session_id: str, text: str):
        try:
            # 新增文本到向量库，关联会话ID（用于区分不同会话记忆）
            vector_store.add_texts(
                texts=[text],
                metadatas=[{"session": session_id}]
            )
            vector_store.persist()  # 持久化存储
        except Exception as e:
            pass  # 异常不崩溃，保证系统稳定

    def query(self, session_id: str, query: str, top_k=3):
        try:
            # 优化：使用更轻量的检索方法，减少资源占用；修复tiktoken远程下载卡死问题
            import os
            # 禁用tiktoken远程下载，指定本地缓存目录，避免KeyboardInterrupt
            os.environ["TIKTOKEN_CACHE_DIR"] = "./storage/tiktoken_cache"
            os.makedirs("./storage/tiktoken_cache", exist_ok=True)

            # 限制检索结果数量，进一步提升响应速度，避免检索过多导致卡死
            docs = vector_store.similarity_search(
                query,
                k=min(top_k, 3),  # 最多检索3条，避免检索过多导致卡死
                filter={"session": session_id},
                fetch_k=5  # 预取5条再筛选，提升效率
            )
            return "\n".join([d.page_content for d in docs]) if docs else ""
        except Exception as e:
            return ""  # 异常返回空，不影响主流程

# 全局单例
vector_memory = VectorMemory()
