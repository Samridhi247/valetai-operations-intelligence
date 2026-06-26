import chromadb
from langchain.tools import tool

# -------------------------------------------------------
# Connect to ChromaDB
# -------------------------------------------------------

client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection("operational_notes")

# -------------------------------------------------------
# Known properties
# -------------------------------------------------------

properties = [
    "Sunset Ridge",
    "Green Oaks",
    "Maple Court",
    "Birchwood Commons",
    "Lakeview Terrace",
    "Cedar Park",
    "Willow Creek",
    "Harbor Pointe"
]

# -------------------------------------------------------
# Vector Search Tool
# -------------------------------------------------------

@tool
def search_operational_notes(query: str) -> str:
    """
    Performs semantic search over historical operational notes stored in the
    ValetAI vector database.

    Use this tool when the user asks:
    - Why did something happen?
    - What caused an issue?
    - What patterns are observed?
    - What recommendations can improve operations?
    - What recurring problems exist?
    - Explain operational trends.
    - Suggest possible root causes.

    DO NOT use this tool for:
    - Counts
    - Totals
    - Rankings
    - SQL analytics
    - Numerical comparisons

    If a property name is explicitly mentioned in the query,
    only search notes for that property.

    Otherwise search across the complete knowledge base.
    """

    # -------------------------------------------------------
    # Detect property mentioned in the query
    # -------------------------------------------------------

    detected_property = None

    for prop in properties:
        if prop.lower() in query.lower():
            detected_property = prop
            break

    # -------------------------------------------------------
    # Perform vector search
    # -------------------------------------------------------

    if detected_property:
        results = collection.query(
            query_texts=[query],
            where={"property_name": detected_property},
            n_results=10
        )
    else:
        results = collection.query(
            query_texts=[query],
            n_results=10
        )

    notes = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Remove duplicate notes
    unique_notes = {}
    for note, meta in zip(notes, metadatas):
        if note not in unique_notes:
            unique_notes[note] = meta

    if len(unique_notes) == 0:
        return "RETRIEVED_COUNT: 0\nNo relevant historical operational notes were found."

    formatted = [f"RETRIEVED_COUNT: {len(unique_notes)}"]
    for note, meta in unique_notes.items():
        formatted.append(f"[{meta['property_name']} - {meta['issue_type']}] {note}")

    return "\n".join(formatted)

    # -------------------------------------------------------
    # Extract results
    # -------------------------------------------------------

    # notes = results["documents"][0]
    # metadatas = results["metadatas"][0]

    # if len(notes) == 0:
    #     return "No relevant operational notes were found."

    # # -------------------------------------------------------
    # # Remove duplicate notes
    # # -------------------------------------------------------

    # unique_notes = {}

    # for note, meta in zip(notes, metadatas):

    #     if note not in unique_notes:
    #         unique_notes[note] = meta

    # # -------------------------------------------------------
    # # Format response
    # # -------------------------------------------------------

    # formatted = []

    # for note, meta in unique_notes.items():

    #     formatted.append(
    #         f"[{meta['property_name']} - {meta['issue_type']}] {note}"
    #     )

    # return "\n".join(formatted)



# import chromadb
# from langchain.tools import tool

# client = chromadb.PersistentClient(path="data/chroma_db")
# collection = client.get_or_create_collection("operational_notes")

# # @tool
# # def search_operational_notes(query: str) -> str:
# #     """
# #     Searches historical operational notes for issues related to the query.
# #     Use this when a question asks WHY something is happening, or asks for
# #     patterns, root causes, or recommendations - not for exact counts or numbers.
# #     Returns the most relevant past notes about property operations issues.
# #     """
# @tool
# def search_operational_notes(query: str) -> str:
#     """
#     Performs semantic search over historical operational notes stored in the
#     ValetAI vector database.

#     Use this tool when the user asks:

#     - Why did something happen?
#     - What caused an issue?
#     - What patterns are observed?
#     - What recommendations can improve operations?
#     - What recurring problems exist?
#     - Explain operational trends.
#     - Suggest possible root causes.

#     Do NOT use this tool for:

#     - Counts
#     - Totals
#     - Rankings
#     - SQL analytics
#     - Numerical comparisons

#     Those questions should use the SQL analytics tool.

#     Returns the most relevant historical operational notes together with
#     metadata to help explain business context.
#     """
#     results = collection.query(query_texts=[query], n_results=5)
#     notes = results["documents"][0]
#     metadatas = results["metadatas"][0]

#     formatted = []
#     for note, meta in zip(notes, metadatas):
#         formatted.append(f"[{meta['property_name']} - {meta['issue_type']}] {note}")

#     return "\n".join(formatted)