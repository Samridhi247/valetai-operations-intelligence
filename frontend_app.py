import streamlit as st
import requests

import os

# BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://valetai240705app.azurewebsites.net"
)
print("BACKEND_URL =", BACKEND_URL)

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="ValetAI Operations Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:

    st.title("🤖 ValetAI")

    st.markdown("### Operations Intelligence Platform")

    st.success("🟢 SQL Analytics")
    st.info("🔵 RAG Search")
    st.warning("🟣 Hybrid Intelligence")

    st.divider()

    st.markdown("### Sample Questions")

    sample_questions = [
        "Which property has the highest missed pickups?",
        "Why is Green Oaks struggling?",
        "Which property should management prioritize?",
        "Compare Green Oaks and Birchwood Commons.",
        "Generate an executive summary for Sunset Ridge.",
        "Which route has the highest missed pickups?",
        "Recommend improvements for Green Oaks.",
        "Show historical operational notes for Cedar Park."
    ]

    for q in sample_questions:
        st.markdown(f"• {q}")

    st.divider()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.caption("Powered by")
    st.write("• FastAPI")
    st.write("• LangGraph")
    st.write("• SQLite")
    st.write("• ChromaDB")
    st.write("• Databricks")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🤖 ValetAI")

st.markdown(
"""
### Operations Intelligence Assistant

Ask questions about property performance, missed pickups,
historical operational issues, and receive AI-powered recommendations.

**Powered by SQL Analytics • RAG • Hybrid AI**
"""
)

st.divider()


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# WELCOME SCREEN
# ---------------------------------------------------------
if len(st.session_state.messages) == 0:

    st.info(
"""
### 👋 Welcome!

Try asking:

- Which property has the highest missed pickups?

- Why is Green Oaks struggling?

- Compare Green Oaks and Birchwood Commons.

- Which property should management prioritize?

- Generate an executive summary for Sunset Ridge.
"""
    )


# ---------------------------------------------------------
# DISPLAY OLD CHAT
# ---------------------------------------------------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        if msg["role"] == "assistant":

            with st.container(border=True):

                st.markdown("### 🤖 ValetAI")

                st.write(msg["content"])

                route = msg.get("route", "")

                if route == "sql":
                    st.success("🟢 SQL Analytics")

                elif route == "rag":
                    st.info("🔵 RAG Search")

                elif route == "hybrid":
                    st.warning("🟣 Hybrid Intelligence")

                with st.expander("🧠 AI Reasoning Path"):

                    if route == "sql":
                        st.markdown("""
User Question

⬇

SQL Agent

⬇

SQLite Database

⬇

LLM Explanation
""")

                    elif route == "rag":
                        st.markdown("""
User Question

⬇

Vector Search

⬇

ChromaDB

⬇

LLM Reasoning
""")

                    elif route == "hybrid":
                        st.markdown("""
User Question

⬇

Router

⬇

SQL Agent

+

RAG Agent

⬇

Hybrid AI Response
""")

        else:
            st.write(msg["content"])


# ---------------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------------
question = st.chat_input(
    "Ask about waste collection, property performance, operational issues..."
)


# ---------------------------------------------------------
# HANDLE QUESTION
# ---------------------------------------------------------
if question:

    # Show User
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    # Assistant
    with st.chat_message("assistant"):

        with st.spinner("Analyzing operational data..."):

            try:

                # response = requests.post(
                #     "http://127.0.0.1:8000/ask",
                #     json={
                #         "question": question
                #     },
                #     timeout=120
                # )
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={
                        "question": question
                    },
                    timeout=120
                )

                data = response.json()

                answer = data.get(
                    "answer",
                    "No answer returned."
                )

                route = data.get(
                    "route",
                    "unknown"
                )

                with st.container(border=True):

                    st.markdown("### 🤖 ValetAI")

                    st.write(answer)

                    if route == "sql":
                        st.success("🟢 SQL Analytics")

                    elif route == "rag":
                        st.info("🔵 RAG Search")

                    elif route == "hybrid":
                        st.warning("🟣 Hybrid Intelligence")

                    else:
                        st.error("Unknown Route")

                    with st.expander("🧠 AI Reasoning Path"):

                        if route == "sql":

                            st.markdown("""
                            ### SQL Analytics Flow

                            User Question

                            ⬇

                            SQL Agent

                            ⬇

                            SQLite Database

                            ⬇

                            LLM Explanation
                            """)

                        elif route == "rag":

                            st.markdown("""
                            ### Retrieval-Augmented Generation

                            User Question

                            ⬇

                            Vector Search

                            ⬇

                            ChromaDB

                            ⬇

                            LLM Reasoning
                            """)

                        elif route == "hybrid":

                            st.markdown("""
                            ### Hybrid Intelligence

                            User Question

                            ⬇

                            Router

                            ⬇

                            SQL Analytics

                            +

                            Vector Search

                            ⬇

                            Final AI Synthesis
                            """)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "route": route
                    }
                )

            except Exception as e:

                st.error(
                f"""
            Unable to connect to the backend.

            Please ensure:
            - FastAPI server is running
            - Endpoint: {BACKEND_URL}/ask

            Error:
            {e}
            """
            )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "ValetAI Enterprise Operations Intelligence • Built using FastAPI, LangGraph, SQLite, ChromaDB and Databricks"
)

# import streamlit as st
# import requests

# st.set_page_config(page_title="ValetAI Operations Assistant", page_icon="🗑️")

# with st.sidebar:
#     st.title("🤖 ValetAI")

#     st.markdown("### Operations Intelligence")

#     st.success("🟢 SQL Analytics")
#     st.info("🔵 RAG Search")
#     st.warning("🟣 Hybrid Intelligence")

#     st.divider()

#     st.markdown("### Sample Questions")

#     st.markdown("""
# - Which property has the highest missed pickups?
# - Why is Green Oaks struggling?
# - Compare Green Oaks and Birchwood Commons.
# - Which property should management prioritize?
# - Generate an executive summary.
# """)

#     st.divider()

#     if st.button("🗑 Clear Chat"):
#         st.session_state.messages = []
#         st.rerun()

# st.title("🗑️ ValetAI Operations Assistant")
# st.caption("Ask about waste collection performance across Valet Living properties")

# # Keep conversation history across interactions
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display past messages
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.write(msg["content"])
#         if msg.get("route"):
#             st.caption(f"Routed to: {msg['route']}")

# # Input box at the bottom
# question = st.chat_input("Ask a question about property operations...")

# if question:
#     # Show the user's question immediately
#     st.session_state.messages.append({"role": "user", "content": question})
#     with st.chat_message("user"):
#         st.write(question)

#     # Call your existing FastAPI backend
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 response = requests.post(
#                     "http://127.0.0.1:8000/ask",
#                     json={"question": question},
#                     timeout=60
#                 )
#                 data = response.json()
#                 answer = data.get("answer", "No answer returned.")
#                 route = data.get("route", "unknown")

#                 st.write(answer)
#                 st.caption(f"Routed to: {route}")

#                 st.session_state.messages.append({
#                     "role": "assistant",
#                     "content": answer,
#                     "route": route
#                 })
#             except Exception as e:
#                 st.error(f"Could not reach the backend: {e}")