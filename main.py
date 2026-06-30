from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from typing import TypedDict, Optional, Literal
from dotenv import load_dotenv
import os

from agents.analyst_agent import analyst_agent
from rag.resolution_agent import resolution_agent

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

load_dotenv()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

langfuse_handler = CallbackHandler()


class GraphState(TypedDict):
    question: str
    route: Optional[str]
    sql_answer: Optional[str]
    rag_answer: Optional[str]
    final_answer: Optional[str]


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


# ----------------------------
# Router Node
# ----------------------------
def router_node(state: GraphState) -> GraphState:
    question = state["question"]
    question_lower = question.lower()

    sql_overrides = [
        "compare",
        "comparison",
        "versus",
        "vs",
        "difference between",
        "how many",
        "count",
        "total",
        "average",
        "rank",
        "ranking",
        "highest",
        "lowest",
        "minimum",
        "maximum",
    ]

    hybrid_overrides = [
        "executive summary",
        "management summary",
        "management report",
        "business summary",
        "prioritize and why",
        "worst and why",
        "best and why",
    ]

    rag_overrides = [
        "why",
        "root cause",
        "cause",
        "recommend",
        "recommendation",
        "recurring",
        "pattern",
        "historical notes",
        "lessons learned",
    ]

    if any(x in question_lower for x in hybrid_overrides):
        route = "hybrid"

    elif any(x in question_lower for x in sql_overrides) and any(x in question_lower for x in rag_overrides):
        route = "hybrid"

    elif any(x in question_lower for x in sql_overrides):
        route = "sql"

    elif any(x in question_lower for x in rag_overrides):
        route = "rag"

    else:
        routing_prompt = f"""
        You are the routing agent for ValetAI.

        Classify the user's question into exactly one of these routes:

        sql:
        Use this if the question can be answered using structured database metrics only.
        Examples: counts, totals, averages, rankings, percentages, missed pickups, completion time.

        rag:
        Use this if the question requires historical operational notes only.
        Examples: why something happened, root cause, recurring issues, recommendations, patterns.

        hybrid:
        Use this only if BOTH SQL metrics and historical operational notes are needed.

        Question:
        {question}

        Reply with exactly one word only:
        sql
        rag
        hybrid
        """

        response = llm.invoke(routing_prompt)
        route = response.content.strip().lower().split()[0]

        if route not in ["sql", "rag", "hybrid"]:
            route = "hybrid"

    print(f"[ROUTER] Classified as: {route}")

    return {
        **state,
        "route": route,
        "sql_answer": state.get("sql_answer"),
        "rag_answer": state.get("rag_answer"),
        "final_answer": state.get("final_answer"),
    }


# ----------------------------
# Analyst / SQL Node
# ----------------------------
def analyst_node(state: GraphState) -> GraphState:
    print("[ANALYST_NODE] ENTERED")

    try:
        result = analyst_agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": state["question"]
                }
            ]
        },
        
        config={
                "recursion_limit": 15,
                "callbacks": [langfuse_handler],
            }

        )

        answer = result["messages"][-1].content

    except Exception as e:
        print(f"[ANALYST_NODE ERROR] {e}")
        answer = "I could not retrieve SQL metrics for this question due to a temporary SQL analysis issue."

    print("[ANALYST_NODE] AGENT RETURNED")
    print(f"[ANALYST AGENT] {answer}")

    return {
        **state,
        "sql_answer": answer
    }


# ----------------------------
# Resolution / RAG Node
# ----------------------------
def resolution_node(state: GraphState) -> GraphState:
    print("[RESOLUTION_NODE] ENTERED")

    try:
        result = resolution_agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": state["question"]
                }
            ]
        },
        config={
                "recursion_limit": 15,
                "callbacks": [langfuse_handler],
            }
        )

        answer = result["messages"][-1].content

    except Exception as e:
        print(f"[RESOLUTION_NODE ERROR] {e}")
        answer = "No relevant historical operational notes were found for this issue."

    print("[RESOLUTION_NODE] AGENT RETURNED")
    print(f"[RESOLUTION AGENT] {answer}")

    return {
        **state,
        "rag_answer": answer
    }


