import chromadb
from chromadb.utils import embedding_functions
import os

# 1. 初始化配置 (對應第 9 週：向量資料庫系統)
# client = chromadb.PersistentClient(path="./my_enterprise_db")
client = chromadb.PersistentClient(path="./200_db")
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_or_create_collection(
    name="daily_reports", 
    embedding_function=default_ef
)

# 2. 工具 A：關鍵字向量搜尋 (Keyword Search Tool)
def keyword_search(keyword: str, n_results: int = 3):
    """
    使用語意搜尋，找尋與關鍵字最相關的內容
    """
    results = collection.query(
        query_texts=[keyword],
        n_results=n_results
    )
    # 格式化回傳，方便 LLM 閱讀
    combined_docs = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        combined_docs.append(f"[{meta['date']}] {doc}")
    return "\n---\n".join(combined_docs)

# # 3. 工具 B：時間範圍過濾 (Temporal Summary Tool)
def temporal_summary(date_prefix: str):
    all_data = collection.get(include=['metadatas', 'documents'])
    documents = all_data['documents']
    metadatas = all_data['metadatas']
    
    filtered_docs = []
    current_length = 0
    # 設定一個上限，例如 5000 tokens (約 8000-10000 字)
    # 免費版 Groq 建議先設小一點，確保能跑通
    MAX_CHARS = 4000 

    for doc, meta in zip(documents, metadatas):
        if meta.get('date', '').startswith(date_prefix):
            content = f"日期: {meta['date']}\n內容: {doc}"
            print(content)
            if current_length + len(content) > MAX_CHARS:
                break
            filtered_docs.append(content)
            current_length += len(content)
            
    if not filtered_docs:
        return f"找不到 {date_prefix} 的相關記錄。"
        
    return "\n\n".join(filtered_docs)

def power_search(query_param: str):
    # 嘗試從參數提取日期 (例如把 "2012年12月" 轉為 "2012-12")
    import re
    date_match = re.search(r'(\d{4})[-年](\d{1,2})', query_param)
    
    if date_match:
        year, month = date_match.groups()
        formatted_date = f"{year}-{int(month):02d}"
        # 這就相當於你以前在「找 2012-12 的檔案」
        return temporal_summary(formatted_date) 
    else:
        # 如果沒日期，才跑語意搜尋
        return keyword_search(query_param)

# 修改 tools.py
# 取代 keyword_search
# def hybrid_search(keyword: str, date_prefix: str, n_results: int = 5):
#     """
#     先根據日期前綴 (如 '2001-07') 過濾 ID，再進行關鍵字語意搜尋
#     """
#     # 1. 抓取所有資料的 IDs 與 Metadatas
#     all_data = collection.get(include=['metadatas'])
#     ids = all_data['ids']
#     metadatas = all_data['metadatas']
    
#     # 2. 篩選出符合日期前綴的 IDs
#     # 例如：'2001-07' 會匹配 '2001-07-01', '2001-07-15' 等
#     target_ids = [
#         ids[i] for i, meta in enumerate(metadatas) 
#         if meta.get('date', '').startswith(date_prefix)
#     ]
    
#     if not target_ids:
#         return f"在資料庫中找不到日期為 {date_prefix} 的記錄。"

#     # 3. 在指定的 ID 範圍內進行語意搜尋
#     # ChromaDB 的 query 支援 ids 參數，能強制只搜尋這些文件
#     results = collection.query(
#         query_texts=[keyword],
#         n_results=min(n_results, len(target_ids)),
#         ids=target_ids
#     )
    
#     combined_docs = []
#     for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
#         combined_docs.append(f"[{meta['date']}] {doc}")
        
#     return "\n---\n".join(combined_docs)

# 含年月
def hybrid_search(keyword: str, date_prefix: str, n_results: int = 5):
    # 1. 先找出所有符合日期開頭的 ID
    all_data = collection.get(include=['metadatas'])
    ids = all_data['ids']
    metadatas = all_data['metadatas']
    
    # 只要資料庫的日期是以 date_prefix 開頭的都算 (支援 年、年月、年月日)
    target_ids = [
        ids[i] for i, meta in enumerate(metadatas) 
        if meta.get('date', '').startswith(date_prefix)
    ]
    
    if not target_ids:
        return f"找不到日期為 {date_prefix} 的相關資料。"

    # 2. 只在這些 ID 中進行語意搜尋
    results = collection.query(
        query_texts=[keyword],
        n_results=min(n_results, len(target_ids)),
        ids=target_ids
    )
    
    combined_docs = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        combined_docs.append(f"[{meta['date']}] {doc}")
        
    return "\n---\n".join(combined_docs)