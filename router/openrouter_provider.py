from openai_provider import OpenAIProvider
import requests

class OpenRouterProvider(OpenAIProvider):
    def __init__(self, api_key, model):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1"
        )

    def chat(self, prompt, system=None, temperature=0.7, max_tokens=4096):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Alexx-coder/Cortex",
            "X-Title": "Cortex",
        }

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