# ----------------------------
# Synthesizer Node
# ----------------------------
def synthesizer_node(state: GraphState) -> GraphState:
    print("[SYNTHESIZER_NODE] ENTERED")

    sql_answer = state.get("sql_answer")
    rag_answer = state.get("rag_answer")

    if sql_answer and rag_answer:
        merge_prompt = f"""
You have two pieces of analysis answering the same question.

Prioritize the exact SQL data as the primary authoritative answer.
Use the RAG answer only as supporting context if it clearly applies.

If the RAG answer does not clearly explain the SQL result, do not force a connection.
Say that the specific cause requires further investigation.

Question:
{state["question"]}

SQL answer:
{sql_answer}

RAG answer:
{rag_answer}

Write the final response using exactly this structure:

Primary Finding
---------------

Likely Cause
------------

Recommended Actions
-------------------

Summary
-------
"""

        response = llm.invoke(merge_prompt)
        final = response.content

    elif sql_answer:
        final = sql_answer

    elif rag_answer:
        final = rag_answer

    else:
        final = "I could not generate an answer because neither SQL nor RAG returned a result."

    print(f"[SYNTHESIZER] {final}")

    return {
        **state,
        "final_answer": final
    }


# ----------------------------
# Routing Decisions
# ----------------------------
def route_decision(state: GraphState) -> Literal["analyst", "resolution"]:
    route = state.get("route")

    if route == "sql":
        return "analyst"

    if route == "rag":
        return "resolution"

    return "analyst"


def after_analyst(state: GraphState) -> Literal["resolution", "synthesizer"]:
    route = state.get("route")

    if route == "hybrid":
        return "resolution"

    return "synthesizer"


# ----------------------------
# Build Graph
# ----------------------------
graph = StateGraph(GraphState)

graph.add_node("router", router_node)
graph.add_node("analyst", analyst_node)
graph.add_node("resolution", resolution_node)
graph.add_node("synthesizer", synthesizer_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "analyst": "analyst",
        "resolution": "resolution",
    }
)

graph.add_conditional_edges(
    "analyst",
    after_analyst,
    {
        "resolution": "resolution",
        "synthesizer": "synthesizer",
    }
)

graph.add_edge("resolution", "synthesizer")

# Important: hard stop after synthesizer
graph.add_edge("synthesizer", END)

app = graph.compile()


if __name__ == "__main__":
    question = "Which property should management prioritize and why?"

    result = app.invoke(
        {
            "question": question,
            "route": None,
            "sql_answer": None,
            "rag_answer": None,
            "final_answer": None,
        },
        config={
            "recursion_limit": 15,
            "callbacks": [langfuse_handler],
        }
    )

    print("\n=== FINAL ANSWER ===")
    print(result["final_answer"])

# from langgraph.graph import StateGraph, END
# from langchain_groq import ChatGroq
# from typing import TypedDict, Optional
# from dotenv import load_dotenv
# import os

# from agents.analyst_agent import analyst_agent
# from rag.resolution_agent import resolution_agent

# from langfuse import Langfuse
# from langfuse.langchain import CallbackHandler

# load_dotenv()

# langfuse = Langfuse(
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     host=os.getenv("LANGFUSE_HOST")
# )

# langfuse_handler = CallbackHandler()

# # --- STATE: the shared dictionary that travels through every node ---
# class GraphState(TypedDict):
#     question: str
#     route: Optional[str]
#     sql_answer: Optional[str]
#     rag_answer: Optional[str]
#     final_answer: Optional[str]

# # llm = ChatGroq(
# #     model="llama-3.1-8b-instant",
# #     api_key=os.getenv("GROQ_API_KEY")
# # )

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     api_key=os.getenv("GROQ_API_KEY")
# )

# # --- NODE 1: Router - LLM decides which agent(s) should handle this ---
# # def router_node(state: GraphState) -> GraphState:
# #     question = state["question"]

# #     routing_prompt = f"""Classify this question into exactly one category:
# # - "sql" if it asks for exact numbers, counts, rates, or rankings
# # - "rag" if it asks why something happens, or asks for recommendations/patterns
# # - "hybrid" if it needs both exact numbers AND reasoning/recommendations

# # Question: {question}

