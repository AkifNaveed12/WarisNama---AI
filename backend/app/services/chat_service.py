import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.chatbot import InheritanceChatbot

class ChatService:
    def __init__(self):
        self.chatbot = InheritanceChatbot()
    
    def process_message(self, user_message: str):
        response = self.chatbot.chat(user_message)
        scenario = self.chatbot.get_scenario()
        return response, scenario