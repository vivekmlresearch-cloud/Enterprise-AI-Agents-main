from __future__ import annotations

from typing import Sequence

import httpx

from app.core.config import get_settings


class VLLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.vllm_base_url.rstrip('/')
        self.api_key = settings.vllm_api_key
        self.model = settings.vllm_model

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'temperature': 0.2,
            'max_tokens': 700,
        }
        headers = {'Authorization': f'Bearer {self.api_key}'}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f'{self.base_url}/chat/completions', json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
