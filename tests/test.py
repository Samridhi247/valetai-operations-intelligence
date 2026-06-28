# import sqlite3
# conn = sqlite3.connect("data/valetai.db")
# cursor = conn.execute("PRAGMA table_info(property_metrics)")
# for row in cursor.fetchall():
#     print(row)
# conn.close()

# import chromadb
# client = chromadb.PersistentClient(path="data/chroma_db")
# collection = client.get_or_create_collection("operational_notes")

# results = collection.query(query_texts=["reasons for missed pickups across properties"], n_results=20)
# for note, meta in zip(results["documents"][0], results["metadatas"][0]):
#     print(f"[{meta['property_name']} - {meta['issue_type']}] {note}")

# import pandas as pd
# df = pd.read_csv('data/silver_operational_notes.csv')
# print(df['note_text'].nunique(), 'unique notes out of', len(df))
# print(df.groupby('property_name')['issue_type'].value_counts())

# import sqlite3

# conn = sqlite3.connect("data/valetai.db")   # same DB your project uses
# cursor = conn.cursor()

# # Show all tables
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print("Tables:")
# print(cursor.fetchall())

# print("\n------------------------")

# # Replace this with your table name
# cursor.execute("PRAGMA table_info(property_performance);")
# print("Columns:")
# for row in cursor.fetchall():
#     print(row)

# conn.close()

# # import sqlite3

# # conn = sqlite3.connect("data/valetai.db")
# # cursor = conn.cursor()

# # cursor.execute("""
# # SELECT
# # property_name,
# # avg_completion_time,
# # typeof(avg_completion_time)
# # FROM property_metrics
# # LIMIT 5;
# # """)

# # for row in cursor.fetchall():
# #     print(row)

# # conn.close()

# import sqlite3

# conn = sqlite3.connect("data/valetai.db") 
# cursor = conn.cursor()

# # List all tables
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# for (table_name,) in tables:
#     print(f"\n===== {table_name} =====")
#     cursor.execute(f"PRAGMA table_info({table_name});")
#     columns = cursor.fetchall()

#     for col in columns:
#         print(col)

# conn.close()

# import sqlite3

# conn = sqlite3.connect("data/valetai.db")
# cursor = conn.cursor()

# cursor.execute("""
# SELECT
#     property_name,
#     avg_completion_minutes,
#     typeof(avg_completion_minutes)
# FROM property_metrics
# WHERE property_name='Green Oaks';
# """)

# print(cursor.fetchall())

# conn.close()

# import sqlite3

# conn = sqlite3.connect("data/valetai.db")
# cur = conn.cursor()

# cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cur.fetchall())

import sqlite3

conn = sqlite3.connect("data/valetai.db")
print(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print(conn.execute("SELECT COUNT(*) FROM property_metrics").fetchone())
print(conn.execute("SELECT COUNT(*) FROM waste_logs").fetchone())