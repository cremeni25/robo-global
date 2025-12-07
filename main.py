from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase_client import get_supabase

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação de produtos usando Supabase.",
    version="2.0.0"
)

# ------------------------------------------------------------
# MODELO DO BODY DO /atualizar
# ------------------------------------------------------------
class AtualizarPayload(BaseModel):
    id_produto: str
    metrica: str
    valor: float


# ------------------------------------------------------------
# /status
# ------------------------------------------------------------
@app.get("/status")
def status():
    return {"status": "OK", "supabase": "conectado"}


# ------------------------------------------------------------
# /produtos
# ------------------------------------------------------------
@app.get("/produtos")
def listar_produtos():
    try:
        supabase = get_supabase()
        res = supabase.table("produtos").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar produtos: {e}")


# ------------------------------------------------------------
# Função interna para salvar na tabela metrica_historica
# ------------------------------------------------------------
def salvar_metrica_historica(id_produto: str, metrica: str, valor: float):
    supabase = get_supabase()

    data = {
        "id_produto": id_produto,
        "metrica": metrica,
        "valor": valor
    }

    return supabase.table("metrica_historica").insert(data).execute()


# ------------------------------------------------------------
# /atualizar
# ------------------------------------------------------------
@app.post("/atualizar")
def atualizar_metrica(payload: AtualizarPayload):
    try:
        salvar_metrica_historica(payload.id_produto, payload.metrica, payload.valor)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar: {e}")


# ------------------------------------------------------------
# /pontuacao
# ------------------------------------------------------------
@app.get("/pontuacao")
def li
