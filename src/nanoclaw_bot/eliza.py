class ElizaOSIntegration:
    """ElizaOS-style AI personality integration with memory."""

    PERSONALITIES = {
        "assistant": {
            "name": "Assistant",
            "system_prompt": (
                "You are a helpful, concise AI assistant. Provide clear, actionable responses."
            ),
            "emoji": "🤖",
        },
        "therapist": {
            "name": "Therapist",
            "system_prompt": (
                "You are a compassionate therapist using active listening techniques. "
                "Ask open-ended questions, reflect feelings back, and help the user "
                "explore their thoughts. Never give medical advice."
            ),
            "emoji": "🧠",
        },
        "creative": {
            "name": "Creative",
            "system_prompt": (
                "You are an imaginative creative writing partner. Use vivid language, "
                "suggest unexpected angles, and help brainstorm ideas with enthusiasm."
            ),
            "emoji": "🎨",
        },
        "technical": {
            "name": "Technical",
            "system_prompt": (
                "You are a senior software engineer. Give precise technical answers "
                "with code examples when relevant. Mention trade-offs and best practices."
            ),
            "emoji": "💻",
        },
    }

    def __init__(self, default_personality: str = "assistant", max_messages: int = 20):
        self._default_personality = default_personality
        self._max_messages = max_messages
        self._chat_personalities: dict[int, str] = {}
        self._chat_memory: dict[int, list[dict]] = {}

    def set_personality(self, chat_id: int, personality_name: str) -> bool:
        if personality_name not in self.PERSONALITIES:
            return False
        self._chat_personalities[chat_id] = personality_name
        return True

    def get_personality(self, chat_id: int) -> dict:
        name = self._chat_personalities.get(chat_id, self._default_personality)
        return self.PERSONALITIES[name]

    def get_personality_name(self, chat_id: int) -> str:
        return self._chat_personalities.get(chat_id, self._default_personality)

    def add_message(self, chat_id: int, role: str, content: str):
        if chat_id not in self._chat_memory:
            self._chat_memory[chat_id] = []
        self._chat_memory[chat_id].append({"role": role, "content": content})
        if len(self._chat_memory[chat_id]) > self._max_messages:
            self._chat_memory[chat_id] = self._chat_memory[chat_id][-self._max_messages :]

    def get_context(self, chat_id: int) -> dict:
        personality = self.get_personality(chat_id)
        messages = self._chat_memory.get(chat_id, [])
        return {
            "system_prompt": personality["system_prompt"],
            "messages": list(messages),
        }

    def get_memory_size(self, chat_id: int) -> int:
        return len(self._chat_memory.get(chat_id, []))

    def clear_memory(self, chat_id: int):
        self._chat_memory.pop(chat_id, None)

    def enhance(self, chat_id: int, user_input: str) -> dict:
        self.add_message(chat_id, "user", user_input)
        return self.get_context(chat_id)
