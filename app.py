from fastapi import FastAPI
from pydantic import BaseModel
# from main import app as graph_app, langfuse_handler
print("======== Importing main.py ========")

from main import app as graph_app, langfuse_handler

print("======== Imported main.py successfully ========")

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

# @api.post("/ask")
# def ask_question(request: QuestionRequest):

#     print("STEP 1")

#     result = graph_app.invoke(
#         {"question": request.question}
#     )

#     print("STEP 2")

#     return {
#         "question": request.question,
#         "route": result.get("route"),
#         "answer": result["final_answer"]
#     }

# @api.post("/ask")
# def ask_question(request: QuestionRequest):

#     return {
#         "question": request.question,
#         "route": "sql",
#         "answer": "Reached app.py successfully"
#     }

#     # Keep this below for now (it won't execute)
#     result = graph_app.invoke(
#         {"question": request.question}
#     )

@api.post("/ask")
def ask_question(request: QuestionRequest):

    print("STEP 1: Request received")

    # result = graph_app.invoke(
    #     {"question": request.question}
    # )
    result = graph_app.invoke(
        {"question": request.question},
        config={
            "recursion_limit": 15
            # "recursion_limit": 4
        }
    )

    print("STEP 2: Graph finished")

    return {
        "question": request.question,
        "route": result.get("route"),
        "answer": result["final_answer"]
    }

@api.get("/")
def health_check():
    return {"status": "ValetAI is running"}