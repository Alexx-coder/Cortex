# **Example: Custom Language Translator Agent**

*This example shows how to create a dedicated translation agent directly in your config.json.*

**1. Update** `~/.cortex/config.json`

- **Add a new agent called** *translator* to the "agents" block:

```json
"agents": {    "code": { "provider": "ollama", "temperature": 0.2 },    "ideas": { "provider": "ollama", "temperature": 0.9 },    "other": { "provider": "ollama", "temperature": 0.7 },    "translator": {      "provider": "ollama",      "temperature": 0.3,      "max_tokens": 2048,      "system_prompt": "You are a professional translator. Translate the given text accurately. Maintain the original tone and style. Only output the translation, nothing else."    }}
```

**2. Use it in Cortex**

```text
Cortex > /new French Translation
Cortex > /message: translator Hello, how are you doing today?
Cortex > /message: translator The weather is beautiful, but I have to write some Python code.
```

*(Note: Low temperature 0.3 ensures the translation is strict and accurate, not creative).*

# Example: Automated Code Reviewer

Using the `/load` command, you can turn Cortex into a strict Senior Developer that reviews your code for bugs and bad practices.

### 1. Setup a strict agent in `config.json`

```json
"agents": {
    "reviewer": {
      "provider": "ollama",
      "temperature": 0.1,
      "max_tokens": 4096,
      "system_prompt": "You are a Senior Software Engineer conducting a code review. Be extremely critical. Look for potential bugs, security vulnerabilities, performance issues, and bad architecture. Output a list of problems and how to fix them."
    }
}

```

### 2. Load your code and ask for a review

```text
Cortex > /new Review Session
Cortex > /load my_python_script.py
[SYSTEM] File 'my_python_script.py' loaded into context (1250 chars).

Cortex > /message: reviewer Please review the loaded code. Focus on security and edge cases.
```

Cortex will analyze the exact code from your file and give you a professional review!

# Example: Creative Brainstorming Partner

Need ideas for a startup, a game, or a story? Configure an agent with maximum creativity (high temperature) to break out of standard thinking.

### 1. Setup in `config.json`

```json
"agents": {
    "brainstorm": {
      "provider": "ollama",
      "temperature": 1.0,
      "max_tokens": 4096,
      "system_prompt": "You are an eccentric creative director. Think outside the box. Generate wild, unconventional, and groundbreaking ideas. Never say 'that's impossible'. Connect unrelated concepts."
    }
}
```

### 2. Generate crazy ideas

```text
Cortex > /new Startup Ideas
Cortex > /message: brainstorm Give me 5 unconventional ideas for mobile apps that use local AI models without internet.
```

*(Note: Temperature 1.0 forces the LLM to take risks with word choices, leading to highly creative and unexpected responses).*