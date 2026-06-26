import pandas as pd
import sqlite3

conn = sqlite3.connect("data/valetai.db")

df_metrics = pd.read_csv("data/gold_property_metrics.csv")
df_logs = pd.read_csv("data/silver_waste_logs.csv")

df_metrics.to_sql("property_metrics", conn, if_exists="replace", index=False)
df_logs.to_sql("waste_logs", conn, if_exists="replace", index=False)

result = pd.read_sql("SELECT * FROM property_metrics ORDER BY missed_pickup_rate DESC LIMIT 3", conn)
print(result)

conn.close()