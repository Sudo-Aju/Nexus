import asyncio
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Message:
    id: str
    source: str # "gmail", "slack"
    sender: str
    subject: str
    snippet: str
    timestamp: datetime

class CommsService:
    def __init__(self):
        # In a real app, inject vault to get credentials
        pass

    async def fetch_recent(self) -> list[Message]:
        # Mock implementation for now as real auth requires user setup
        await asyncio.sleep(1) # simulate net lag
        
        return [
            Message("1", "gmail", "boss@corp.com", "Project deadline", "We need this done by...", datetime.now()),
            Message("2", "slack", "dev-team", "#general", "Deploy failed :(", datetime.now()),
            Message("3", "gmail", "newsletter@tech.com", "Weekly Update", "New features in Python...", datetime.now()),
        ]

    async def send_reply(self, target: str, content: str):
        # Mock send
        await asyncio.sleep(0.5)
        print(f"Sent reply to {target}: {content}")
