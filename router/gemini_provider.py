import requests
from typing import Optional

class GeminiProvider:
    def __init__(self, api_key, model="gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    def chat(self, prompt: str, system: Optional[str] = None, history: list = None) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent?key={self.api_key}"
        )

        contents = []
        
        # Переводим стандартную историю в формат Gemini
        if history:
            for msg in history:
                role = "user"
                if msg["role"] == "assistant":
                    role = "model" # Gemini требует роль "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

        # Добавляем текущее сообщение пользователя
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {"contents": contents}

        if system:
            payload["system_instruction"] = {
                "parts": [{"text": system}]
            }

        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()

        return r.json()["candidates"][0]["content"]["parts"][0]["text"]