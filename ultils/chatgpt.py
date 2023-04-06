import json
import tiktoken
import asyncio
import aiohttp
import atexit

class ChatGPT:
    API_URL = "https://api.openai.com/v1/chat/completions"
    ENGINE = "gpt-3.5-turbo"
    
    def __init__(self, api_key: str, 
                    max_tokens: int = 3000, temperature: float = 0.5, top_p: float = 1.0,
                    presence_penalty: float = 0.0, frequency_penalty: float = 0.0,
                    reply_count: int = 1,
                ):
        
        self.api_key = api_key
        self.system_prompt = "Hello, How can I help you?"
        
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.reply_count = reply_count
        self.top_p = top_p

        self.session = aiohttp.ClientSession(headers = {"Authorization": f"Bearer {api_key}"})
        atexit.register(self._close_session)
        
        self.conversation: dict = {
                                    "default": [
                                        {
                                            "role": "system",
                                            "content": self.system_prompt,
                                        },
                                    ],
                                    "auto" : [
                                        {
                                            "role": "system",
                                            "content": self.system_prompt,
                                        },
                                    ]
                                }
        
    def add_new_conversation(self, message: str, role: str, convo_id: str = "default"):
        self.conversation[convo_id].append({"role": role, "content": message})

    def __truncate_conversation(self, convo_id: str = "default"):
        while True:
            if (self.get_token_count(convo_id) > self.max_tokens and len(self.conversation[convo_id]) > 1):
                self.conversation[convo_id].pop(1)
            else:
                break

    def get_token_count(self, convo_id: str = "default"):
        encoding = tiktoken.encoding_for_model(self.ENGINE)

        num_tokens = 0
        for message in self.conversation[convo_id]:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  
                    num_tokens += 1 
                    
        num_tokens += 2 
        return num_tokens

    def get_max_tokens(self, convo_id: str) -> int:
        return self.max_tokens - self.get_token_count(convo_id)
    
    def get_role(self, data):
        data = json.loads(data)
        return data["choices"][0]["delta"]["role"]

    async def ask(self, prompt: str, role: str = "user", convo_id: str = "default"):
        if convo_id not in self.conversation:
            self.reset(convo_id=convo_id, system_prompt=self.system_prompt)
            
        self.add_new_conversation(prompt, "user", convo_id=convo_id)
        self.__truncate_conversation(convo_id=convo_id)
        
        json_data = {
                "model": self.ENGINE,
                "messages": self.conversation[convo_id],
                "stream": True,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
                "n": self.reply_count,
                "user": role,
                "max_tokens": self.get_max_tokens(convo_id=convo_id),
            }
        response = await self.session.post(self.API_URL, json = json_data)
        if response.status != 200:
            raise Exception(f"Connection error with status code: {response.status}")
            
        
        answer = ""
        data = await response.content.read()
        data = data.split(b'data: ')
        response_role = self.get_role(data[1])
        
        for line in data[2:]:
            if not line:
                continue
            
            # Remove "data: "
            line = line.decode("utf-8")
            
            if line == "[DONE]\n\n":
                break

            resp = json.loads(line)
            delta = resp['choices'][0]["delta"]
                
            if "content" in delta:
                content = delta["content"]
                answer += content
                
        self.add_new_conversation(answer, response_role, convo_id = convo_id)
        return answer
    
    def save_chat(self, filename: str, convo_id: str = "default"):
        data = self.conversation[convo_id]
        if len(data) < 2:
            return False
        
        with open(filename, "w+", encoding = "utf-8") as f:
            f.write(f"Nội dung chat:\n")
            f.write("========================================\n\n")
            
            for conver in data:
                if conver["role"] == "system" or conver["role"] == "assistant":
                    who = "## Bot:\n"
                else:
                    who = f"## You:\n"
                
                f.write(who)
                f.write(f"{conver['content']}\n<br/><br/> \n\n")
        return True

    def rollback(self, n: int = 1, convo_id: str = "default"):
        for _ in range(n):
            self.conversation[convo_id].pop()

    def reset(self, convo_id: str = "default"):
        self.conversation[convo_id] = [
                                        {
                                            "role": "system", 
                                            "content": self.system_prompt
                                            }
                                        ]

    def _close_session(self):
        asyncio.run(self.session.close())
