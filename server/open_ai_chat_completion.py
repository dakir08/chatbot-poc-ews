#!/usr/bin/python3
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

system = """
You are an AI assistant that helps people find information.

"""

# Reinitialzing messages
messages = [{"role": "system", "content": system},]

prompt = "What is 1+1"

messages.append({"role": "user", "content": "What is 1+1"})
messages.append({"role": "assistant", "content": "The sum of 1 and 1 is 2."})
messages.append({"role": "user", "content": "What is my previous and the answer?"})

chat_completion = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"),
    messages=messages
)

print(chat_completion.choices[0].message)