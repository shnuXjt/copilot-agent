# import os
# import time
#
# from langchain_chroma import Chroma
# from langchain_openai import OpenAIEmbeddings
# from pydantic import BaseModel
# from typing import Optional, List
# from config_loader import config_loader
# from src.config import MODEL_API_KEY, MODEL_BASE_URL, EMBEDDING_MODEL_NAME
#
# # MCP 协议规范： 资源URI（唯一标识，供模型定位资源，不可重复）
# MCP_RESOURCE_URI = "vector_memory://long_term_context"
#
# # MCP 协议规范： 资源查询参数
# class ResourceQueryParams(BaseModel):
#     session_id: str # 会话ID
#     query: str # 检索关键字
#     top_k: Optional[int] = 3 # 检索数量（协议可选参数)
#
# # MCP协议规范： 资源响应格式
# class ResourceResponse(BaseModel):
#     code: int = 200
#     message: str = "success"
#     resource_uri: str = MCP_RESOURCE_URI
#     data: List[str] = [] # 资源数据（长期记忆内容）
#     context_id: str # 上下文ID
#
# # 从配置文件中读取参数
# vector_config = config_loader.model_config["memory"]["long_memory"]["vector_db"]
#
#
#
# class VectorMemory:
#     """向量长期记忆： 完全遵循配置文件，支持配置化调整"""
#     def __init__(self):
#
#         # 用Langchain包装通义千问Embedding，适配配置
#         self.embedding = OpenAIEmbeddings(
#             api_key=MODEL_API_KEY,
#             base_url=MODEL_BASE_URL,
#             model=EMBEDDING_MODEL_NAME
#         )
#         # 向量库实例（配置化路径）
#         self.vector_store = Chroma(
#             collection_name="agent_memory",
#             embedding_function=self.embedding,
#             persist_directory=vector_config["persis_dir"]
#         )
#         self.top_k = vector_config["top_k"]
#         self.timeout = vector_config["timeout"]
#         # 配置化tiktoken本地缓存，避免远程下载卡死
#         self._set_tiktoken_cache()
#
#     def _set_tiktoken_cache(self):
#         """从配置读取tiktoken缓存目录，设置环境变量"""
#         cache_dir = vector_config["tiktoken_cache"]
#         os.environ["TIKTOKEN_CACHE_DIR"] = cache_dir
#         os.makedirs(cache_dir, exist_ok=True)
#
#     # MCP协议标准化资源查询接口（供Client调用，统一接口名get_resource)
#     def get_resource(self, params: dict) -> dict:
#         try:
#             validated_params = ResourceQueryParams(**params)
#             # 检索当前会话资源（长期记忆），复用原有检索逻辑
#             docs = self.vector_store.similarity_search(
#                 validated_params.query,
#                 k = validated_params.top_k,
#                 fileter={"session": validated_params.session_id}
#             )
#
#             data = [d.page_content for d in docs] if docs else []
#             # 按MCP协议格式返回资源数据
#             return ResourceResponse(
#                 data=data,
#                 context_id=f"vector_memory_{validated_params.session_id}"
#             ).model_dump()
#         except Exception as e:
#             return ResourceResponse(
#                 code=500,
#                 message=f"资源查询失败： {str(e)}",
#                 context_id= f"vector_memory_error_{params.get('session_id', 'unknown')}"
#             ).model_dump()
#
#     # MCP 协议标准化资源更新接口（同步上下文，统一接口名update_resource)
#     def update_resource(self, params: dict) -> dict:
#         """新增/更新资源（长期记忆），准许MCP协议规范"""
#         try:
#             session_id = params.get("session_id")
#             text = params.get("text")
#             if not session_id or not text:
#                 return ResourceResponse(
#                     code=400,
#                     message="参数错误：session_id和text为必填项",
#                     context_id=f"vector_memory_update_error_{session_id}"
#                 ).model_dump()
#             # 新增记忆
#             self.vector_store.add_texts(
#                 texts=[text],
#                 metadatas=[{"session": session_id}]
#             )
#             self.vector_store.persist()
#             return ResourceResponse(
#                 message="资源更新成功",
#                 context_id=f"vector_memory_update_{session_id}"
#             ).model_dump()
#         except Exception as e:
#             return ResourceResponse(
#                 code=500,
#                 message=f"资源更新失败：{str(e)}",
#                 context_id=f"vector_memory_update_error_{params.get('session_id', 'unknown')}"
#             ).model_dump()
#
#
# # 注册到MCP资源清单（供Client发现，统一管理）
# MCP_RESOURCES = [{"uri": MCP_RESOURCE_URI, "handler": VectorMemory()}]
