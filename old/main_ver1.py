from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent import get_intent_planner
import asyncio

app = FastAPI()

# async def mock_rag_engine(decision):
#     # 這裡未來會接上你寫的 ChromaDB 檢索邏輯 (tools.py)
#     tool = decision['tool']
#     param = decision['parameter']
    
#     yield f"data: [系統訊息] 啟動工具: {tool}，參數: {param}\n\n"
#     await asyncio.sleep(1)
    
#     full_text = f"根據您的要求，在 {param} 的文件中找到以下內容：..."
#     for char in full_text:
#         yield f"data: {char}\n\n"
#         await asyncio.sleep(0.05)
from tools import keyword_search, temporal_summary
async def rag_engine(decision):
    if decision['tool'] == "keyword_search":
        context = keyword_search(decision['parameter'])
    elif decision['tool'] == "temporal_summary":
        context = temporal_summary(decision['parameter'])

@app.get("/chat")
async def chat(query: str):
    # 1. 意圖判斷 (Planner)
    decision = get_intent_planner(query)
    
    # 2. 根據判斷結果，啟動 RAG 引擎與 Streaming
    return StreamingResponse(
        rag_engine(decision), 
        media_type="text/event-stream"
    )