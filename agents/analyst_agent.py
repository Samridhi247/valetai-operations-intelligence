from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

from tools.sql_tool import run_sql_query

load_dotenv()

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY")
# )

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY"),
#     model_kwargs={"tool_choice": "auto"}  # try this first
# )

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

tools = [run_sql_query]

analyst_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
You are an Operations Analyst for Valet Living.

You answer questions using ONLY the run_sql_query tool.

Rules:

1. Always use the run_sql_query tool before answering.

2. The SQL query result is the single source of truth.

3. NEVER change, round, estimate, convert, or reinterpret any numeric value returned by SQL unless the user explicitly asks for a conversion.

4. Preserve every metric exactly as returned by SQL.

5. If SQL returns 1116.821185617104 minutes, your answer must contain 1116.821185617104 minutes (or a clearly rounded version like 1116.82 minutes). Never convert it into another unit.

6. Never invent values.

7. Never infer missing information.

8. If SQL returns no rows, clearly state that no matching records were found.

9. If the user asks for rankings, comparisons, highest, lowest, averages, totals, or property performance, answer strictly from the SQL output.

10. Keep answers concise, factual, and professional.

The SQL output is authoritative. Your job is to explain it, not modify it.
"""
    # system_prompt="""
    # You are an Operations Analyst for Valet Living.
    # Always answer the complete user question.
    # If the user asks for both a metric and an identifier (property_id, property_name, route_id, etc.), your SQL query must return both.
    # Never return only an aggregate value when additional columns are requested.
    # Answer questions about waste collection performance using the run_sql_query tool.
    # Always write a SELECT query, run it, and then explain the result in plain English in not more than 3 to 4 sentences.
    # """
)


# import sqlite3
# import pandas as pd
# from langchain_groq import ChatGroq
# from langchain.tools import tool
# from langchain.agents import create_agent
# from dotenv import load_dotenv
# import os

# load_dotenv()

# @tool
# def run_sql_query(query: str) -> str:
#     """
#     Runs a SQL query against the ValetAI database and returns the results.
#     The database has two tables:
#     - property_metrics (one row per property, pre-aggregated totals - columns: property_name,
#       total_collections, total_missed_pickups, total_bags_collected, avg_completion_minutes,
#       missed_pickup_rate). USE THIS TABLE for any question comparing properties overall,
#       asking for "best", "worst", "highest", "lowest", "total", or "rate" - these refer to
#       property-level totals, not individual collection events.
#     - waste_logs (one row per individual collection event - columns: collection_id, property_id,
#       property_name, collection_date, route_id, bags_collected, missed_pickups, completion_time,
#       collector_id, region). Only use this for questions about specific dates, routes, or
#       individual collection events, not for property-level comparisons.
#     Only use SELECT statements. Always use exact column names listed above.
#     When asked for a minimum, maximum, best, or worst value, always also select the
#     corresponding property_name or property_id in the same query - never return an
#     aggregate value alone without its identifying property. Apply subqueries wherever needed and also 
#     use windowing and ranking functions wherever needed.
#     """
#     try:
#         conn = sqlite3.connect("data/valetai.db")
#         result = pd.read_sql(query, conn)
#         conn.close()
#         return result.to_string(index=False)
#     except Exception as e:
#         return f"SQL Error: {str(e)}"

# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     api_key=os.getenv("GROQ_API_KEY")
# )

# tools = [run_sql_query]

# # analyst_agent = create_react_agent(
# #     model=llm,
# #     tools=tools,
# #     prompt="You are an Operations Analyst for Valet Living. "
# #            "Answer questions about waste collection performance using the run_sql_query tool. "
# #            "Always write a SELECT query, run it, and then explain the result in plain English."
# # )

# analyst_agent = create_agent(
#     model=llm,
#     tools=tools,
#     system_prompt="""
#     You are an Operations Analyst for Valet Living.

#     You are an Operations Analyst.

#     Always answer the complete user question.

#     If the user asks for both a metric and an identifier (property_id, property_name, route_id, etc.), your SQL query must return both.

#     Never return only an aggregate value when additional columns are requested.

#     Answer questions about waste collection performance using the run_sql_query tool.

#     Always write a SELECT query, run it, and then explain the result in plain English in not more than 3 to 4 sentences.
#     """
# )


# # if __name__ == "__main__":
# #     question = "How many missed pickups does Green Oaks have in total?"
# #     result = analyst_agent.invoke({"messages": [{"role": "user", "content": question}]})
# #     print("\n=== FINAL ANSWER ===")
# #     print(result["messages"][-1].content)

if __name__ == "__main__":
    question = "Which property is struggling the most?"
    result = analyst_agent.invoke({
        "messages": [{"role": "user", "content": "Which property is struggling the most and why?"}]
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
