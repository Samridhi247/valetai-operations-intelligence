import chromadb
import pandas as pd

client = chromadb.PersistentClient(path="data/chroma_db")

# Delete old collection (if it exists)

try:
    client.delete_collection("operational_notes")
    print("Old collection deleted.")
except:
    print("No existing collection found.")

# Creating fresh collection

collection = client.create_collection("operational_notes")

# Loading CSV

df_notes = pd.read_csv("data/silver_operational_notes.csv")

# Adding documents

collection.add(
    ids=df_notes["note_id"].astype(str).tolist(),
    documents=df_notes["note_text"].tolist(),
    metadatas=df_notes[["property_name", "issue_type"]].to_dict("records")
)

print(f"\nLoaded {collection.count()} notes into ChromaDB\n")

#Query 1

print("=" * 60)
print("TEST 1 : Green Oaks")
print("=" * 60)

results = collection.query(
    query_texts=["Why is Green Oaks struggling?"],
    n_results=5
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"""
        Property : {meta['property_name']}
        Issue    : {meta['issue_type']}
        {doc}
    """)

#Query 2

print("=" * 60)
print("TEST 2 : Sunset Ridge")
print("=" * 60)

results = collection.query(
    query_texts=["Why do we keep missing collections at Sunset Ridge?"],
    n_results=5
)

for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"""
        Property : {meta['property_name']}
        Issue    : {meta['issue_type']}

        {doc}
     """)




# import chromadb
# import pandas as pd

# client = chromadb.PersistentClient(path="data/chroma_db")
# collection = client.get_or_create_collection("operational_notes")

# df_notes = pd.read_csv("data/silver_operational_notes.csv")

# collection.add(
#     ids=df_notes["note_id"].astype(str).tolist(),
#     documents=df_notes["note_text"].tolist(),
#     metadatas=df_notes[["property_name", "issue_type"]].to_dict("records")
# )

# print(f"Loaded {collection.count()} notes into ChromaDB")

# results = collection.query(
#     query_texts=["what operational issues are affecting property performance"],
#     n_results=10
# )
# for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
#     print(f"[{meta['issue_type']}] {doc}")

# results = collection.query(
#     query_texts=["resident complaints about waste collection"],
#     n_results=50  # cast a wider net
# )

# seen_types = set()
# unique_docs = []
# for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
#     issue = meta["issue_type"]
#     if issue not in seen_types:
#         seen_types.add(issue)
#         unique_docs.append(doc)

# for doc in unique_docs:
#     print("-", doc)

# results = collection.query(query_texts=["why do collections keep getting delayed"], n_results=3)
# for doc in results["documents"][0]:
#     print("-", doc)

# results = collection.query(query_texts=["resident complaints about waste collection"], n_results=5)
# for doc in results["documents"][0]:
#     print("-", doc)  #duplication problem

# results = collection.query(
#     query_texts=["resident complaints about waste collection"],
#     n_results=20  # ask for more candidates than we need
# )

# seen = set()
# unique_docs = []
# for doc in results["documents"][0]:
#     if doc not in seen:
#         seen.add(doc)
#         unique_docs.append(doc)
#     if len(unique_docs) == 5:  # stop once we have 5 unique ones
#         break

# for doc in unique_docs:
#     print("-", doc)
