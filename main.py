from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from supabase import create_client, Client
import os
from fastapi.middleware.cors import CORSMiddleware

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FRONTEND = od.getenv("FRONTEND")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:81"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductosRequest(BaseModel):
    nombres: List[str]
    usar_precio_unitario: bool = False
    supermercados: Optional[List[int]] = None  # e.g. [1, 2]

@app.post("/buscar")
async def buscar_productos(request: ProductosRequest) -> List[Dict]:
    resultados = []

    campo_precio = "precioporunidadproducto" if request.usar_precio_unitario else "precioproducto"

    for termino in request.nombres:
        q = supabase.table("producto") \
            .select(f"idproducto,nombreproducto,{campo_precio},supermercado(nombresupermercado)") \
            .ilike("nombreproducto", f"{termino} %")

        if request.supermercados:
            q = q.in_("idsupermercado", request.supermercados)

        q = q.order(campo_precio, desc=False).limit(1)
        response = q.execute()

        if response.data:
            p = response.data[0]
            resultados.append({
                "nombre": p["nombreproducto"],
                "precio": p[campo_precio],
                "supermercado": p["supermercado"]["nombresupermercado"]
            })
        else:
            resultados.append({
                "nombre": None,
                "precio": None,
                "supermercado": None,
                "error": f"No se encontró ningún producto que contenga: {termino}"
            })

    return resultados

