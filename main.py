from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase_client import get_supabase

app = FastAPI(
    title="Robô Global de Afiliados",
    description="API para ranking e pontuação usando Supabase.",
    version="3.0.0"
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
    supabase = get_supabase()
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
# Salva histórico de métricas
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
# (retorna todas as métricas cadastradas por produto)
# ------------------------------------------------------------
@app.get("/pontuacao")
def pontuacao():
    try:
        supabase = get_supabase()
        res = supabase.table("metrica_historica").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar pontuação: {e}")


# ------------------------------------------------------------
# /ranking — AGORA TOTALMENTE CORRIGIDO
# ------------------------------------------------------------
@app.get("/ranking")
def ranking():
    try:
        supabase = get_supabase()

        # CONSULTA segura usando a FUNCTION executar_query
        sql = """
            select json_agg(resultado)
            from (
                select 
                    p.id_produto,
                    p.nome,
                    sum(case when m.metrica = 'vendas' then m.valor else 0 end) as total_vendas,
                    sum(case when m.metrica = 'cliques' then m.valor else 0 end) as total_cliques,
                    sum(case when m.metrica = 'roi' then m.valor else 0 end) as total_roi,
                    sum(case when m.metrica = 'conversao' then m.valor else 0 end) as total_conversao
                from produtos p
                left join metrica_historica m on m.id_produto = p.id_produto
                group by p.id_produto, p.nome
                order by total_vendas desc
            ) resultado;
        """

        # AQUI está o segredo: enviamos o SQL como texto válido para a função executar_query
        response = supabase.rpc("executar_query", {"query": sql}).execute()

        return response.data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar ranking: {e}")


