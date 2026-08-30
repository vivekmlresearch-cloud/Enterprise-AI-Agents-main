from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from ..config import settings

logger = logging.getLogger(__name__)

class BaseLLMClient:
    def invoke_json(self, system: str, user: str) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    def invoke_json(self, system: str, user: str) -> dict[str, Any]:
        return {
            "summary": "Fallback macro summary produced without a live LLM.",
            "factors": ["LLM provider not configured; using deterministic fallback."],
            "risks": ["Narrative quality limited in mock mode."],
            "macro_score": 50,
            "verdict_reasoning": "Fallback judge mode used.",
            "reasons": ["Deterministic scores dominated the decision."],
        }


class OpenAICompatibleLLMClient(BaseLLMClient):
    def __init__(self, model_name: str):
        from langchain_openai import ChatOpenAI

        self.model = ChatOpenAI(
            model=model_name,
            base_url=settings.openai_compatible_base_url,
            api_key=settings.openai_compatible_api_key,
            temperature=0,
        )

    def invoke_json(self, system: str, user: str) -> dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", user),
        ])
        chain = prompt | self.model
        result = chain.invoke({})
        content = result.content if hasattr(result, "content") else str(result)
        return _extract_json(content)


class VertexGemmaLLMClient(BaseLLMClient):
    def __init__(self, model_name: str):
        from langchain_google_vertexai import GemmaChatVertexAIModelGarden

        if not settings.vertex_gemma_endpoint_id:
            raise ValueError("VERTEX_GEMMA_ENDPOINT_ID must be set for vertex_gemma provider.")
        self.model = GemmaChatVertexAIModelGarden(
            endpoint_id=settings.vertex_gemma_endpoint_id,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )
        self.model_name = model_name

    def invoke_json(self, system: str, user: str) -> dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", user),
        ])
        chain = prompt | self.model
        result = chain.invoke({})
        content = result.content if hasattr(result, "content") else str(result)
        return _extract_json(content)

def build_llm_client(model_name: str) -> BaseLLMClient:
    provider = settings.llm_provider.lower()
    if provider == "openai_compatible":
        return OpenAICompatibleLLMClient(model_name)
    if provider == "vertex_gemma":
        return VertexGemmaLLMClient(model_name)
    return MockLLMClient()


def _extract_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception:
        logger.warning("Could not parse JSON from LLM response; returning raw text wrapper.")
        return {"summary": text, "raw": text}
