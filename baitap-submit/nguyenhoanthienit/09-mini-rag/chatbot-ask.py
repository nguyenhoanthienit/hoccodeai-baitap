# 2. Thay vì hardcode `doc = wiki.page('Hayao_Miyazaki').text`, sử dụng function calling để:
#   - Lấy thông tin cần tìm từ câu hỏi
#   - Dùng `wiki.page` để lấy thông tin về
#   - Sử dụng RAG để có kết quả trả lời đúng.
import chromadb
from chromadb.utils import embedding_functions
from wikipediaapi import Wikipedia
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "wiki"

chroma_client = chromadb.PersistentClient(path="./data")
chroma_client.heartbeat()

embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)

wiki = Wikipedia('nguyenhoanthienit/1 (nguyenhoanthienit@gmail.com)', 'en')

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "openai/gpt-oss-120b"

# Function calling: LLM đọc câu hỏi và trả về tên trang Wikipedia cần tìm
tools = [{
    "type": "function",
    "function": {
        "name": "get_wiki_page",
        "description": "Get the English Wikipedia page title of the person, anime or topic the question is about.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Wikipedia page title",
                }
            },
            "required": ["title"],
        },
    },
}]

query = "Why Conan not tell Ran about the truth?"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        # Hướng dẫn model luôn gọi tool, kể cả khi câu hỏi chỉ nhắc tên nhân vật
        {"role": "system", "content": "Always call get_wiki_page with the English Wikipedia article title that best answers the question. If the question is about a character, use the title of the anime, manga, film or book the character comes from."},
        {"role": "user", "content": query},
    ],
    tools=tools,
    tool_choice="required",
    temperature=0
)
tool_call = response.choices[0].message.tool_calls[0]
title = json.loads(tool_call.function.arguments)["title"]
print(f"Wikipedia page: {title}")

# Thay cho wiki.page("Naruto") hardcode
page = wiki.page(title)
if not page.exists():
    raise SystemExit(f"Không tìm thấy trang Wikipedia: {title}")
doc = page.text

paragraphs = doc.split('\n\n')

# save in collection (upsert để chạy lại không bị trùng id; id có tên trang để nhiều trang dùng chung 1 collection)
collection.upsert(
    documents=paragraphs,
    ids=[f"{title}-{index}" for index in range(len(paragraphs))],
    metadatas=[{"title": title}] * len(paragraphs),
)

# Chỉ tìm trong các đoạn của trang vừa lấy
q = collection.query(query_texts=[query], n_results=3, where={"title": title})
CONTEXT = q["documents"][0]
# print(CONTEXT)

prompt = f"""
You are a helpful assistant that provides information about famous people, anime, and other topics based on the context provided. Use the context to answer the question accurately.
Context: {CONTEXT}
Question: {query}
"""

# rag response
response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

print(response.choices[0].message.content)
