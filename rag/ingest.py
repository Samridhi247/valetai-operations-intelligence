import chromadb
import pandas as pd
import os
import shutil

# -------------------------------------------------------
# Paths
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
CSV_PATH = os.path.join(BASE_DIR, "data", "silver_operational_notes.csv")

# -------------------------------------------------------
# Delete existing ChromaDB and rebuild fresh
# -------------------------------------------------------
if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)
    print("Deleted existing ChromaDB.")

# -------------------------------------------------------
# Load CSV
# -------------------------------------------------------
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} notes from CSV.")

# -------------------------------------------------------
# Create ChromaDB client and collection
# -------------------------------------------------------
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("operational_notes")

# -------------------------------------------------------
# Ingest in batches
# -------------------------------------------------------
BATCH_SIZE = 500

for i in range(0, len(df), BATCH_SIZE):
    batch = df.iloc[i:i+BATCH_SIZE]

    documents = batch["note_text"].tolist()
    ids = batch["note_id"].tolist()
    metadatas = [
        {
            "property_name": row["property_name"],
            "issue_type": row["issue_type"]
        }
        for _, row in batch.iterrows()
    ]

    collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
    print(f"Ingested batch {i//BATCH_SIZE + 1} ({len(batch)} notes)")

print(f"\nDone. Total in collection: {collection.count()}")

# -------------------------------------------------------
# Verify filter works
# -------------------------------------------------------
test = collection.query(
    query_texts=["missed pickups Green Oaks"],
    where={"property_name": "Green Oaks"},
    n_results=3
)
print(f"\nFilter test (Green Oaks): {len(test['documents'][0])} results")
print(test['documents'][0])