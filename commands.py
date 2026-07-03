import time
from art import text2art as t2

class Commands:
    def __init__(self, providers, agent_map, config_path, version):
        self.providers = providers
        self.agent_map = agent_map
        self.config_path = config_path
        self.version = version

        self.prompts = {
            "code": "You are an expert programmer. Write clean, optimized code with comments. Answer only to the point.",
            "ideas": "You are a creative idea generator. Help with brainstorming and offer non-standard solutions.",
            "other": "You are a helpful AI assistant. Answer any user questions friendly and in detail."
        }

    def help(self):
        print("\n--- AVAILABLE COMMANDS ---")
        print("/help          - Show this help message")
        print("/about         - Information about Cortex")
        print("/version       - Current version")
        print("/settings      - Show current configuration")
        print("/message: <agent> <text> - Send message to agent")
        print("               Agents: code, ideas, other")
        print("/stop          - Stop Cortex")
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

    def message(self, full_input):
        parts = full_input.split(" ", 1)
        if len(parts) < 2:
            print("[ERROR] Format: /message: <agent> <text>")
            return
        
        agent_name = parts[0].lower()
        prompt_text = parts[1]

        if agent_name not in self.agent_map:
            print(f"[ERROR] Agent '{agent_name}' does not exist. Available: {', '.join(self.agent_map.keys())}")
            return

        provider_name = self.agent_map[agent_name]
        agent_provider = self.providers.get(provider_name)

        if not agent_provider:
            print(f"[ERROR] Provider '{provider_name}' for agent '{agent_name}' is not configured properly in config.json.")
            return

        system_prompt = self.prompts.get(agent_name, self.prompts["other"])
        
        print(f"\n[{agent_name.upper()}] Thinking...")
        try:
            response = agent_provider.chat(prompt_text, system=system_prompt)
            print(f"\n[{agent_name.upper()}]:\n{response}\n")
        except Exception as e:
            print(f"[ERROR] Failed to get response from AI: {e}\n")