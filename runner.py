import json
import os
import sys
import time
import getpass
from art import text2art as t2

sys.path.append(os.path.join(os.path.dirname(__file__), 'router'))

from commands import Commands
from router.gemini_provider import GeminiProvider
from router.ollama_provider import Ollama
from router.openai_provider import OpenAIProvider
from router.openrouter_provider import OpenRouterProvider

from database import Database

PICTURE_MAIN = t2("CORTEX")

CONFIG_DIR = os.path.expanduser("~/.cortex")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "gemini": {
        "api_key": "",
        "model": "gemini-2.5-flash"
    },
    "openai": {
        "api_key": "",
        "model": "gpt-3.5-turbo"
    },
    "openrouter": {
        "api_key": "",
        "model": "meta-llama/llama-3-8b-instruct:free"
    },
    "ollama": {
        "model": "glm-4.7-flash:latest",
        "base_url": "http://localhost:11434"
    },
    "agents": {
        "code": "ollama",
        "ideas": "ollama",
        "other": "ollama"
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(f"[SYSTEM] Config file created at: {CONFIG_PATH}")
        print("[SYSTEM] Please open it, add your API keys, assign agents, and restart Cortex.")
        sys.exit(0)
    
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

class Runner:
    def __init__(self):
        self.name = "CORTEX"
        self.version = 'v0.1.2'
        
        print("--- DATABASE AUTHENTICATION ---")
        pwd = getpass.getpass("Enter master password: ")
        self.db = Database(pwd)
        print("Database loaded successfully.\n")
        
        self.config = load_config()

        
   
        for agent_name, agent_value in self.config["agents"].items():
            if isinstance(agent_value, str):
                self.config["agents"][agent_name] = {
                    "provider": agent_value,
                    "temperature": 0.7,
                    "max_tokens": 4096
                }

        
        self.providers = {
            "ollama": Ollama(
                model=self.config["ollama"]["model"], 
                url=self.config["ollama"]["base_url"]
            ),
            "gemini": GeminiProvider(
                api_key=self.config["gemini"]["api_key"], 
                model=self.config["gemini"]["model"]
            ) if self.config["gemini"]["api_key"] else None,
            
            "openai": OpenAIProvider(
                api_key=self.config["openai"]["api_key"], 
                model=self.config["openai"]["model"]
            ) if self.config["openai"]["api_key"] else None,
            
            "openrouter": OpenRouterProvider(
                api_key=self.config["openrouter"]["api_key"], 
                model=self.config["openrouter"]["model"]
            ) if self.config["openrouter"]["api_key"] else None
        }

        self.commands_handler = Commands(
            providers=self.providers,
            agent_map=self.config["agents"],
            config_path=CONFIG_PATH,
            version=self.version,
            db=self.db  
        )

    def main(self):
        print(PICTURE_MAIN)
        print(f"Version: {self.version} | Type /help for commands\n")
        
        while True:
            try:
                user_input = input("Cortex > ").strip()
                if not user_input:
                    continue
                
                if user_input.startswith("/message:"):
                    cmd_text = user_input.replace("/message:", "").strip()
                    self.commands_handler.message(cmd_text)
                elif user_input.startswith("/new "):
                    chat_name = user_input.replace("/new ", "").strip()
                    self.commands_handler.new_chat(chat_name)
                elif user_input == "/chats":
                    self.commands_handler.list_chats()
                elif user_input.startswith("/switch "):
                    chat_id = user_input.replace("/switch ", "").strip()
                    self.commands_handler.switch_chat(chat_id)
                elif user_input == "/stop":
                    print("Stopping Cortex...")
                    time.sleep(1)
                    sys.exit(0)
                elif user_input == "/help":
                    self.commands_handler.help()
                elif user_input == "/about":
                    self.commands_handler.about()
                elif user_input == "/version":
                    self.commands_handler.version()
                elif user_input == "/settings":
                    self.commands_handler.settings()
                elif user_input.startswith("/switch "):
                    chat_id = user_input.replace("/switch ", "").strip()
                    self.commands_handler.switch_chat(chat_id)
                elif user_input == "/clear":
                    self.commands_handler.clear_chat()
                elif user_input == "/export":
                    self.commands_handler.export_chat()
                else:
                    print(f"[ERROR] Command '{user_input}' not found. Type /help")
                    
            except KeyboardInterrupt:
                print("\n[SYSTEM] Cortex stopped by user.")
                sys.exit(0)
            except Exception as err:
                print(f"[ERROR] An error occurred: {err}")

if __name__ == "__main__":
    try:
      app = Runner()
      app.main()
    except Exception as err:
        print(f'[ERROR] An error has occurred: {err}')
    except KeyboardInterrupt:
        print("[SYSTEM] Cortex stopped by user.")