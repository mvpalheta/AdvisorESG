# ====================================================
# Agente Ingestor Trabalho Análogo ao de Escravo
# Camadas: RAW → BRONZE → SILVER
# ====================================================
import sqlite3
import pandas as pd
import requests
from io import BytesIO
from ingestion_settings import Settings
import chardet
import re

# ====================================================
# Funções Utilitárias
# ====================================================
def detectar_encoding(content):
    resultado = chardet.detect(content)
    return resultado["encoding"]

def normalizar_colunas(df):
    """
    Remove acentos, espaços e coloca nomes de colunas em snake_case.
    """
    df.columns = (
        df.columns.str.normalize("NFKD")  # remove acentos
        .str.encode("ascii", errors="ignore").str.decode("utf-8")
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", "_", regex=True)  # troca espaços por _
        .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)  # remove caracteres especiais
    )
    return df

def limpar_colunas_documento(df, colunas):
    """
    Converte colunas para string, remove .0 do final e mantém apenas dígitos.
    """
    for col in colunas:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r"\.0$", "", regex=True)  # remove final .0
                .str.replace(r"\D", "", regex=True)    # remove não dígitos
            )
    return df

# ====================================================
# Agente RAW
# ====================================================
class AgenteTrabalhoEscravoRaw:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def carregar_raw(self, url, tabela):
        print(f"📥 Baixando dados de {url}...")
        response = requests.get(url, verify=False)
        response.raise_for_status()

        raw_bytes = response.content
        encoding_detectado = detectar_encoding(raw_bytes)

        # Detecta formato
        if url.endswith(".xlsx") or url.endswith(".xls"):
            df = pd.read_excel(BytesIO(response.content))
        else:
            df = pd.read_csv(BytesIO(response.content), sep=";", encoding=encoding_detectado, low_memory=False)

        # Cria tabela RAW (colunas originais)
        colunas = ", ".join([f'"{col}" TEXT' for col in df.columns])
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS "{tabela}" ({colunas})')
        self.conn.commit()

        # Sobrescreve RAW
        self.cursor.execute(f'DELETE FROM "{tabela}"')
        self.conn.commit()
        df.to_sql(tabela, self.conn, if_exists="append", index=False)

        print(f"✅ Tabela RAW {tabela} carregada com {len(df)} registros")


# ====================================================
# Agente BRONZE
# ====================================================
class AgenteTrabalhoEscravoBronze:
    def __init__(self, raw_db_path, bronze_db_path):
        self.raw_conn = sqlite3.connect(raw_db_path)
        self.raw_cursor = self.raw_conn.cursor()

        self.bronze_conn = sqlite3.connect(bronze_db_path)
        self.bronze_cursor = self.bronze_conn.cursor()

    def replicar_raw_para_bronze(self, tabela_raw, tabela_bronze):
        print(f"🔄 Replicando dados de {tabela_raw} → {tabela_bronze}...")

        # Lê raw
        df = pd.read_sql_query(f'SELECT * FROM "{tabela_raw}"', self.raw_conn)

        # Cria tabela bronze
        colunas = ", ".join([f'"{col}" TEXT' for col in df.columns])
        self.bronze_cursor.execute(f'CREATE TABLE IF NOT EXISTS "{tabela_bronze}" ({colunas})')
        self.bronze_conn.commit()

        # Sobrescreve bronze
        self.bronze_cursor.execute(f'DELETE FROM "{tabela_bronze}"')
        self.bronze_conn.commit()
        df.to_sql(tabela_bronze, self.bronze_conn, if_exists="append", index=False)

        print(f"✅ Tabela BRONZE {tabela_bronze} replicada ({len(df)} registros)")


# ====================================================
# Agente SILVER
# ====================================================
class AgenteTrabalhoEscravoSilver:
    def __init__(self, bronze_db_path, silver_db_path):
        self.bronze_conn = sqlite3.connect(bronze_db_path)
        self.bronze_cursor = self.bronze_conn.cursor()

        self.silver_conn = sqlite3.connect(silver_db_path)
        self.silver_cursor = self.silver_conn.cursor()

    def transformar_para_silver(self, tabela_bronze, tabela_silver):
        print(f"✨ Transformando {tabela_bronze} → {tabela_silver}...")

        # Lê bronze
        df = pd.read_sql_query(f'SELECT * FROM "{tabela_bronze}"', self.bronze_conn)

        # Normaliza nomes das colunas
        df = normalizar_colunas(df)

        # Tratamento: limpar colunas de CNPJ/CPF (se existirem)
        possiveis_colunas_cnpj = ["cnpj", "cpf_cnpj", "CNPJ/CPF", "CNPJCPF", "cpf", "cpf_cnpj_do_infrator"]
        for col in possiveis_colunas_cnpj:
            if col in df.columns:
                df = limpar_colunas_documento(df, [col])
                break

        # Cria tabela silver
        colunas = ", ".join([f'"{col}" TEXT' for col in df.columns])
        self.silver_cursor.execute(f'DROP TABLE IF EXISTS "{tabela_silver}"')
        self.silver_cursor.execute(f'CREATE TABLE "{tabela_silver}" ({colunas})')
        self.silver_conn.commit()

        # Sobrescreve silver
        self.silver_cursor.execute(f'DELETE FROM "{tabela_silver}"')
        self.silver_conn.commit()
        df.to_sql(tabela_silver, self.silver_conn, if_exists="append", index=False)

        print(f"✅ Tabela SILVER {tabela_silver} criada ({len(df)} registros)")

# ====================================================
# Exemplo de uso
# ====================================================
settings = Settings()

# Instanciar agentes
agente_raw = AgenteTrabalhoEscravoRaw(settings.raw_db_path)
agente_bronze = AgenteTrabalhoEscravoBronze(settings.raw_db_path, settings.bronze_db_path)
agente_silver = AgenteTrabalhoEscravoSilver(settings.bronze_db_path, settings.silver_db_path)
url_lista_suja = settings.url_lista_suja_mte  

# Executar fluxo completo
agente_raw.carregar_raw(url_lista_suja, settings.trabalho_escravo_TableName)
agente_bronze.replicar_raw_para_bronze(settings.trabalho_escravo_TableName, settings.trabalho_escravo_TableName)
agente_silver.transformar_para_silver(settings.trabalho_escravo_TableName, settings.trabalho_escravo_TableName)
