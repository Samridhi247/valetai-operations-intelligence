# 🚀 ValetAI – Multi-Agent Operations Intelligence Platform

> An end-to-end Agentic AI platform that combines Data Engineering, SQL Analytics, Retrieval-Augmented Generation (RAG), and Multi-Agent Orchestration to provide intelligent operational insights for business users.

---

## 📌 Overview

ValetAI is an enterprise-inspired AI Operations Intelligence platform designed to answer both structured and unstructured operational questions through natural language.

Traditional dashboards are capable of answering **what happened**, but they cannot explain **why it happened** or **what should be done next**.

ValetAI bridges this gap by combining:

- Structured operational analytics
- Semantic understanding of historical operational notes
- Multi-Agent AI orchestration
- Hybrid reasoning (SQL + RAG)
- Cloud deployment
- End-to-end observability

Users interact with the system through natural language while specialized AI agents collaborate behind the scenes to generate accurate and actionable business insights.

---

# 🎯 Problem Statement

Operational organizations generate two very different types of data.

### Structured Data
- Missed pickups
- Completion times
- Property metrics
- Route statistics
- Staffing metrics

Stored inside relational databases.

---

### Unstructured Data

- Technician notes
- Customer complaints
- Incident reports
- Historical observations
- Resolution logs

Stored as free-form text.

---

Traditional BI dashboards cannot combine both data sources effectively.

For example:

✅ "Which property has the highest missed pickups?"

can be answered using SQL.

But

❌ "Why is this property struggling?"

requires searching thousands of historical notes.

ValetAI solves this using a Hybrid AI architecture.

---

# ✨ Features

- Multi-Agent AI Architecture using LangGraph
- Intelligent Router Agent
- SQL Analytics Agent
- RAG Resolution Agent
- Hybrid SQL + RAG reasoning
- FastAPI backend
- Streamlit frontend
- ChromaDB Vector Database
- SQLite Analytics Database
- LangFuse Observability
- GitHub Actions CI/CD
- Azure App Service Deployment

---

# 🏗 System Architecture

```
                User
                  │
                  ▼
        Streamlit Frontend
                  │
                  ▼
          FastAPI Backend
                  │
                  ▼
          LangGraph Router
         ┌──────┼─────────┐
         │      │         │
         ▼      ▼         ▼
      SQL     RAG      Hybrid
      Agent   Agent    Workflow
         │      │
         ▼      ▼
     SQLite   ChromaDB
         │      │
         └──┬───┘
            ▼
     Response Synthesizer
            ▼
      Final Business Answer
```

---

# ⚙ Architecture Workflow

## Step 1 — Data Engineering

Operational datasets are prepared using Databricks-inspired Medallion architecture.

### Bronze Layer

- Raw operational CSV files
- Landing zone
- No transformations

---

### Silver Layer

Data cleaning using PySpark

- Remove duplicates
- Handle missing values
- Standardize formats
- Feature engineering

---

### Gold Layer

Analytics-ready datasets

Used by

- SQLite
- ChromaDB

---

## Step 2 — User Query

Users ask natural language questions like

> Which property should management prioritize and why?

---

## Step 3 — Router Agent

LangGraph first classifies the request into

- SQL
- RAG
- Hybrid

Example

Question

```
How many missed pickups occurred?
```

↓

SQL

---

Question

```
Why are pickups delayed?
```

↓

RAG

---

Question

```
Which property should management prioritize and why?
```

↓

Hybrid

---

## Step 4 — SQL Analyst Agent

Handles structured analytical questions.

Responsibilities

- Generate SQL queries
- Execute SQLite queries
- Return metrics
- Rankings
- Counts
- Percentages

Example

```
Top 5 properties
Average completion time
Highest missed pickups
```

---

## Step 5 — Resolution Agent (RAG)

Handles semantic questions.

Pipeline

User Question

↓

Embedding Generation

↓

Vector Similarity Search

↓

Retrieve Historical Notes

↓

LLM Summary

---

Example

```
Recurring staffing issues

Historical complaints

Operational recommendations
```

---

## Step 6 — Response Synthesizer

If both SQL and RAG execute

↓

Responses are merged into a structured business report.

Output Format

```
Primary Finding

Likely Cause

Recommended Actions

Summary
```

---

# 📊 Technology Stack

## Data Engineering

- Databricks (training workflow)
- PySpark
- SQLite

---

## AI & Agentic Framework

- LangGraph
- LangChain
- Groq LLM

---

## Vector Search

- ChromaDB
- Sentence Transformers

---

## Backend

- FastAPI

---

## Frontend

- Streamlit

---

## Observability

- LangFuse

---

## Deployment

- Azure App Service
- GitHub Actions
- Docker (containerized deployment)

---

# 📂 Project Structure

```
ValetAI
│
├── agents/
│   ├── analyst_agent.py
│   ├── router.py
│
├── rag/
│   ├── ingest.py
│   ├── resolution_agent.py
│   ├── vector_tool.py
│
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── chroma_db/
│   └── valetai.db
│
├── frontend/
│   └── frontend_app.py
│
├── main.py
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# 💬 Example Queries

### SQL

```
Which property has the highest missed pickups?
```

---

```
Show top 5 properties by completion time.
```

---

```
Average missed pickup rate.
```

---

### RAG

```
Why are complaints increasing?
```

---

```
Summarize recurring staffing issues.
```

---

```
Common historical operational challenges.
```

---

### Hybrid

```
Which property should management prioritize and why?
```

---

```
Which property is struggling the most and what should management do?
```

---

```
Give an executive summary of operations.
```

---

# 🚀 Local Setup

Clone repository

```bash
git clone <repository-url>

cd valetai
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run backend

```bash
uvicorn app:api --reload
```

Run frontend

```bash
streamlit run frontend/frontend_app.py
```

---

# ☁ Azure Deployment

The application is deployed on Azure App Service.

Deployment workflow

GitHub Push

↓

GitHub Actions

↓

Docker Build

↓

Azure App Service

↓

Automatic Deployment

---

# 📈 LangFuse Observability

Every request is traced.

Captured information includes

- Router decision
- Prompt execution
- Agent execution
- SQL queries
- RAG retrieval
- Token usage
- Latency
- Final response

This enables debugging and performance monitoring.

---

# 🔍 Future Improvements

Potential production enhancements include

- Authentication & RBAC
- Real-time data ingestion
- Databricks Delta Lake integration
- Azure AI Search
- PostgreSQL instead of SQLite
- Redis caching
- Kubernetes deployment
- Multi-tenant architecture
- Fine-tuned domain-specific LLM
- Agent memory
- Feedback learning loop

---

# 📚 Learning Outcomes

Through this project I gained practical experience in

- Data Engineering
- ETL Pipelines
- PySpark
- FastAPI
- Agentic AI
- LangGraph
- LangChain
- Retrieval-Augmented Generation
- Prompt Engineering
- ChromaDB
- Vector Search
- LangFuse Observability
- Azure Deployment
- GitHub Actions CI/CD

---

# 👩‍💻 Author

**Samridhi Sinha**

Associate Software Engineering Intern

Built as part of an enterprise AI Engineering internship focused on Data Engineering, Agentic AI, and Cloud Deployment.

---

# ⭐ Acknowledgements

This project was developed as part of an internship focused on modern enterprise technologies including:

- Data Engineering
- Agentic AI
- Retrieval-Augmented Generation
- Cloud Deployment
- AI Observability
- Multi-Agent Systems
