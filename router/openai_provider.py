import requests
import json
from typing import Optional

class OpenAIProvider:
    def __init__(self, api_key, model, base_url="https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        history: list = None
    ) -> str:
        # Берем историю
        messages = history.copy() if history else []

        # Добавляем системный промпт
        if system:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": system})

        # Добавляем запрос
        messages.append({"role": "user", "content": prompt})

        r = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=120,
        )

        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def chat_stream(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 4096, history: list = None):
        messages = history.copy() if history else []
        if system:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        r = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            },
            stream=True,
            timeout=120,
        )
        r.raise_for_status()

        for line in r.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "choices" in data and len(data["choices"]) > 0:
                delta = data["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]