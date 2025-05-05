from typing import List

from vector_db.chroma_db import ChromaDB
from config import VECTOR_DB_DIR, TINYLLAMA_MODEL_PATH
from llama_cpp import Llama, ChatCompletionRequestSystemMessage, ChatCompletionRequestUserMessage, CreateChatCompletionResponse
from codebase_analyzer.embedder.codet5p_embedder import CodeT5pEmbedder
from pydantic import BaseModel

db = ChromaDB(persist_dir=VECTOR_DB_DIR / "clickhouse",
              collection_name="clickhouse_chunks")
llm = Llama(model_path=str(TINYLLAMA_MODEL_PATH), n_ctx=2048, n_threads=4)
embedder = CodeT5pEmbedder()


class Query(BaseModel):
    question: str


def query_rag(q: Query):
    embedding = embedder.embed(q.question)
    results = db.query(query_embedding=embedding, top_k=5)
    context = "\n\n".join(sum(results["documents"], []))
    messages = [
        ChatCompletionRequestSystemMessage({
            "role":
            "system",
            "content":
            "You are a coding assistant. Only answer based on the context provided. "
            "Do not invent or guess any information that is not in the context. "
            "If the answer is not in the context, respond with 'I cannot answer based on the provided information.'"
        }),
        ChatCompletionRequestUserMessage({
            "role":
            "user",
            "content":
            f"Context:\n{context}\n\nQ: {q.question}\nA:"
        })
    ]

    print("Messages:\n", messages)
    response = llm.create_chat_completion(messages=messages,
                                          max_tokens=256,
                                          temperature=0.7)

    if isinstance(response, dict):
        choices = response.get("choices", [])
        if choices and "message" in choices[0] and "content" in choices[0][
                "message"]:
            return {"answer": choices[0]["message"]["content"]}
        else:
            return {"answer": "[Error] Unexpected LLM response structure."}
    else:
        return {"answer": "[Error] LLM response is not a dictionary."}
