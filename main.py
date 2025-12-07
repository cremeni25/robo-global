from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase_client import get_supabase

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos usando Supabase.",
    version="1.0.0"
)

# ----- MODELO DO BODY -----
class AtualizarPayload(BaseModel):
    id_produto: str
    metrica: str
    valor: float


# ----- ENDPOINT STATUS -----
@app.get("/status")
def status():
    return {"status": "ok"}


# ----- LISTAR PRODUTOS -----
@app.get("/produtos")
def listar_produtos():
    supabase = get_supabase()
    res = supabase.table("produtos").select("*").execute()
    return res.data


# ----- SALVAR NA TABELA CORRETA -----
def salvar_metrica_historica(id_produto: str, metrica: str, valor: float):
    supabase = get_supabase()

    data = {
        "id_produto": id_produto,
        "métrica": metrica,   # nome da COLUNA exatamente como está no Supabase
        "valor": valor
    }

    re
