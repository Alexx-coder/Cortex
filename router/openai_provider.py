import requests


class OpenAIProvider:
    def __init__(self, api_key, model, base_url="https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def chat(
        self,
        prompt,
        system=None,
        temperature=0.7,
        max_tokens=4096,
    ):
        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

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
