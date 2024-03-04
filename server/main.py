#!/usr/bin/python3
from ai.chatbot import AzureAIChatBot
from crawler.web_crawler import WebCrawler
from preprocessor.json_preprocessor import JsonPreprocessor

# Crawler

crawler = WebCrawler()

# links = crawler.get_internal_links()

crawler.playwright_crawl()

json_preprocessor = JsonPreprocessor("./preprocessor/data/crawlData.json")

json_preprocessor.join_content()

df = json_preprocessor.to_dataframe()

# bot = AzureAIChatBot()

# df2 = bot.embedding_text(df, "./preprocessor/data/embedded_data.csv")

# bot.load_embedded_data_from_csv("./preprocessor/data/embedded_data.csv")

# res = bot.search_docs("What is the address for Kiaar?", top_n=4)

# prompt = bot.prepare_prompt("What is the address for Kiaar?", res)

# response = bot.chat_completion(prompt)

# print(response)