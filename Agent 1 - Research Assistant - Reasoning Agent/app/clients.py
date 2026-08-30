from __future__ import annotations

import time
from typing import Any, Iterable

import httpx
import tiktoken
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

print("DEBUG: CLIENTS.PY LOADED FROM THIS FILE")

_tokenizer = tiktoken.get_encoding("cl100k_base")


def _truncate_tokens(text: str, max_tokens: int = 500) -> str:
    tokens = _tokenizer.encode(text)
    return _tokenizer.decode(tokens[:max_tokens])


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip() if api_key else ""
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=payload,
            )

            if response.status_code >= 400:
                raise httpx.HTTPStatusError(
                    f"HTTP {response.status_code} for {response.request.url}\nResponse body: {response.text}",
                    request=response.request,
                    response=response,
                )

            return response.json()


class LLMClient(OpenAICompatibleClient):
    def generate(self, question: str, contexts: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
        started = time.perf_counter()
        prompt = self._build_prompt(question, contexts)
        
        print("LLM_BASE_URL:", self.base_url)


        payload = {
                "model": settings.llm_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant. Answer only from provided context. Cite sources.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.1,
                "max_tokens": 1024,
                "stream": False,
            }

        data = self.post("/chat/completions", payload)

        latency_ms = (time.perf_counter() - started) * 1000.0

        choices = data.get("choices", [])
        answer = choices[0]["message"]["content"] if choices else ""
        usage = data.get("usage", {})

        return answer, {"llm_latency_ms": latency_ms, "usage": usage}

    @staticmethod
    def _build_prompt(question: str, contexts: list[dict[str, Any]]) -> str:
        context_lines = []
        for idx, ctx in enumerate(contexts, start=1):
            context_lines.append(
                f"[{idx}] Title: {ctx.get('title', '')}\n"
                f"Published: {ctx.get('published')}\n"
                f"URL: {ctx.get('url', '')}\n"
                f"Snippet: {ctx.get('snippet', '')}"
            )

        context_block = "\n\n".join(context_lines)

        return (
            "You are a research assistant.\n"
            "Answer only from the provided paper context.\n"
            "Always cite paper titles inline in square brackets.\n\n"
            f"Question: {question}\n\n"
            f"Contexts:\n{context_block}"
        )


class EmbeddingClient(OpenAICompatibleClient):
    def embed_texts(self, texts: Iterable[str], input_type: str) -> list[list[float]]:
        clean_texts = [
            _truncate_tokens(str(text).strip(), max_tokens=500)
            for text in texts
            if text and str(text).strip()
        ]

        if not clean_texts:
            return []

        payload = {
            "input": clean_texts,
            "model": settings.embedding_model,
            "input_type": input_type,
        }

        data = self.post("/embeddings", payload)
        return [row["embedding"] for row in data["data"]]

    def embed_query(self, text: str) -> list[float]:
        vectors = self.embed_texts([text], input_type="query")
        return vectors[0] if vectors else []

    def embed_passages(self, texts: Iterable[str]) -> list[list[float]]:
        return self.embed_texts(texts, input_type="passage")


class RerankClient(OpenAICompatibleClient):
    def rerank(self, query: str, documents: list[str], top_n: int) -> list[dict[str, Any]]:
        clean_documents = [str(doc).strip()[:2000] for doc in documents if str(doc).strip()]

        if not clean_documents:
            return []

        payload = {
            "model": settings.rerank_model,
            "query": query,
            "documents": clean_documents,
            "top_n": top_n,
        }

        try:
            data = self.post("/rerank", payload)
            return data.get("results", [])
        except Exception:
            return [
                {"index": i, "relevance_score": float(len(doc))}
                for i, doc in enumerate(clean_documents[:top_n])
            ]
