#%%
# ====================================================
# Agente 2 - Recuperador/Analista ESG (Classe Unificada)
# ====================================================
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
#%%
class AgenteRetrieverESG:
    def __init__(self, db_path):
        self.db_path = db_path

    # ---------------------------
    # Função auxiliar: gravidade IBAMA
    # ---------------------------
    def _gravidade_ibama(self, descricao):
        desc = descricao.lower()
        palavras_alta = ["embargo", "desmatamento", "queimada", "poluição", "vazamento", "contaminação"]
        if any(p in desc for p in palavras_alta):
            return "Alta"
        
        palavras_baixa = ["advertência", "não conformidade administrativa"]
        if any(p in desc for p in palavras_baixa):
            return "Baixa"
        
        return "Média"

    # ---------------------------
    # Eventos IBAMA
    # ---------------------------
    def eventos_ibama(self, cpf_cnpj):
        eventos = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # --- Autos de Infração ---
        try:
            query_autos = """
                SELECT "DAT_HORA_AUTO_INFRACAO" as data,
                       "DES_AUTO_INFRACAO" as descricao,
                       "NOME_INFRATOR" as nome_pessoa,
                       "CPF_CNPJ_INFRATOR" as cpf_cnpj_pessoa,
                       "VAL_AUTO_INFRACAO" as valor_multa
                FROM autos_infracao
                WHERE CPF_CNPJ_INFRATOR = ?
            """
            cursor.execute(query_autos, (cpf_cnpj,))
            rows = cursor.fetchall()
            for r in rows:
                eventos.append({
                    "data": r[0],
                    "cpf_cnpj": r[3],
                    "descricao": r[1],
                    "valor": r[4],
                    "pilar": "Ambiental",
                    "gravidade": self._gravidade_ibama(r[1]),
                    "fonte": "Auto de Infração (IBAMA)"
                })
        except Exception as e:
            print("⚠️ Erro ao buscar autos de infração:", e)

        # --- Termos de Embargo ---
        try:
            query_embargos = """
                SELECT "DAT_EMBARGO" as data,
                       "DES_TAD" as descricao,
                       "NOME_EMBARGADO" as nome_pessoa,
                       "CPF_CNPJ_EMBARGADO" as cpf_cnpj
                FROM embargos
                WHERE CPF_CNPJ_EMBARGADO = ?
            """
            cursor.execute(query_embargos, (cpf_cnpj,))
            rows = cursor.fetchall()
            for r in rows:
                eventos.append({
                    "data": r[0],
                    "cpf_cnpj": r[3],
                    "descricao": r[1],
                    "pilar": "Ambiental",
                    "gravidade": "Alta",
                    "fonte": "Termo de Embargo (IBAMA)"
                })
        except Exception as e:
            print("⚠️ Erro ao buscar termos de embargo:", e)

        conn.close()
        return eventos

    # ---------------------------
    # Eventos Trabalho Escravo
    # ---------------------------
    def eventos_trabalho_escravo(self, cpf_cnpj):
        eventos = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # calcula a data limite (últimos 24 meses)
            limite = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

            query = """
                SELECT cnpjcpf, empregador, inclusao_no_cadastro_de_empregadores
                FROM trabalho_escravo
                WHERE cnpjcpf = ?
                  AND DATE(substr(inclusao_no_cadastro_de_empregadores, 7, 4) || '-' || 
                           substr(inclusao_no_cadastro_de_empregadores, 4, 2) || '-' || 
                           substr(inclusao_no_cadastro_de_empregadores, 1, 2)) >= DATE(?)
            """
            cursor.execute(query, (cpf_cnpj, limite))
            rows = cursor.fetchall()

            for r in rows:
                eventos.append({
                    "data": r[2],
                    "cpf_cnpj": r[0],
                    "descricao": f"Empregador {r[1]} incluído na lista de trabalho escravo",
                    "pilar": "Social",
                    "gravidade": "Alta",
                    "fonte": "Lista de Trabalho Escravo (MTE)"
                })

        except Exception as e:
            print("⚠️ Erro ao buscar lista de trabalho escravo:", e)

        conn.close()
        return eventos

    # ---------------------------
    # Eventos CNEP
    # ---------------------------
    def eventos_cnep(self, cpf_cnpj):
        eventos = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # --- Sanções ---
        try:
            query_sancoes = """
                SELECT dataInicioSancao as data,
                       fundamentacao_json as descricao,
                       sancionado_nome as nome_pessoa,
                       sancionado_codigoFormatado as cpf_cnpj_pessoa,
                       valorMulta as valor_multa
                FROM sancoes_cnep
                WHERE sancionado_codigoFormatado = ?
            """
            cursor.execute(query_sancoes, (cpf_cnpj,))
            rows = cursor.fetchall()
            for r in rows:
                eventos.append({
                    "data": r[0],
                    "cpf_cnpj": r[3],
                    "descricao": r[1],
                    "valor": r[4],
                    "pilar": "Governança",
                    "gravidade": "Alta",
                    "fonte": "CNEP"
                })
        except Exception as e:
            print("⚠️ Erro ao buscar sanções:", e)

        conn.close()
        return eventos

    # ---------------------------
    # Eventos CEIS
    # ---------------------------
    def eventos_ceis(self, cpf_cnpj):
        eventos = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # --- Sanções ---
        try:
            query_sancoes = """
                SELECT dataInicioSancao as data,
                       fundamentacao_json as descricao,
                       sancionado_nome as nome_pessoa,
                       sancionado_codigoFormatado as cpf_cnpj_pessoa
                       
                FROM sancoes_ceis
                WHERE sancionado_codigoFormatado = ?
            """
            cursor.execute(query_sancoes, (cpf_cnpj,))
            rows = cursor.fetchall()
            for r in rows:
                eventos.append({
                    "data": r[0],
                    "cpf_cnpj": r[3],
                    "descricao": r[1],
                    #"valor": r[4],
                    "pilar": "Governança",
                    #"gravidade": "Alta",
                    "fonte": "CEIS"
                })
        except Exception as e:
            print("⚠️ Erro ao buscar sanções:", e)

        conn.close()
        return eventos
    # ---------------------------
    # Consulta Unificada
    # ---------------------------
    def consultar_eventos(self, cpf_cnpj):
        eventos = []
        eventos.extend(self.eventos_ibama(cpf_cnpj))
        eventos.extend(self.eventos_trabalho_escravo(cpf_cnpj))
        eventos.extend(self.eventos_cnep(cpf_cnpj))
        eventos.extend(self.eventos_ceis(cpf_cnpj))
        return eventos


#%%
# === Exemplo de uso ===

if __name__ == "__main__":
    CPF_CNPJ_PESQUISADO = "07999476609" # exemplo "24777079000120" "53162923000106"  "63620189234" #"09568883215" #"33350604900" #"05656434109"

    db_path = Path(__file__).parent.parent.parent / "ingestion" / "sqlite_db" / "advisor_esg_silver.db"

    retriever = AgenteRetrieverESG(db_path)
    eventos = retriever.consultar_eventos(CPF_CNPJ_PESQUISADO)

    print(f"🔎 {len(eventos)} eventos encontrados para {CPF_CNPJ_PESQUISADO}")
    for e in eventos:
        print(e)