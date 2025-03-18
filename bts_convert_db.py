import pandas as pd
import sqlite3 
import os

bts_data_path = os.path.abspath("./bts_data")
sqlite_db_path = os.path.abspath("./bts_data/bts_data.db")

df_list = []

for filename in os.listdir(bts_data_path):
    if filename.endswith(".csv"):
        df = pd.read_csv(os.path.join(bts_data_path, filename))
        df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]

conn = sqlite3.connect(sqlite_db_path)
df.to_sql('bts_data', conn, if_exists='replace', index=False)

conn.commit()
conn.close()

print(f"Saved BTS data to {sqlite_db_path}")
print(df.head())