# # Reply with only one word: sql, rag, or hybrid"""

# #     response = llm.invoke(routing_prompt)
# #     route = response.content.strip().lower()

# #     if route not in ["sql", "rag", "hybrid"]:
# #         route = "hybrid"  # safe fallback

# #     print(f"[ROUTER] Classified as: {route}")
# #     return {**state, "route": route}

# def router_node(state: GraphState) -> GraphState:

#     question = state["question"]
#     question_lower = question.lower()

#     # ----------------------------
#     # Small deterministic overrides
#     # ----------------------------
#     sql_overrides = [
#     "compare",
#     "comparison",
#     "versus",
#     "vs",
#     "difference between",
#     ]


#     if any(x in question_lower for x in sql_overrides):
#         print("[ROUTER] Keyword override -> sql")
#         return {**state, "route": "sql"}


#     hybrid_overrides = [
#         "executive summary",
#         "management summary",
#         "management report",
#         "business summary",
#     ]

    
#     if any(x in question_lower for x in hybrid_overrides):
#         print("[ROUTER] Keyword override -> hybrid")
#         return {**state, "route": "hybrid"}

#     # ----------------------------
#     # LLM Router
#     # ----------------------------
#     routing_prompt = f"""
# You are the routing agent for ValetAI.

# Your job is to decide which specialist agent should answer the user's question.

# There are ONLY three possible routes.

# --------------------------------------------------------
# SQL
# --------------------------------------------------------

# Choose SQL ONLY if the question can be answered completely
# using structured operational metrics stored in the SQL database.

# These include:

# - counts
# - totals
# - averages
# - rankings
# - percentages
# - completion time
# - missed pickups
# - bags collected
# - property statistics

# --------------------------------------------------------
# RAG
# --------------------------------------------------------

# Choose RAG ONLY if the answer requires historical operational notes.

# Examples:

# - why something happened
# - root causes
# - recurring issues
# - operational patterns
# - recommendations
# - historical notes
# - summarize operational notes
# - lessons learned

# --------------------------------------------------------
# HYBRID
# --------------------------------------------------------

# Choose HYBRID ONLY if BOTH are required.

# That means:

# • structured metrics from SQL

# AND

# • historical operational notes from RAG

# Typical Hybrid questions include:

# - Which property is performing worst and why?
# - Which property should management prioritize?
# - Executive summary
# - Management report
# - Business assessment

# IMPORTANT:

# DO NOT choose Hybrid simply because a property name appears.

# If SQL ALONE can answer the question,
# choose SQL.

# If RAG ALONE can answer the question,
# choose RAG.

# Only choose Hybrid when BOTH sources are necessary.

# Question:

# {question}

# Reply with exactly ONE word.

# sql

# rag

# hybrid
# """

#     response = llm.invoke(routing_prompt)

#     route = response.content.strip().lower().split()[0]

#     if route not in ["sql", "rag", "hybrid"]:
#         route = "hybrid"

#     print(f"[ROUTER] Classified as: {route}")

#     return {**state, "route": route}

# # def router_node(state: GraphState) -> GraphState:
# #     question = state["question"]

# #     routing_prompt = f"""
# # Classify this question into exactly one category:
# # - "sql" if it ONLY asks for exact numbers, counts, rates, or rankings, with no need to explain why
# # - "rag" if it ONLY asks why something happens, or for recommendations, with no specific numbers needed
# # - "hybrid" if it asks WHICH property/route/area (needs a ranking number) AND WHY or what to do about it

# # Examples:
# # "How many missed pickups does Green Oaks have?" -> sql
# # "Why do we keep missing collections at Sunset Ridge?" -> rag
# # "Which property should management prioritize and why?" -> hybrid
# # "What is the average completion time?" -> sql
# # "What's the best way to reduce missed pickups?" -> rag
# # "Which property has the worst performance and what should we do about it?" -> hybrid

# # Question: {question}

# # Reply with only one word: sql, rag, or hybrid
# # """

# #     response = llm.invoke(routing_prompt)
# #     route = response.content.strip().lower()

# #     if route not in ["sql", "rag", "hybrid"]:
# #         route = "hybrid"

# #     print(f"[ROUTER] Classified as: {route}")
# #     return {**state, "route": route}

