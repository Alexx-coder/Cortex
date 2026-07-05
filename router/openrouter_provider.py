from openai_provider import OpenAIProvider
import requests
from typing import Optional

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
            
            response_json = r.json()

            if "error" in response_json:
                err_msg = response_json["error"].get("message", "Unknown OpenRouter error")
                return f"[OpenRouter Error] {err_msg}"

            if "choices" not in response_json or not response_json["choices"]:
                return f"[OpenRouter Error] Unexpected response format: {str(response_json)[:200]}"

            return response_json["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            err_details = e.response.text[:200] if e.response is not None else str(e)
            return f"[OpenRouter HTTP Error] {err_details}"
        except Exception as e:
            return f"[OpenRouter Error] {str(e)}"