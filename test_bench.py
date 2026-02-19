# problem: 好像測不準
import json
from agent import get_intent_planner
from tools import keyword_search, temporal_summary
# 假設你已經加入了 hybrid_search 函數到 tools.py
# from tools import hybrid_search 

def run_test_case(test_name, query, expected_tool=None):
    print(f"=== [測試案例] {test_name} ===")
    print(f"使用者輸入: {query}")
    
    # 1. 測試 Agent 解析
    try:
        decision = get_intent_planner(query)
        tool_name = decision.get('tool') or decision.get('keyword') # 根據你 agent 的 JSON 結構調整
        print(f"調用工具: {tool_name}")
        print(f"1. Agent 解析結果: {json.dumps(decision, ensure_ascii=False)}")
    except Exception as e:
        print(f"1. Agent 解析失敗: {e}")
        return

    # 2. 測試檢索 (Tools)
    context = ""
    # 這裡模擬 main.py 的邏輯判斷
    # 範例使用你目前的 tools 邏輯
    if "2001" in query and "電子書" in query:
        # 如果你還沒實作 hybrid_search，這裡會跑原本有問題的邏輯
        # context = hybrid_search("電子書", "2001") 
        context = temporal_summary("2001") # 目前暫代
    elif "2001" in query:
        context = temporal_summary("2001")
    else:
        context = keyword_search(query)

    print(f"2. 檢索結果長度: {len(context)}")
    if len(context) > 0:
        print(f"   預覽內容: {context[:100]}...")
    else:
        print("   警告: 檢索結果為空！")

    # 3. 嚴格度判定 (測試是否會胡說八道)
    # 此處可視需求呼叫 LLM 進行最後總結測試
    print("="*50 + "\n")

# --- 開始測試 ---

# 測試 1: 複合查詢 (年代 + 關鍵字)
# run_test_case("複合查詢測試", "2001年關於電子書的事")

# 測試 2: 精確日期測試
run_test_case("精確日期測試", "2001年7月2日發生的事")

# 測試 3: 邊界測試 (資料庫應該沒有的內容)
# run_test_case("不存在的資料測試", "2099年火星移民計畫")

# 測試 4: 純語意測試
# run_test_case("純關鍵字測試", "電子商務的發展趨勢")