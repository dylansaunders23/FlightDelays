import pandas as pd
import sqlite3

df = pd.read_csv('opsnet.csv')
df.columns= [str(col).strip().replace('\n', ' ') for col in df.columns] # clean col names

# Drop rows that are entirely blank
df.dropna(how='all', inplace=True)

if 'Date' in df.columns: #convert date to datetime
    df['Date']= pd.to_datetime(df['Date'], errors='coerce')

print(df.head())
print(df.columns)
print(df.dtypes)
print(df.shape)
print(df.describe())

conn = sqlite3.connect('opsnet_data.db')
df.to_sql('opsnet_table', conn, if_exists='replace', index=False)
conn.close()