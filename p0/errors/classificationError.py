from enum import Enum

class ClassificationError(Exception):
    def __init__(self, message):
        text = message.value if isinstance(message, Enum) else str(message)
        super().__init__(text)