# 🤖 **Agent Configuration Guide**

Cortex allows you to create an unlimited number of custom AI agents. You don't need to write code — just edit your `~/.cortex/config.json`.

## 🌡️ **How Temperature Works**

Temperature controls how "creative" or "strict" the AI is. It ranges from 0.0 to 1.0+.

- 0.0 - 0.2 (Strict Mode): The AI is a calculator. It follows rules perfectly, writes clean code, and translates accurately. Best for: Coding, Math, Translation, Data extraction.

- 0.3 - 0.6 (Balanced Mode): The AI is a good assistant. It answers questions correctly but can explain things in a conversational way. Best for: General questions, Explanations, Summarizing text.

- 0.7 - 0.9 (Creative Mode): The AI starts taking risks with word choices. It might make unexpected connections. Best for: Brainstorming, Storytelling, Ideas generation.
1.0+ (Chaos Mode): The AI breaks the rules. It will hallucinate, make weird connections, and be highly unpredictable. Best for: Extreme brainstorming, Creative writing prompts.

## ⚙️ **Agent Structure**

- Every agent in your config.json under the "agents" block looks like this:

```json
{
"your_agent_name": {
"provider": "ollama",       // Which AI to use (ollama, gemini, openai, openrouter)
"temperature": 0.7,         // Creativity level (see above)
"max_tokens": 4096,         // Maximum length of the response
"system_prompt": "You are..." // The hidden instruction that defines the agent's personality
}
}
```

## 💡 **Pro-Tips for system_prompt**

- The system_prompt is the most powerful tool. Be specific!

**Bad:** "You are a coder."
**Good:** "You are a senior Python developer. Only output code. Do not explain. Use type hints."
**Bad:** "Help me with marketing."
**Good:** "You are a viral marketing expert. Generate 5 hook statements for a TikTok video about AI."

Once you create or edit an agent in config.json, just restart Cortex to apply changes.

---