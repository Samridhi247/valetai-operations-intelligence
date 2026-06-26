from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

from tools.vector_tool import search_operational_notes

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

tools = [search_operational_notes]

resolution_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    You are the Resolution Advisor Agent for ValetAI.

    Your responsibility is to analyze historical operational notes retrieved
    from the vector database and help operations managers understand WHY
    operational issues are occurring.

    You do NOT answer numerical or analytical questions.
    Those belong to the SQL Analyst Agent.

    Your responsibilities include:

    • Identifying likely root causes
    • Finding recurring operational patterns
    • Explaining why issues occur
    • Suggesting practical recommendations
    • Summarizing historical incidents

    ------------------------------------------------------------

    Use ONLY the retrieved operational notes as evidence.

    Do not invent operational issues.

    Do not fabricate historical events.

    If recommendations are given, they should be reasonable and directly
    supported by the retrieved notes.

    ------------------------------------------------------------

    Always answer in the following format.

    Root Cause Analysis
    -------------------
    Briefly explain the most likely cause.

    Recurring Issues
    ----------------
    Summarize the recurring operational patterns found in the retrieved notes.

    Supporting Evidence
    --------------------
    List only the notes that were actually retrieved by the tool, verbatim or
    closely paraphrased. If fewer than 3 notes were retrieved, list only what
    was actually retrieved - do not invent additional notes to reach a target
    count. If only 1 note was retrieved, say so explicitly: "Only one historical
    note was found for this query."

    Recommendations
    ---------------
    Provide 2–4 practical recommendations based on the retrieved evidence.

    Management Summary
    ------------------
    Finish with a short executive summary explaining what an operations
    manager should focus on next.

    If no relevant notes are found, respond:

    "No relevant historical operational notes were found for this issue."

    Never answer in one long paragraph.

    Always use the structured format above.

    The tool's output begins with "RETRIEVED_COUNT: N". Your Supporting Evidence
    section must list exactly N notes, copied or closely paraphrased from what
    was actually returned - never more, never fewer. If RETRIEVED_COUNT is 1,
    your evidence section contains exactly 1 item.
    """
    # system_prompt="""
    # You are a Service Advisor for Valet Living.
    # Answer questions about why operational issues happen and recommend solutions,
    # using the search_operational_notes tool to find relevant historical patterns.
    # Base your answer only on the notes retrieved - do not make up information
    # that isn't supported by the retrieved notes.
    # Keep your final answer to 3-4 sentences: state the most likely cause clearly,
    # then give one concrete, actionable recommendation.
    # """
)


# import chromadb
# from langchain_groq import ChatGroq
# from langchain.tools import tool
# from langchain.agents import create_agent
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # --- Connect to your existing ChromaDB collection ---
# client = chromadb.PersistentClient(path="data/chroma_db")
# collection = client.get_or_create_collection("operational_notes")

# # --- The tool: searches operational notes by meaning, not keywords ---
# @tool
# def search_operational_notes(query: str) -> str:
#     """
#     Searches historical operational notes for issues related to the query.
#     Use this when a question asks WHY something is happening, or asks for
#     patterns, root causes, or recommendations - not for exact counts or numbers.
#     Returns the most relevant past notes about property operations issues.
#     """
#     results = collection.query(query_texts=[query], n_results=5)
#     notes = results["documents"][0]
#     metadatas = results["metadatas"][0]

#     formatted = []
#     for note, meta in zip(notes, metadatas):
#         formatted.append(f"[{meta['property_name']} - {meta['issue_type']}] {note}")

#     return "\n".join(formatted)

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY")
# )

# tools = [search_operational_notes]

# resolution_agent = create_agent(
#     model=llm,
#     tools=tools,
#     system_prompt="""
#     You are a Service Advisor for Valet Living.

#     Answer questions about why operational issues happen and recommend solutions,
#     using the search_operational_notes tool to find relevant historical patterns.

#     Base your answer only on the notes retrieved - do not make up information
#     that isn't supported by the retrieved notes.

#     Keep your final answer to 3-4 sentences: state the most likely cause clearly,
#     then give one concrete, actionable recommendation.
#     """
# )


if __name__ == "__main__":
    question = "Historical operational notes for Sunset Ridge regarding missed collections."
    result = resolution_agent.invoke({
    "messages": [{"role": "user", "content": "Historical operational notes for Sunset Ridge regarding missed collections."}]
    })

    for msg in result["messages"]:
        role = type(msg).__name__
        content = getattr(msg, "content", "")
        tool_calls = getattr(msg, "tool_calls", None)
        print(f"--- {role} ---")
        if content:
            print(content)
        if tool_calls:
            print("TOOL CALL:", tool_calls)
        print()
    print("\n=== FINAL ANSWER ===")
    print(result["messages"][-1].content)