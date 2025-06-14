import pandas as pd
from supabase import create_client, Client

#Conecto con Supabase
SUPABASE_URL = "https://rmkfdfyhfjnxmxqwfcai.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJta2ZkZnloZmpueG14cXdmY2FpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTMyMjE3OSwiZXhwIjoyMDY0ODk4MTc5fQ.-O5oDD8IIbMNLFlOpts4qcU_RBKMkR7AxA-stESWLy0"
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
