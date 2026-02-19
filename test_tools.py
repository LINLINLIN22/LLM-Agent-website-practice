from tools import keyword_search, temporal_summary

def test_retrieval():
    print("--- 測試關鍵字搜尋 ---")
    res1 = keyword_search("華文網路世紀高峰論壇")
    print(res1)
    
    print("\n--- 測試日期過濾 ---")
    # 測試你提供的 2014-10-26 資料
    res2 = temporal_summary("2014-10")
    print(res2)

if __name__ == "__main__":
    test_retrieval()