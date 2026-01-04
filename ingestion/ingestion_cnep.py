import requests
from dotenv import load_dotenv
import os
import sqlite3
from ingestion_settings import Settings
import json
import re
import unicodedata

# Configuration
load_dotenv()
settings = Settings()
url_base = settings.base_url_cnep
pagina = 1
DATA_API_KEY = os.getenv("PORTALDATRANSPARENCIA_API_KEY")
dados = []
download = [1]
# Cabeçalhos da requisição
headers = {
    "chave-api-dados": DATA_API_KEY
}

while len(download) > 0:
    try:
        # Realizando a requisição GET
        url = url_base + str(pagina)
        response = requests.get(url, headers=headers)

        # Verificando se a requisição foi bem-sucedida
        if response.status_code == 200:
            print(f"Baixando página {pagina}", end="\r")
            download = response.json()
            dados.extend(download)
            pagina += 1
        else:
            print(f"Falha na requisição: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")


def limpar_texto(valor):
    if valor is None:
        return None

    # 1. Remover acentos
    valor = unicodedata.normalize('NFKD', valor).encode('ASCII', 'ignore').decode('ASCII')

    # 2. MAIÚSCULO
    valor = valor.upper()

    # 3. Remover caracteres especiais (fica só letras, números e espaço)
    valor = re.sub(r'[^A-Z0-9 ]+', '', valor)

    # 4. Remover espaços extras
    return valor.strip()


def somente_digitos(valor):
    if valor is None:
        return None
    return re.sub(r'\D', '', valor)  # remove tudo que não for dígito

silver_tablename = settings.cnep_TableName
silver_conn = sqlite3.connect(settings.silver_db_path)
silver_cursor = silver_conn.cursor()

silver_cursor.executescript(f"""
CREATE TABLE IF NOT EXISTS {silver_tablename} (
    id INTEGER PRIMARY KEY,
    dataReferencia TEXT,
    dataInicioSancao TEXT,
    dataFimSancao TEXT,
    dataPublicacaoSancao TEXT,
    dataTransitadoJulgado TEXT,
    dataOrigemInformacao TEXT,

    -- tipo sancao
    tipoSancao_descricaoResumida TEXT,
    tipoSancao_descricaoPortal TEXT,

    -- fonte sancao
    fonteSancao_nomeExibicao TEXT,
    fonteSancao_telefoneContato TEXT,
    fonteSancao_enderecoContato TEXT,

    -- orgao sancionador
    orgaoSancionador_nome TEXT,
    orgaoSancionador_siglaUf TEXT,
    orgaoSancionador_poder TEXT,
    orgaoSancionador_esfera TEXT,

    -- sancionado
    sancionado_nome TEXT,
    sancionado_codigoFormatado TEXT,

    -- pessoa
    pessoa_id INTEGER,
    pessoa_cpfFormatado TEXT,
    pessoa_cnpjFormatado TEXT,
    pessoa_numeroInscricaoSocial TEXT,
    pessoa_nome TEXT,
    pessoa_razaoSocialReceita TEXT,
    pessoa_nomeFantasiaReceita TEXT,
    pessoa_tipo TEXT,

    valorMulta TEXT,
    textoPublicacao TEXT,
    linkPublicacao TEXT,
    detalhamentoPublicacao TEXT,
    numeroProcesso TEXT,
    abrangenciaDefinidaDecisaoJudicial TEXT,
    informacoesAdicionaisDoOrgaoSancionador TEXT,

    fundamentacao_json TEXT
);
""")

silver_conn.commit()

# ----------------------------------------------------------
# Função para inserir um item
# ----------------------------------------------------------
def inserir_sancao(item):
    fundamentacao_json = json.dumps(item["fundamentacao"], ensure_ascii=False)

    silver_cursor.execute(f"""
        INSERT OR REPLACE INTO {silver_tablename} (
            id, dataReferencia, 
            dataInicioSancao, 
            dataFimSancao,
            dataPublicacaoSancao, 
            dataTransitadoJulgado, 
            dataOrigemInformacao,

            tipoSancao_descricaoResumida,
            tipoSancao_descricaoPortal,

            fonteSancao_nomeExibicao,
            fonteSancao_telefoneContato,
            fonteSancao_enderecoContato,

            orgaoSancionador_nome,
            orgaoSancionador_siglaUf,
            orgaoSancionador_poder,
            orgaoSancionador_esfera,

            sancionado_nome,
            sancionado_codigoFormatado,

            pessoa_id,
            pessoa_cpfFormatado,
            pessoa_cnpjFormatado,
            pessoa_numeroInscricaoSocial,
            pessoa_nome,
            pessoa_razaoSocialReceita,
            pessoa_nomeFantasiaReceita,
            pessoa_tipo,

            valorMulta,
            textoPublicacao,
            linkPublicacao,
            detalhamentoPublicacao,
            numeroProcesso,
            abrangenciaDefinidaDecisaoJudicial,
            informacoesAdicionaisDoOrgaoSancionador,

            fundamentacao_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item["id"],
        item["dataReferencia"],
        item["dataInicioSancao"],
        item["dataFimSancao"],
        item["dataPublicacaoSancao"],
        limpar_texto(item["dataTransitadoJulgado"]),
        item["dataOrigemInformacao"],

        limpar_texto(item["tipoSancao"]["descricaoResumida"]),
        limpar_texto(item["tipoSancao"]["descricaoPortal"]),

        limpar_texto(item["fonteSancao"]["nomeExibicao"]),
        item["fonteSancao"]["telefoneContato"],
        limpar_texto(item["fonteSancao"]["enderecoContato"]),

        limpar_texto(item["orgaoSancionador"]["nome"]),
        item["orgaoSancionador"]["siglaUf"],
        limpar_texto(item["orgaoSancionador"]["poder"]),
        item["orgaoSancionador"]["esfera"],

        limpar_texto(item["sancionado"]["nome"]),
        somente_digitos(item["sancionado"]["codigoFormatado"]),

        item["pessoa"]["id"],
        item["pessoa"]["cpfFormatado"],
        somente_digitos(item["pessoa"]["cnpjFormatado"]),
        item["pessoa"]["numeroInscricaoSocial"],
        limpar_texto(item["pessoa"]["nome"]),
        limpar_texto(item["pessoa"]["razaoSocialReceita"]),
        limpar_texto(item["pessoa"]["nomeFantasiaReceita"]),
        limpar_texto(item["pessoa"]["tipo"]),

        item["valorMulta"],
        limpar_texto(item["textoPublicacao"]),
        item["linkPublicacao"],
        limpar_texto(item["detalhamentoPublicacao"]),
        item["numeroProcesso"],
        item["abrangenciaDefinidaDecisaoJudicial"],
        item["informacoesAdicionaisDoOrgaoSancionador"],

        fundamentacao_json
    ))

# ----------------------------------------------------------
# Insere toda a lista
# ----------------------------------------------------------
for s in dados:
    inserir_sancao(s)

silver_conn.commit()
silver_conn.close()

print("Todas as sanções foram inseridas na tabela!")

