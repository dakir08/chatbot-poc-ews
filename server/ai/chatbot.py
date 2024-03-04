#!/usr/bin/python3
import ast
import os
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv
from pandas import DataFrame
import pandas as pd
import tiktoken

class AzureAIChatBot:

    __default_system_message = """
    You are an AI assistant that helps people find information.

    """

    __embedded_data = None
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize the AzureOpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),  
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        self.__embedding_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

    def get_encoding(self):
        # Get Tokens number
        embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
        encoding = tiktoken.get_encoding(embedding_encoding)

        return encoding

    def chat_completion(self, message):

        # Reinitializing messages
        messages = [{"role": "system", "content": self.__default_system_message}]
        messages.append({"role": "user", "content": message})

        print(f"sending message: \n {messages}")

        chat_completion = self.client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME"),
            messages=messages
        )

        return chat_completion.choices[0].message
    
    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def get_embedding(self, text, model="text-embedding-ada-002"):
        return self.client.embeddings.create(input = [text], model=model).data[0].embedding
    
    def embedding_text(self, df: DataFrame, export_to_csv_path = None):
        # Remove any row with empty text
        df = df[df.combined_content.ne("")]


        encoding = self.get_encoding()
        df["n_tokens"] = df.combined_content.apply(lambda x: len(encoding.encode(x)))

        # Embedding
        df["embedding"] = df.combined_content.apply(lambda x: self.get_embedding(x, model=self.__embedding_name))

        if (export_to_csv_path is not None):
            df.to_csv(export_to_csv_path, index=False)

        return df
    
    def search_docs(self, user_query, top_n=5):
        if (self.__embedded_data is None):
            raise ValueError("Embedded Data not found, please load the data by using load_embedded_data_from_csv method")

        embedding = self.get_embedding(
            user_query,
            model=self.__embedding_name
        )

        self.__embedded_data["embedding"] = self.__embedded_data["embedding"].apply(lambda x: ast.literal_eval(x))

        self.__embedded_data["similarities"] = self.__embedded_data.embedding.apply(lambda x: self.cosine_similarity(x, embedding))
        
        res = (
            self.__embedded_data.sort_values("similarities", ascending=False)
            .head(top_n)
        )

        return res
    def prepare_prompt(self, prompt, embedded_search_results):
        print(f"embedded_search_results \n {embedded_search_results}")
        # Define the token limit for GPT-3.5-turbo-16k
        tokens_limit = 16384

        # Preparing the start and end parts of the user prompt
        user_start = "Answer the question based on the context below.\n\nContext:\n"
        user_end = f"\n\nQuestion: {prompt}\nAnswer:"

        # Calculate the number of tokens consumed by system messages and the prompt structure
        encoding = self.get_encoding()
        system_message = "\"role\":\"system\", \"content\":\"" + self.__default_system_message + user_start + "\n\n---\n\n" + user_end
        count_of_tokens_consumed = len(encoding.encode(system_message))

        # Determine the remaining number of tokens available for context
        count_of_tokens_for_context = tokens_limit - count_of_tokens_consumed

        # Initialize an empty string for contexts
        contexts = ""

        # Iteratively add contexts from the results as long as within the token limit
        for i in range(len(embedded_search_results)):
            if count_of_tokens_for_context >= embedded_search_results.n_tokens.iloc[i]:
                contexts += embedded_search_results.combined_content.iloc[i] + "\n"
                count_of_tokens_for_context -= 1  # Decrement for the newline character
                count_of_tokens_for_context -= embedded_search_results.n_tokens.iloc[i]  # Decrement by the number of tokens in the context

        # Create the complete prompt by combining all parts
        complete_prompt = user_start + contexts + "\n\n---\n\n" + user_end
        return complete_prompt
    
    def load_embedded_data_from_csv(self, path):
        self.__embedded_data = pd.read_csv(path)


