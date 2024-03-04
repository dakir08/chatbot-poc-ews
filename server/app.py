from fastapi import FastAPI
from pydantic import BaseModel

from ai.chatbot import AzureAIChatBot

app = FastAPI()

class Chat(BaseModel):
    message: str

@app.get("/")
def index():
    return {
        "name": "Hello FAST API"
    }

@app.post("/message")
def message(chat : Chat):
    bot = AzureAIChatBot()
    
    bot.load_embedded_data_from_csv("./preprocessor/data/embedded_data.csv")

    res = bot.search_docs(chat.message, top_n=4)

    prompt = bot.prepare_prompt(chat.message, res)

    response = bot.chat_completion(prompt)
    return {
        "response":response
    }