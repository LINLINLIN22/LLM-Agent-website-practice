import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from tools import keyword_search, temporal_summary
import asyncio
import os
from dotenv import load_dotenv

load_dotenv() # 讀取 .env

app = FastAPI()

# 建議將 API KEY 存在環境變數
client = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://api.groq.com/openai/v1" )

# async def generate_response(query: str):
#     # 1. 意圖判斷 (暫時手動邏輯，確保 demo 成功)
#     # 若 query 包含數字日期，使用 temporal_summary；否則用關鍵字搜尋
#     if any(char.isdigit() for char in query):
#         # 範例：從 "2014年10月" 提取出 "2014-10"
#         # 這裡簡單處理，實務上會由 agent.py 的 Planner 處理
#         context = temporal_summary("2014-10")
#         tool_used = "時間總結工具 (2014-10)"
#     else:
#         context = keyword_search(query)
#         tool_used = "關鍵字搜尋工具"

#     yield f"data: [系統訊息] 已根據您的問題啟動 {tool_used}...\n\n"

#     # 2. 構造企業級 RAG Prompt
#     messages = [
#         {"role": "system", "content": "你是一個專業的文件分析官。請僅根據提供的『參考資料』回答問題。若資料中未提及，請誠實回答不知道。"},
#         {"role": "user", "content": f"參考資料：\n{context}\n\n問題：{query}"}
#     ]

#     # 3. 開啟 OpenAI Streaming 模式
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo", # 或 gpt-4-turbo
#         messages=messages,
#         stream=True
#     )

#     # 4. 逐塊 (Chunk) 解析並傳送
#     for chunk in response:
#         if chunk.choices[0].delta.content:
#             content = chunk.choices[0].delta.content
#             # 將內容封裝成 Server-Sent Events (SSE) 格式
#             yield f"data: {content}\n\n"
#             # 加上微小延遲讓串流感更自然 (可選)
#             await asyncio.sleep(0.01)

async def generate_response(query: str):
    # 1. 檢索階段 (目前手動邏輯，等下接 Agent)
    date_param = "2014-10" # 假設從 query 提取
    context = temporal_summary(date_prefix=date_param)
    
    yield f"data: [系統] 已讀取 {date_param} 的相關文件，正在生成總結...\n\n"

    # 2. 構造對話與 Streaming
    # 這裡使用 OpenAI SDK 作為範例
    response = client.chat.completions.create(
        model="gpt-4o", # 或 gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "你是一個企業分析助手。請根據『參考資料』回答，並標註日期。"},
            {"role": "user", "content": f"參考資料：\n{context}\n\n問題：{query}"}
        ],
        stream=True
    )

    # 3. 將 LLM 的碎片即時傳送回瀏覽器
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            # 必須符合 SSE 格式：data: 內容\n\n
            yield f"data: {content}\n\n"

@app.get("/chat")
async def chat(query: str):
    return StreamingResponse(generate_response(query), media_type="text/event-stream")