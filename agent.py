# import json
# # 假設你使用 OpenAI 或 Anthropic，這裡以虛擬代碼表示
# def get_intent_planner(user_query: str):
#     """
#     扮演 Planner，決定要使用的工具與參數。
#     """
#     system_prompt = """
#     你是一個企業文件助手。請分析使用者問題並輸出 JSON。
#     工具說明：
#     - 'keyword_search': 查詢具體事件或專有名詞。參數為 'keyword'。
#     - 'temporal_summary': 查詢特定時間區間（年或月）。參數格式為 'YYYY' 或 'YYYY-MM'。
    
#     範例輸出：{"tool": "temporal_summary", "parameter": "2014-10"}
#     """
    
#     # 這裡實作 LLM 調用邏輯
#     # response = llm.chat(system_prompt, user_query)
#     # 模擬 LLM 回傳結果
#     if "2014" in user_query:
#         return {"tool": "temporal_summary", "parameter": "2014-10"}
#     return {"tool": "keyword_search", "parameter": user_query}

import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv() # 讀取 .env

def get_intent_planner(user_query: str):
    # 初始化 Groq 或 OpenAI 客戶端 (確保環境變數已載入)
    client = OpenAI(
        api_key=os.getenv("API_KEY"), 
        base_url="https://api.groq.com/openai/v1"
    )

    # 只提年
    # system_prompt = """
    # 你是一個企業文件助手。請分析使用者問題並輸出 JSON。
    # 請從問題中提取「關鍵字 (keyword)」與「時間區間 (date)」。

    # 輸出格式：
    # {"keyword": "電子書", "date": "2001"} 
    # (若無日期則 date 為 null，若無關鍵字則 keyword 為 null)
    # """
# 出YYY-MM-DD
    system_prompt = """
    你是一個文件檢索助手。請將使用者的問題拆解為 JSON 格式。
    1. date: 請統一轉換為 'YYYY-MM-DD' 格式。
    - 如果只提到年份，輸出 '2001'。
    - 如果提到月份，輸出 '2001-07'。
    - 如果提到具體日子，輸出 '2001-07-01'。
    2. keyword: 核心事件關鍵字。

    範例問題：2001年7月1日電子書的新聞
    範例輸出：{"date": "2001-07-01", "keyword": "電子書"}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant", # 或你使用的模型
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        response_format={"type": "json_object"} # 強制輸出 JSON
    )
    
    # 修改 return 邏輯，確保回應符合新結構
    return json.loads(response.choices[0].message.content)