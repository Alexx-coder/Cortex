import json
from typing import Generator, Optional
import requests

class Ollama:
    def __init__(self, model="glm4.7-flash", url="http://localhost:11434"):
        self.url = url
        self.model = model

    def is_alive(self):
        try:
            return requests.get(f"{self.url}/api/tags", timeout=5).ok
        except requests.RequestException:
            return False

    def list_models(self):
        try:
            r = requests.get(f"{self.url}/api/tags", timeout=10)
            r.raise_for_status()
            return [m["name"] for m in r.json()["models"]]
        except requests.RequestException:
            return []

    def chat(self, prompt: str, system: Optional[str] = None) -> str:
        if not self.model:
            return "[ERROR] No Ollama model selected in config.json."

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            r = requests.post(
                f"{self.url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=300,
            )
            r.raise_for_status()
            return r.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            return "[ERROR] Ollama is not running. Please start Ollama locally."
        except Exception as e:
            return f"[ERROR] Ollama request failed: {e}"

    def chat_stream(self, prompt: str, system: Optional[str] = None) -> Generator[str, None, None]:
        if not self.model:
            yield "[ERROR] No Ollama model selected."
            return

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            r = requests.post(
                f"{self.url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True},
                stream=True,
                
            )
            r.raise_for_status()

            for line in r.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if "message" in data:
                    yield data["message"]["content"]
                if data.get("done"):
                    break
        except Exception as e:
            yield f"[ERROR] {e}"