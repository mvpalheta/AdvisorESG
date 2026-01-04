# ====================================================
# Agente Ingestor Dados IBAMA
# Camadas: RAW → BRONZE → SILVER
# ====================================================
import sqlite3
import pandas as pd
import requests
import zipfile
import re
import unicodedata
from io import BytesIO
from datetime import datetime
from ingestion_settings import Settings

# ========================
# Funções auxiliares
# ========================

def normalizar_colunas(colunas):
    """
    Remove acentos, espaços e coloca em UPPERCASE.
    """
    return [
        unicodedata.normalize("NFKD", col)
        .encode("ASCII", "ignore")
        .decode("utf-8")
        .replace(" ", "_")
        .upper()
        for col in colunas
    ]
# ========================
# Agente Raw
# ========================
class AgenteRawIBAMA:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.ano_atual = datetime.now().year

    def _criar_tabela(self, tabela, df):
        colunas = ", ".join([f'"{col}" TEXT' for col in df.columns])
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS "{tabela}" ({colunas})')
        self.conn.commit()

    def carregar_zip_url_autos(self, url, tabela, separador=";"):
        response = requests.get(url, verify=False)
        response.raise_for_status()

        anos_validos = list(range(self.ano_atual - 4, self.ano_atual + 1))

        with zipfile.ZipFile(BytesIO(response.content)) as z:
            for file_name in z.namelist():
                if file_name.endswith(".csv"):
                    match = re.search(r"(\d{4})\.csv$", file_name)
                    if match:
                        ano = int(match.group(1))
                        if ano in anos_validos:
                            with z.open(file_name) as f:
                                df = pd.read_csv(
                                    f,
                                    sep=separador,
                                    encoding="utf8",
                                    dtype={"CPF_CNPJ_INFRATOR": str},
                                    low_memory=False,
                                )
                                df["ano"] = ano
                                self._criar_tabela(tabela, df)

                                self.cursor.execute(
                                    f'DELETE FROM "{tabela}" WHERE ano = ?', (str(ano),)
                                )
                                self.conn.commit()
                                df.to_sql(tabela, self.conn, if_exists="append", index=False)

    def carregar_zip_url_embargos(self, url, tabela, separador=";"):
        response = requests.get(url, verify=False)
        response.raise_for_status()

        with zipfile.ZipFile(BytesIO(response.content)) as z:
            for file_name in z.namelist():
                if file_name.endswith(".csv"):
                    with z.open(file_name) as f:
                        df = pd.read_csv(
                            f,
                            sep=separador,
                            encoding="utf8",
                            dtype={"CPF_CNPJ_EMBARGADO": str},
                            low_memory=False,
                        )
                        self._criar_tabela(tabela, df)
                        self.cursor.execute(f'DELETE FROM "{tabela}"')
                        self.conn.commit()
                        df.to_sql(tabela, self.conn, if_exists="append", index=False)

# ========================
# Agente Bronze
# ========================
class AgenteBronzeIBAMA:
    def __init__(self, raw_db, bronze_db):
        self.raw_conn = sqlite3.connect(raw_db)
        self.bronze_conn = sqlite3.connect(bronze_db)

    def replicar_tabela(self, tabela):
        df = pd.read_sql_query(f'SELECT * FROM "{tabela}"', self.raw_conn)
        df.to_sql(tabela, self.bronze_conn, if_exists="replace", index=False)
        print(f"📦 Tabela {tabela} replicada para Bronze ({len(df)} registros)")

# ========================
# Agente Silver
# ========================
class AgenteSilverIBAMA:
    def __init__(self, bronze_db, silver_db):
        self.bronze_conn = sqlite3.connect(bronze_db)
        self.silver_conn = sqlite3.connect(silver_db)

    def limpar_colunas_documento(self, df, colunas):
        for col in colunas:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(r"\.0$", "", regex=True)
                    .str.replace(r"\D", "", regex=True)
                )
        return df

    def processar_tabela(self, tabela, colunas_limpeza=None):
        df = pd.read_sql_query(f'SELECT * FROM "{tabela}"', self.bronze_conn)

        if colunas_limpeza:
            df = self.limpar_colunas_documento(df, colunas_limpeza)

        # Normalizar colunas
        df.columns = normalizar_colunas(df.columns)

        df.to_sql(tabela, self.silver_conn, if_exists="replace", index=False)
        print(f"✨ Tabela {tabela} salva na Silver ({len(df)} registros)")

settings = Settings()
# --- RAW ---
raw = AgenteRawIBAMA(settings.raw_db_path)
raw.carregar_zip_url_autos(settings.url_autos_ibama, settings.AutosInfracao_table_name)
raw.carregar_zip_url_embargos(settings.url_embargos_ibama, settings.embargos_table_name)
# --- BRONZE ---
bronze = AgenteBronzeIBAMA(settings.raw_db_path, settings.bronze_db_path)
bronze.replicar_tabela(settings.AutosInfracao_table_name)
bronze.replicar_tabela(settings.embargos_table_name)
# --- SILVER ---
silver = AgenteSilverIBAMA(settings.bronze_db_path, settings.silver_db_path)
silver.processar_tabela(settings.AutosInfracao_table_name, colunas_limpeza=["CPF_CNPJ_INFRATOR"])
silver.processar_tabela(settings.embargos_table_name, colunas_limpeza=["CPF_CNPJ_EMBARGADO"])


# %%
