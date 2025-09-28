from collections import deque

class Memory:
    def __init__(self, buffer_size=5):
        self.buffer_size = buffer_size
        self.short_term_memory = deque(maxlen=buffer_size)
        self.rolling_summary = ""

    def add_to_memory(self, user_input, assistant_response):
        entry = {
            "user_input": user_input,
            "assistant_response": assistant_response
        }
        self.short_term_memory.append(entry)
        self.update_rolling_summary(user_input, assistant_response)

    def update_rolling_summary(self, user_input, assistant_response):
        self.rolling_summary += f"User: {user_input}\nAssistant: {assistant_response}\n"

    def get_memory(self):
        return list(self.short_term_memory)

    def get_rolling_summary(self):
        return self.rolling_summary.strip()