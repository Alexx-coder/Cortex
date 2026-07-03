import requests


class GeminiProvider:
    def __init__(self, api_key, model="gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    def chat(self, prompt, system=None):
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        if system:
            payload["system_instruction"] = {
                "parts": [
                    {"text": system}
                ]
            }

        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()

        return r.json()["candidates"][0]["content"]["parts"][0]["text"]