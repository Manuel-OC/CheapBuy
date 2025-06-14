import pandas as pd
from supabase import create_client, Client
import os

#Conecto con Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "producto"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#Borro todo lo que hay en la tabla
supabase.table(TABLE_NAME).delete().neq("idproducto", 0).execute()

#Cargo el csv
df = pd.read_csv("cheapbuy.csv", delimiter=";")
df_clean = df.dropna()
data = df_clean.to_dict(orient="records")

#Importo el csv a la tabla
res = supabase.table(TABLE_NAME).insert(data).execute()

print("BASE DE DATOS ACTUALIZADA!")
