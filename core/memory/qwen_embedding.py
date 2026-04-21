import requests
from src.config import MODEL_API_KEY, MODEL_BASE_URL, EMBEDDING_MODEL_NAME


class QwenEmbeddingFunction:
    def __init__(self):
        self.api_key = MODEL_API_KEY
        self.api_base = MODEL_BASE_URL
        self.model = EMBEDDING_MODEL_NAME

    def name(self):
        return "qwen_embedding"

        # 必须叫 input（Chroma 强制）

    def __call__(self, input):
        return self._embed(input)

        # 供 query 使用（必须实现！）

    def embed_query(self, input):
        return self._embed(input)[0]

        # 供 documents 使用

    def embed_documents(self, input):
        return self._embed(input)

        # 真正调用通义千问 embedding

    def _embed(self, input):
        if isinstance(input, str):
            texts = [input]
        else:
            texts = input

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "input": texts
        }

        resp = requests.post(
            url=f"{self.api_base}/embeddings",
            json=data,
            headers=headers,
            timeout=15
        )
        resp.raise_for_status()
        return [item["embedding"] for item in resp.json()["data"]]