import json
import os
import sys
import time
import getpass
import hashlib
import readline
from art import text2art as t2

sys.path.append(os.path.join(os.path.dirname(__file__), 'router'))

from commands import Commands
from router.gemini_provider import GeminiProvider
from router.ollama_provider import Ollama
from router.openai_provider import OpenAIProvider
from router.openrouter_provider import OpenRouterProvider

from database import Database
from logger import logger

PICTURE_MAIN = t2("CORTEX")

CONFIG_DIR = os.path.expanduser("~/.cortex")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "providers": {
        "ollama": {
            "model": "glm-4.7-flash:latest",
            "base_url": "http://localhost:11434"
        },
        "gemini": {
            "api_key": "",
            "model": "gemini-3.1"
        },
        "openai": {
            "api_key": "",
            "model": "gpt-5.5"
        },
        "openrouter": {
            "api_key": "",
            "model": "meta-llama/llama-3-8b-instruct:free"
        }
    },
    "agents": {
        "code": {
            "provider": "ollama",
            "temperature": 0.2,
            "max_tokens": 4096,
            "system_prompt": "You are an expert programmer. Write clean, optimized code with comments. Answer only to the point."
        },
        "ideas": {
            "provider": "ollama",
            "temperature": 0.9,
            "max_tokens": 2048,
            "system_prompt": "You are a creative idea generator. Help with brainstorming and offer non-standard solutions."
        },
        "other": {
            "provider": "ollama",
            "temperature": 0.7,
            "max_tokens": 4096,
            "system_prompt": "You are a helpful AI assistant. Answer any user questions friendly and in detail."
        }
    },
    "ui": {
        "show_ascii_art": True,
        "show_welcome_message": True
    },
    "security": {
        "max_output_limit": 8192 
    },
    "memory": {
        "remember_last_chat": True
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(f"[SYSTEM] Config file created at: {CONFIG_PATH}")
        logger.info(f"Config file created at {CONFIG_PATH}")
        print("[SYSTEM] Please open it, add your API keys, assign agents, and restart Cortex.")
        sys.exit(0)
    
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

class Runner:
    def __init__(self):
        self.name = "CORTEX"
        self.version = 'v0.2.0'

        TOKEN_PATH = os.path.join(CONFIG_DIR, "auth.token")
        db_key = None

        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "r") as f:
                db_key = bytes.fromhex(f.read().strip())

        else:
            print("--- FIRST TIME SETUP ---")
            pwd = getpass.getpass("Create a master password for your database: ")
            db_key = hashlib.sha256(pwd.encode('utf-8')).digest()
            
            # Сохраняем токен для будущих запусков
            with open(TOKEN_PATH, "w") as f:
                f.write(db_key.hex())
            print("[SYSTEM] Authentication token saved. You won't need to enter the password again.\n")

        self.db = Database(key=db_key) 
        
        self.config = load_config()
        
        if "providers" not in self.config:
            old_providers = {
                "ollama": self.config.pop("ollama", {}),
                "gemini": self.config.pop("gemini", {}),
                "openai": self.config.pop("openai", {}),
                "openrouter": self.config.pop("openrouter", {})
            }
            self.config["providers"] = old_providers

        for agent_name, agent_value in self.config.get("agents", {}).items():
            if isinstance(agent_value, str):
                self.config["agents"][agent_name] = {
                    "provider": agent_value,
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
        
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
                
        prov_config = self.config.get("providers", {})
        
        self.providers = {
            "ollama": Ollama(
                model=prov_config.get("ollama", {}).get("model", "glm-4.7-flash:latest"), 
                url=prov_config.get("ollama", {}).get("base_url", "http://localhost:11434")
            ),
            "gemini": GeminiProvider(
                api_key=prov_config.get("gemini", {}).get("api_key", ""), 
                model=prov_config.get("gemini", {}).get("model", "gemini-3.1")
            ) if prov_config.get("gemini", {}).get("api_key") else None,
            
            "openai": OpenAIProvider(
                api_key=prov_config.get("openai", {}).get("api_key", ""), 
                model=prov_config.get("openai", {}).get("model", "gpt-5.5")
            ) if prov_config.get("openai", {}).get("api_key") else None,
            
            "openrouter": OpenRouterProvider(
                api_key=prov_config.get("openrouter", {}).get("api_key", ""), 
                model=prov_config.get("openrouter", {}).get("model", "meta-llama/llama-3-8b-instruct:free")
            ) if prov_config.get("openrouter", {}).get("api_key") else None
        }

        self.commands_handler = Commands(
            providers=self.providers,
            agent_map=self.config["agents"],
            config_path=CONFIG_PATH,
            version=self.version,
            db=self.db
        )

    def main(self):
        ui_settings = self.config.get("ui", {})
        
        if ui_settings.get("show_ascii_art", True):
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
                elif user_input == "/clear":
                    self.commands_handler.clear_chat()
                elif user_input == "/export":
                    self.commands_handler.export_chat()
                    
                elif user_input.startswith("/load "):
                    file_path = user_input.replace("/load ", "").strip()
                    self.commands_handler.load_file(file_path)
                    
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
        logger.error(f"An error has ocurred: {err}")
    except KeyboardInterrupt:
        print("[SYSTEM] Cortex stopped by user.")
        logger.info(f'Cortex stopped by user.')