# # --- NODE 2: Analyst Agent (SQL) ---
# # def analyst_node(state: GraphState) -> GraphState:
# #     result = analyst_agent.invoke({"messages": [{"role": "user", "content": state["question"]}]})
# #     answer = result["messages"][-1].content
# #     print(f"[ANALYST AGENT] {answer}")
# #     return {**state, "sql_answer": answer}

# def analyst_node(state: GraphState) -> GraphState:
#     print("[ANALYST_NODE] ENTERED")
#     result = analyst_agent.invoke({"messages": [{"role": "user", "content": state["question"]}]})
#     print("[ANALYST_NODE] AGENT RETURNED")
#     answer = result["messages"][-1].content
#     print(f"[ANALYST AGENT] {answer}")
#     return {**state, "sql_answer": answer}

# # --- NODE 3: Resolution Agent (RAG) ---
# # def resolution_node(state: GraphState) -> GraphState:
# #     result = resolution_agent.invoke({"messages": [{"role": "user", "content": state["question"]}]})
# #     answer = result["messages"][-1].content
# #     print(f"[RESOLUTION AGENT] {answer}")
# #     return {**state, "rag_answer": answer}

# def resolution_node(state: GraphState) -> GraphState:
#     try:
#         result = resolution_agent.invoke({"messages": [{"role": "user", "content": state["question"]}]})
#         answer = result["messages"][-1].content
#     except Exception as e:
#         print(f"[RESOLUTION_NODE ERROR] {e}")
#         answer = "No relevant historical operational notes were found for this issue. (The notes search encountered a temporary issue — try rephrasing the question.)"
#     print(f"[RESOLUTION AGENT] {answer}")
#     return {**state, "rag_answer": answer}

# # --- NODE 4: Synthesizer - merges answers if both ran ---
# # def synthesizer_node(state: GraphState) -> GraphState:
# #     if state.get("sql_answer") and state.get("rag_answer"):
# #         merge_prompt = f"""Combine these two answers into one clear response.

# # Exact data: {state['sql_answer']}

# # Pattern-based insight: {state['rag_answer']}

# # Write one combined answer:"""
# #         response = llm.invoke(merge_prompt)
# #         final = response.content
# #     elif state.get("sql_answer"):
# #         final = state["sql_answer"]
# #     else:
# #         final = state["rag_answer"]

# #     print(f"[SYNTHESIZER] {final}")
# #     return {**state, "final_answer": final}

# # def synthesizer_node(state: GraphState) -> GraphState:
# #     if state.get("sql_answer") and state.get("rag_answer"):
# #         merge_prompt = f"""You have two pieces of analysis answering the same question.
# #         If they point to different properties or conclusions, prioritize the exact data
# #         (SQL) as the primary answer, and use the pattern-based insight (RAG) to explain
# #         WHY, or as a secondary consideration. Do not just list both separately - reconcile
# #         them into one clear, confident recommendation.

# #         Exact data: {state['sql_answer']}

# #         Pattern-based insight: {state['rag_answer']}

# #         Write one combined, reconciled answer:"""
# #         response = llm.invoke(merge_prompt)
# #         final = response.content
# #     elif state.get("sql_answer"):
# #         final = state["sql_answer"]
# #     else:
# #         final = state["rag_answer"]

# #     print(f"[SYNTHESIZER] {final}")
# #     return {**state, "final_answer": final}


# # def synthesizer_node(state: GraphState) -> GraphState:
# #     if state.get("sql_answer") and state.get("rag_answer"):
# #         merge_prompt = f"""You have two pieces of analysis answering the same question.
# # Prioritize the exact data (SQL) as the primary, authoritative answer when the two
# # conflict, and use the pattern-based insight (RAG) as supporting explanation.

# # Exact data: {state['sql_answer']}

# # Pattern-based insight: {state['rag_answer']}

# # Write your answer using exactly this structure, with these section headers:

# # Primary Finding
# # ---------------
# # State the exact data-driven answer clearly, with the specific numbers.

# # Likely Cause
# # ------------
# # Explain the probable root cause, based on the pattern-based insight. If the
# # insight conflicts with the primary finding, note that here and explain why
# # the primary finding still takes priority.

