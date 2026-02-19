import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from tools import keyword_search, temporal_summary,hybrid_search
from agent import get_intent_planner
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware  # [NEW] 引入 CORS 套件
import re

load_dotenv() # 讀取 .env


app = FastAPI()
# [NEW] 設定 CORS，允許所有來源 (為了開發方便，我們先全開)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許任何網址呼叫這個 API
    allow_credentials=True,
    allow_methods=["*"],  # 允許任何方法 (GET, POST...)
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

# test小記錄
record = ["hybrid_search","temporal_summary","keyword_search","未知無法調用工具"]


async def generate_response(query: str):
    try:
        # 1. 立即吐出第一個字，維持連線
        yield "data: [連線成功] 正在啟動分析引擎...\n\n"
        await asyncio.sleep(0.1) 

        # 2. 意圖判斷 (Agent Planning)
        yield "data: [思考] 正在判斷查詢意圖...\n\n"
        # 確保 get_intent_planner 不會卡太久
        # decision = get_intent_planner(query)

# ... 在 generate_response 函式內 ...

        # main.py 中的 generate_response 函式片段
        # decision = get_intent_planner(query)
        # keyword = decision.get('keyword')
        # date_param = decision.get('date')

        # if date_param and keyword:
        #     yield f"data: [執行] 正在檢索 {date_param} 年關於「{keyword}」的資料...\n\n"
        #     context = hybrid_search(keyword, date_param)
        #     tool_name = record[0]
        # elif date_param:
        #     yield f"data: [執行] 正在整理 {date_param} 年的時序摘要...\n\n"
        #     context = temporal_summary(date_param)
        #     tool_name = record[1]
        # else:
        #     yield f"data: [執行] 正在進行全域語意搜尋：{keyword}...\n\n"
        #     context = keyword_search(keyword)
        #     tool_name = record[2]
        # # main.py
        decision = get_intent_planner(query) # 取得 JSON
        kw = decision.get('keyword')
        dt = decision.get('date')

        if dt and kw:
            # 同時有日期與關鍵字：最精準
            context = hybrid_search(kw, dt)
            tool_name = record[0]
            yield f"data: [執行] 正在檢索 {dt} 年關於「{kw}」的資料...\n\n"
        elif dt:
            # 只有日期：跑原本的 temporal_summary
            context = temporal_summary(dt)
            tool_name = record[1]
            yield f"data: [執行] 正在整理 {dt} 的時序摘要...\n\n"
        else:
            # 只有關鍵字：跑原本的 keyword_search
            context = keyword_search(kw)
            tool_name = record[2]
            yield f"data: [執行] 正在進行全域語意搜尋：{kw}...\n\n"
            
            

        # 【關鍵檢查點】
        print(f"--- 執行工具: {tool_name}, 結果長度: {len(context)} ---")
        if len(context) < 10:
            print(f"警告：檢索到的內容太少或為空！內容為: {context}")
            yield "data: [錯誤] 資料庫中找不到相關文件。\n\n"
            return

        # 4. 進入模型生成
        yield "data: [總結] 正在整理最終回答...\n\n"
        
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "你是一個專業資料整理助手，請文件內的資料回答，不得引用外部來源。"},
                {"role": "user", "content": f"資料：{context}\n問題：{query}"}
            ],
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"
        
        # 5. 發送結束訊號
        yield "data: [DONE]\n\n"

    except asyncio.CancelledError:
        print("客戶端已斷開連線")
@app.get("/chat")
async def chat(query: str):
    return StreamingResponse(generate_response(query), media_type="text/event-stream")