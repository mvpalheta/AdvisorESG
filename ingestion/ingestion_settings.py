from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv


class Settings(BaseSettings):

    load_dotenv()

    # Config file paths
    raw_db_path: str = "sqlite_db/advisor_esg_raw.db"
    bronze_db_path: str = "sqlite_db/advisor_esg_bronze.db"
    silver_db_path: str = "sqlite_db/advisor_esg_silver.db"
    url_autos_ibama: str = "https://dadosabertos.ibama.gov.br/dados/SIFISC/auto_infracao/auto_infracao/auto_infracao_csv.zip"
    url_embargos_ibama: str = "https://dadosabertos.ibama.gov.br/dados/SIFISC/termo_embargo/termo_embargo/termo_embargo_csv.zip"
    url_lista_suja_mte: str = "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/areas-de-atuacao/cadastro_de_empregadores.csv"
    base_url_cnep: str = "https://api.portaldatransparencia.gov.br/api-de-dados/cnep?pagina="
    base_url_ceis: str = "https://api.portaldatransparencia.gov.br/api-de-dados/ceis?pagina="

    model_config = {"env_file": ".env", "extra": "allow"}

    #database table names
    embargos_table_name: str = "embargos"
    AutosInfracao_table_name: str = "autos_infracao"
    trabalho_escravo_TableName: str = "trabalho_escravo"
    cnep_TableName: str = "sancoes_cnep"
    CEIS_TableName: str = "sancoes_ceis"