# # Recommended Actions
# # --------------------
# # List 2-3 concrete, specific actions, numbered.

# # Summary
# # -------
# # One or two sentences a manager could read on their own without the rest."""
# #         response = llm.invoke(merge_prompt)
# #         final = response.content
# #     elif state.get("sql_answer"):
# #         final = state["sql_answer"]
# #     else:
# #         final = state["rag_answer"]

# #     print(f"[SYNTHESIZER] {final}")
# #     return {**state, "final_answer": final}

# def synthesizer_node(state: GraphState) -> GraphState:
#     if state.get("sql_answer") and state.get("rag_answer"):

#         merge_prompt = f"""
# You have two pieces of analysis answering the same question.

# Prioritize the exact data (SQL) as the primary, authoritative answer when the two conflict, and use the pattern-based insight (RAG) as supporting explanation.

# If the pattern-based insight does not clearly explain the specific metric in the primary finding, do not force a connection or narrate the mismatch. Instead, state the primary finding confidently on its own, and mention the pattern-based insight only as a separate, secondary observation worth monitoring - without claiming it explains the primary finding if it doesn't.

# Exact data:
# {state["sql_answer"]}

# Pattern-based insight:
# {state["rag_answer"]}

# Write your answer using exactly this structure, with these section headers:

# Primary Finding
# ---------------

# State the exact data-driven answer clearly, with the specific numbers.

# Likely Cause
# ------------

# If the pattern-based insight genuinely explains the primary finding, state it directly and confidently.
# If it does not clearly connect, say plainly that the specific cause requires further investigation, and mention the secondary observation separately rather than forcing a weak connection.

# Recommended Actions
# -------------------

# Generate only recommendations supported by:

# - the SQL metrics
# - the retrieved historical notes

# Do NOT invent recommendations.

# If evidence is limited, recommend
# further investigation instead.

# Summary
# -------

# One or two sentences a manager could read on their own without the rest.
# """

#         response = llm.invoke(merge_prompt)
#         final = response.content

#     elif state.get("sql_answer"):
#         final = state["sql_answer"]

#     else:
#         final = state["rag_answer"]

#     print(f"[SYNTHESIZER] {final}")
#     return {**state, "final_answer": final}

# # --- EDGES: deciding where to go after the router ---
# def route_decision(state: GraphState) -> str:
#     route = state["route"]
#     if route == "sql":
#         return "analyst_only"
#     elif route == "rag":
#         return "resolution_only"
#     else:
#         return "both"

# # --- BUILD THE GRAPH ---
# graph = StateGraph(GraphState)

# graph.add_node("router", router_node)
# graph.add_node("analyst", analyst_node)
# graph.add_node("resolution", resolution_node)
# graph.add_node("synthesizer", synthesizer_node)

# graph.set_entry_point("router")

# graph.add_conditional_edges(
#     "router",
#     route_decision,
#     {
#         "analyst_only": "analyst",
#         "resolution_only": "resolution",
#         "both": "analyst",  # if hybrid, go to analyst first, then resolution
#     }
# )

# # if hybrid, after analyst we still need resolution before synthesizer
# def after_analyst(state: GraphState) -> str:
#     if state["route"] == "hybrid":
#         return "resolution"
#     return "synthesizer"

# graph.add_conditional_edges("analyst", after_analyst, {
#     "resolution": "resolution",
#     "synthesizer": "synthesizer"
# })

# graph.add_edge("resolution", "synthesizer")
# graph.add_edge("synthesizer", END)

# app = graph.compile()


# # if __name__ == "__main__":
# #     question = "Which property should management prioritize and why?"
# #     result = app.invoke({"question": question})
# #     print("\n=== FINAL ANSWER ===")
# #     print(result["final_answer"])

# # if __name__ == "__main__":
# #     question = "Which property should management prioritize and why?"
# #     result = app.invoke(
# #         {"question": question},
# #         config={"callbacks": [langfuse_handler]}
# #     )
# #     print("\n=== FINAL ANSWER ===")
# #     print(result["final_answer"])

# if __name__ == "__main__":
#     question = "Which property should management prioritize and why?"
#     result = app.invoke(...)