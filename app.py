from fastapi import FastAPI
from pydantic import BaseModel
from main import app as graph_app, langfuse_handler

api = FastAPI(title="ValetAI Operations Assistant")

from fastapi.middleware.cors import CORSMiddleware

api = FastAPI(title="ValetAI Operations Assistant")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

# @api.post("/ask")
# def ask_question(request: QuestionRequest):
#     result = graph_app.invoke(
#         {"question": request.question},
#         config={"callbacks": [langfuse_handler]}
#     )
#     return {
#         "question": request.question,
#         "route": result.get("route"),
#         "answer": result["final_answer"]
#     }

@api.post("/ask")
def ask_question(request: QuestionRequest):

    print("Received question:", request.question)

    # result = graph_app.invoke(
    #     {"question": request.question}
    # )

    # print("Graph execution completed")

    return {
        "question": request.question,
        "route": "test",
        "answer": "Backend is working"
    }

@api.get("/")
def health_check():
    return {"status": "ValetAI is running"}