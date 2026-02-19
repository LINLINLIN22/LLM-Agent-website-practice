# count_data.py
import chromadb

client = chromadb.PersistentClient(path="./my_enterprise_db")
collection = client.get_collection(name="daily_reports")

# 獲取所有 metadata
all_meta = collection.get(include=['metadatas'])['metadatas']
dates = [m.get('date')[:7] for m in all_meta]

# # 計算每個年份出現次數
# from collections import Counter
# print(Counter(dates))

# 排序版
from collections import Counter
counter = Counter(dates)
for ym, count in sorted(counter.items()):
    print(ym, count)
