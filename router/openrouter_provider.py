from openai_provider import OpenAIProvider
import requests
from typing import Optional, Generator
import json

class OpenRouterProvider(OpenAIProvider):
    def __init__(self, api_key, model):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1"
        )

    def chat(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 4096, history: list = None) -> str:
        messages = history.copy() if history else []
        
        if system:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": system})
                
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Alexx-coder/Cortex",
            "X-Title": "Cortex",
        }

        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
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
        except requests.exceptions.HTTPError as e:
            err_details = e.response.text[:200]
            return f"[OpenRouter HTTP Error] {err_details}"
        except Exception as e:
            return f"[OpenRouter Error] {str(e)}"

    def chat_stream(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 4096, history: list = None) -> Generator[str, None, None]:
        messages = history.copy() if history else []
        if system:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # ОБЯЗАТЕЛЬНО эти заголовки, иначе 403 на бесплатных моделях
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Alexx-coder/Cortex",
            "X-Title": "Cortex",
        }

        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
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

            if r.status_code == 403:
                try:
                    error_data = r.json()
                    reason = error_data.get("error", {}).get("message", "Unknown reason")
                except Exception:
                    reason = r.text[:200] # Если это не JSON, берем просто текст
                
                yield f"\n[OpenRouter 403 Forbidden] Reason: {reason}"
                return

            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if "choices" in data and len(data["choices"]) > 0:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
                        
        except requests.exceptions.HTTPError as e:
            yield f"\n[OpenRouter Stream Error] {e.response.text[:200]}"
        except Exception as e:
            yield f"\n[OpenRouter Stream Error] {str(e)}"