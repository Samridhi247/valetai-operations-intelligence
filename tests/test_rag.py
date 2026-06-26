import chromadb
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

# --- Step 1: connect to your existing ChromaDB collection ---
client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection("operational_notes")

# --- Step 2: connect to your existing LLM ---
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# --- Step 3: the actual question ---
question = "Why do we keep missing collections at Sunset Ridge?"

# --- Step 4: RETRIEVE relevant notes ---
results = collection.query(query_texts=[question], n_results=5)
retrieved_notes = results["documents"][0]

print("Retrieved context ")
for note in retrieved_notes:
    print("-", note)
print("End context \n")

# --- Step 5: AUGMENT - build a prompt with that context ---
context = "\n".join(f"- {note}" for note in retrieved_notes)

prompt = f"""Answer using ONLY the context below.

Context:
{context}

Question: {question}

Answer:"""

# --- Step 6: GENERATE - ask the LLM ---
response = llm.invoke(prompt)
print(response.content)