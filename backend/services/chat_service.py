from collections import deque

class ChatService:
    def __init__(self, max_messages=100, max_length=250):
        self.messages = deque(maxlen=max_messages)
        self.max_length = max_length

    def add(self, player_id, username, message):
        item = {"player_id": player_id, "username": username, "message": message.strip()[:self.max_length]}
        self.messages.append(item)
        return item

    def history(self):
        return list(self.messages)
