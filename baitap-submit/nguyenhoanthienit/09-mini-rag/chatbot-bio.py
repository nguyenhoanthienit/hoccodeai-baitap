# 1. Dùng chunking để làm bot trả lời tiểu sử người nổi tiếng, anime v...v
#   - <https://en.wikipedia.org/wiki/S%C6%A1n_T%C3%B9ng_M-TP>
#   - <https://en.wikipedia.org/wiki/Jujutsu_Kaisen>
import chromadb
from chromadb.utils import embedding_functions
from wikipediaapi import Wikipedia
from openai import OpenAI
import os
from dotenv import load_dotenv

COLLECTION_NAME = "naruto"

client = chromadb.PersistentClient(path="./data")
client.heartbeat()

embedding_function = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function
)

wiki = Wikipedia('nguyenhoanthienit/1 (nguyenhoanthienit@gmail.com)', 'en')
doc = wiki.page("Naruto").text

# print(doc)

paragraphs = doc.split('\n\n')

# save in collection
for index, paragraph in enumerate(paragraphs):
    collection.add(documents=[paragraph], ids=[str(index)])

# print(collection.peek())

questions = [
    "Why Naruto want to become Hokage?",
    "Why Sasuke want to kill Itachi?",
    "Why Naruto and Sasuke fight each other?",
]
query = " ".join(questions)  # dùng cho prompt sau này

# Mỗi câu hỏi là 1 phần tử -> Chroma tìm 3 đoạn riêng cho từng câu
q = collection.query(query_texts=questions, n_results=3)

# q["documents"] = [[3 đoạn cho câu 1], [3 đoạn cho câu 2], [3 đoạn cho câu 3]]
# Gộp lại thành 1 danh sách, bỏ đoạn trùng (giữ nguyên thứ tự)
CONTEXT = []
for docs in q["documents"]:
    for d in docs:
        if d not in CONTEXT:
            CONTEXT.append(d)
# print(CONTEXT)

prompt = f"""
You are a helpful assistant that provides information about famous people, anime, and other topics based on the context provided. Use the context to answer the question accurately.
Context: {CONTEXT}
Question: {query}
"""

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# rag response
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

print(response.choices[0].message.content)