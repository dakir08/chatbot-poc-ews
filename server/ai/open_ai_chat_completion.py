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

def chat_completion(message):
    system = """
    You are an AI assistant that helps people find information.

    """

    # Reinitialzing messages
    messages = [{"role": "system", "content": system}]

    messages.append({"role": "user", "content": message})

    chat_completion = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"),
        messages=messages
    )

    return chat_completion.choices[0].message

