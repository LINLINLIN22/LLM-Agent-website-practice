import os
import chromadb
from chromadb.utils import embedding_functions

# 1. 初始化 ChromaDB (對應第 9 週：向量資料庫系統) [cite: 63]
# 設定資料持久化路徑，這樣資料才不會因為程式關閉而消失
client = chromadb.PersistentClient(path="./my_enterprise_db")

# 使用開源的 Embedding 模型 (模擬第 9 週的 Embedding 過程) [cite: 64]
default_ef = embedding_functions.DefaultEmbeddingFunction()

# 建立或取得 Collection (類似資料表)
collection = client.get_or_create_collection(
    name="daily_reports", 
    embedding_function=default_ef
)

def sync_txt_files(folder_path="./docs"):
    # 2. 取得目前已存入資料庫的檔案清單 (Metadata 檢查) [cite: 27]
    # 我們透過 metadata 中的 'source' 標籤來比對
    existing_metadatas = collection.get(include=['metadatas'])['metadatas']
    processed_files = {m['source'] for m in existing_metadatas}

    # 3. 掃描資料夾中的新檔案 (對應第 5 週：ETL Pipeline) 
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    new_files = [f for f in all_files if f not in processed_files]

    if not new_files:
        print("所有檔案皆已同步，無需處理。")
        return

    for file_name in new_files:
        print(f"\r正在處理新檔案: {file_name}", end="")
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 實作 Chunking (對應第 9 週：RAG pipeline:chunking) 
            # 小型專案簡單處理：每 500 字切一塊
            chunk_size = 200
            chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
            
            # 準備存入向量庫
            ids = [f"{file_name}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": file_name, "date": file_name.replace('.txt', '')} for _ in chunks]
            
            # 4. 存入向量資料庫 (Indexing) 
            collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
    print(f"同步完成，共新增 {len(new_files)} 個檔案。")


def smart_retrieval(decision):
    if decision['tool'] == "temporal_summary":
        # 直接利用 Metadata 進行時間過濾
        # 這對應課綱第 9 週：使用向量資料庫的 Filter 功能
        results = collection.get(
            where={"date": {"$sep_start": decision['parameter']}} 
        )
    else:
        # 關鍵字向量搜尋
        results = collection.query(
            query_texts=[decision['parameter']],
            n_results=3
        )
    return results['documents']

# 執行同步
sync_txt_files()