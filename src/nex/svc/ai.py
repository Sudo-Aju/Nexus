import httpx
import json

class AIService:
    def __init__(self, provider="ollama", api_key=None, model="llama3", base_url=None):
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        if base_url:
            self.base_url = base_url
        elif provider == "ollama":
            self.base_url = "http://localhost:11434"
        elif provider == "openai":
            self.base_url = "https://api.openai.com/v1"

    async def chat(self, prompt: str) -> str:
        if self.provider == "openai":
            return await self._chat_openai(prompt)
        return await self._chat_ollama(prompt)

    async def _chat_ollama(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("response", "")
                else:
                    return f"Error: {resp.status_code} {resp.text}"
        except Exception as e:
            return f"Ollama Connection Error: {e}"

    async def _chat_openai(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data['choices'][0]['message']['content']
                else:
                    return f"OpenAI Error: {resp.status_code} {resp.text}"
        except Exception as e:
            return f"OpenAI Connection Error: {e}"
