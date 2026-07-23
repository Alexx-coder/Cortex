import time
import os
from yaspin import yaspin
from art import text2art as t2
from logger import logger

class Commands:
    def __init__(self, providers, agent_map, config_path, version, db):
        self.providers = providers
        self.agent_map = agent_map
        self.config_path = config_path
        self.version = version
        self.db = db

        self.prompts = {
            "code": "You are an expert programmer. Write clean, optimized code with comments. Answer only to the point.",
            "ideas": "You are a creative idea generator. Help with brainstorming and offer non-standard solutions.",
            "other": "You are a helpful AI assistant. Answer any user questions friendly and in detail."
        }

    def help(self):
        print("\n--- AVAILABLE COMMANDS ---")
        print("/help             - Show this help message")
        print("/new <name>       - Create a new chat")
        print("/chats            - List all saved chats")
        print("/switch <id>      - Switch to another chat")
        print("/clear            - Clear current chat history (AI forgets context)")
        print("/export           - Export current chat to a Markdown (.md) file")
        print("/load <file_path> - Load a file into AI context")
        print("/message: <agent> <text> - Send message to agent (streaming enabled)")
        print("               Agents: code, ideas, other")
        print("/settings         - Show current configuration")
        print("/about            - Information about Cortex")
        print("/version          - Current version")
        print("/stop             - Stop Cortex")
        print("-------------------------\n")

    def about(self):
        print("\n" + t2("ABOUT CORTEX"))
        print(f"""Cortex is a program with AI agents (includes local, free API keys, and paid API keys) 
designed for different tasks (code, ideas, etc).
To work with Cortex, you need a local AI model (Ollama) or API keys.
License: MIT
GitHub: https://github.com/Alexx-coder/Cortex
Creator: Alexx-coder (https://github.com/Alexx-coder)
Version: {self.version}\n""")
        time.sleep(3)

    def version(self):
        print(f"Cortex Version: {self.version}")

    def settings(self):
        print("\n--- CURRENT SETTINGS ---")
        print(f"Config file location: {self.config_path}")
        print("\nAssigned Agents:")
        for agent, provider_name in self.agent_map.items():
            print(f"  - {agent}: {provider_name}")
        print("\nTo change settings, edit the config.json file and restart Cortex.")
        print("------------------------\n")

    def new_chat(self, name):
        if not name:
            print("[ERROR] Please provide a chat name. Example: /new My Python Project")
            return
        chat_id = self.db.create_chat(name)
        print(f"[SYSTEM] Created new chat '{name}' with ID: {chat_id}")
        logger.info(f"Created new chat '{name}' with ID: {chat_id}")

    def list_chats(self):
        chats = self.db.list_chats()
        if not chats:
            print("[SYSTEM] No chats found. Use /new <name> to create one.")
            logger.info("No chats found")
            return
        print("\n--- YOUR CHATS ---")
        for c in chats:
            print(c)
        print("------------------\n")

    def switch_chat(self, chat_id):
        if self.db.switch_chat(chat_id):
            print(f"[SYSTEM] Switched to chat {chat_id}")
            logger.info(f"Switched to chat {chat_id}")
        else:
            print(f"[ERROR] Chat {chat_id} not found.")
            logger.error(f"Chat {chat_id} not found.")

    def clear_chat(self):
        chat_id = self.db.data.get('active_chat')
        if not chat_id or chat_id not in self.db.data['chats']:
            print("[ERROR] No active chat to clear.")
            logger.info("No active chat to clear.")
            return
        
        self.db.data['chats'][chat_id]['history'] = []
        self.db._save()
        print(f"[SYSTEM] History for chat {chat_id} cleared. AI has forgotten the context.")
        logger.info(f"History for chat {chat_id} clearned.")

    def load_file(self, file_path):
        if not self.db.data.get('active_chat'):
            print("[ERROR] No active chat. Use /new <name> first.")
            return

        if not os.path.exists(file_path):
            print(f"[ERROR] File '{file_path}' not found.")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Добавляем файл в историю как сообщение пользователя
            prompt_text = f"[System: User loaded file '{file_path}']\n```\n{content}\n```"
            self.db.add_message("user", prompt_text)
            print(f"[SYSTEM] File '{file_path}' loaded into context ({len(content)} chars). You can now ask questions about it.")
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")

    def export_chat(self):
        chat_id = self.db.data.get('active_chat')
        if not chat_id or chat_id not in self.db.data['chats']:
            print("[ERROR] No active chat to export.")
            logger.error("No active chat to export")
            return
        
        chat_data = self.db.data['chats'][chat_id]
        if not chat_data['history']:
            print("[ERROR] Current chat is empty. Nothing to export.")
            logger.error("Current chat is empty. Nothing to export.")
            return

        # Создаем имя файла в текущей папке
        safe_name = chat_data['name'].replace(' ', '_').lower()
        filename = f"chat_{safe_name}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {chat_data['name']}\n\n")
            for msg in chat_data['history']:
                role = msg['role'].capitalize()
                if role == "Assistant":
                    f.write(f"## 🤖 {role}\n```\n{msg['content']}\n```\n\n")
                else:
                    f.write(f"## 👤 {role}\n{msg['content']}\n\n")
        
        print(f"[SYSTEM] Chat exported successfully to '{filename}'")
        logger.info(f"Chat exported successfully to '{filename}' ")

    def message(self, full_input):
        if not self.db.data.get('active_chat'):
            print("[ERROR] No active chat. Please create one using /new <name>")
            logger.error("No active chat.")
            return

        parts = full_input.split(" ", 1)
        if len(parts) < 2:
            print("[ERROR] Format: /message: <agent> <text>")
            logger.error("Wrong format for /message.")
            return
        
        agent_name = parts[0].lower()
        prompt_text = parts[1]

        if agent_name not in self.agent_map:
            print(f"[ERROR] Agent '{agent_name}' does not exist. Available: {', '.join(self.agent_map.keys())}")
            logger.error(f"Agent '{agent_name}' does not exist.")
            return

        agent_settings = self.agent_map[agent_name]
        provider_name = agent_settings.get("provider")
        temperature = agent_settings.get("temperature", 0.7)
        max_tokens = agent_settings.get("max_tokens", 4096)

        agent_provider = self.providers.get(provider_name)

        if not agent_provider:
            print(f"[ERROR] Provider '{provider_name}' for agent '{agent_name}' is not configured properly in config.json.")
            logger.error(f"Provider '{provider_name}' for agent '{agent_name}' is not configured properly in config.json")
            return

        system_prompt = agent_settings.get("system_prompt") or self.prompts.get(agent_name, self.prompts["other"])
        history = self.db.get_active_history()
        
        self.db.add_message("user", prompt_text)
        print(f"\n[{agent_name.upper()}] Thinking...\n")

        full_response = ""

        try:
            if hasattr(agent_provider, 'chat_stream') and provider_name == "ollama":
                for chunk in agent_provider.chat_stream(
                    prompt_text, 
                    system=system_prompt, 
                    history=history,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    print(chunk, end="", flush=True)
                    full_response += chunk
                print("\n")
            else:
                with yaspin(text=f"[{agent_name.upper()}] Generating response...", color="cyan") as sp:
                    full_response = agent_provider.chat(
                        prompt_text, 
                        system=system_prompt, 
                        history=history,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    sp.ok(f"Generated {len(full_response)} characters.") 
                
                print(f"[{agent_name.upper()}]:\n{full_response}\n")
            
            self.db.add_message("assistant", full_response)
            
        except Exception as e:
            print(f"\n[ERROR] Failed to get response from AI: {e}\n")