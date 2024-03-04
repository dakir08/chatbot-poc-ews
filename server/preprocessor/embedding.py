import os
from dotenv import load_dotenv
import tiktoken
import pandas as pd

load_dotenv()



# embedding model parameters
embedding_model = os.getenv("DEPLOYMENT_EMBEDDED_NAME")
embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191

encoding = tiktoken.get_encoding(embedding_encoding)

# remove any row with empty text
df = df[df.text.ne('')]

df["n_tokens"] = df.text.apply(lambda x: len(encoding.encode(x)))

df["embedding"] = df.text.apply(lambda x: get_embedding(x, engine=embedding_model))

df