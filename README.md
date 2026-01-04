# Advisor ESG

Um sistema de análise multi-stream que utiliza RAG (Retrieval-Augmented Generation) para realizar análise ESG (Environmental, Social, Governance) de pessoas físicas e jurídicas do Brasil. Inspirado pelo projeto [RAGFOLIO](https://github.com/infoslack/RAGfolio) do Daniel Romero, este projeto combina dados de diversas fontes com modelos LLM para fornecer análise dos 3 aspectos ESG.

# Demonstração

https://github.com/user-attachments/assets/29e212dd-abf7-48bb-a438-6ec02bc0eda8

## Visão Geral

This project combines advanced vector search with LLM analysis to provide comprehensive investment insights through three parallel streams:

Este projeto cobina análise quantitativa com LLM para fornecer uma abrangente análise dos aspectos ESG a partir de cinco streams:

1. **Análise Quantitativa** - Nota quantitativa a partir de regras básicas (também poderia ser a partir de um modelo de machine learning ou algum outro tipo de análise quantitativa)
2. **Environment Analysis** - Análise de informações sobre embargos e autos de infração aplicados pelo IBAMA
3. **Social Analysis** - Processa dados da lista de empregadores que submeteram trabalhadores a condições análogas à escravidão disponibilizado pelo Ministério do Trabalho e Emprego (MTE)  
4. **Governance Analysis 1** - Avalia informações do Cadastro Nacional de Empresas Punidas (CNEP), disponibilizados pela Controladoria Geral da União (CGU), que lista empresas punidas por atos lesivos contra a Administração Pública, conforme a Lei Anticorrupção (Lei 12.846/2013)
5. **Governance Analysis 2** - Avalia informações do Cadastro Nacional de Empresas Inidôneas e Suspensas (CEIS), disponibilizados pela CGU, que lista empresas e pessoas físicas que sofreram sanções que implicaram a restrição de participar de licitações ou de celebrar contratos com a Administração Pública, conforme a Lei Anticorrupção (Lei 12.846/2013)

### Detalhes do Fluxo de Análise

#### Análise Quantitativa (Stream 1)
O stream de análise quantitativa processa informações do IBAMA e aplica algumas regras básicas para calcular uma nota inicial que varia de zero (pior cenário) a dez (melhor cenário). Essa nota também poderia ser calculada de forma mais sofisticada a partir de um modelo de machine learning, por exemplo. No caso deste projeto foram utilizadas regras simples apenas para ilustrar o processo.

#### Environment Analysis (Stream 2)
O stream de análise ambiental (Environment Analysis) processa informações sobre os motivos dos [autos de infração](https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao) e [embargos](https://dadosabertos.ibama.gov.br/dataset/termos-de-embargo) realizados pelo Ibama em suas ações de fiscalização. O sistema busca a descrição (motivo legal) de aplicação dos autos de infracao e/ou embargos para entender melhor a causa de aplicação deles. O conteúdo recuperado é então analisado utilizando um prompt especializado que atua como um analista ESG senior sintetizando toda a informação em uma avaliação consolidada que inclui um resumo geral dos riscos e pontos positivos ESG, gravidade do evento (alta, média, baixa), Impactos ambientais, nota ESG da avaliação qualitativa, nota ESG final sugerida, justificativa da nota ESG final, recomendações para melhoria da nota e um nível de confiança na análise qualitativa.

#### Social Analysis (Stream 3)  
A análise social (Social Analysis) foca no Cadastro de Empregadores que tenham submetido trabalhadores a condições análogas à de escravo [(Lista Suja do Trabalho Escravo)](https://dados.gov.br/dados/conjuntos-dados/trabalho-analogo-ao-de-escravo) disponibilizada pelo MTE para capturar o aspecto social. As informações recuperadas são analizadas pelo fluxo LLM a fim de sugerir uma nota final para a pessoa avaliada.

#### Governance Analysis 1 (Stream 4)
O stream 1 de análise de governança (Governance Analysis 1) analisa informações do CNEP disponibilizadas pela CGU. O sistema basicamente avalia a fundamentação legal que embasou a sanção a fim de entender os motivos da aplicação. O conteúdo é analisado utilizando um prompt especializado que atua como um analista ESG senior sintetizando toda a informação em uma avaliação consolidada que inclui um resumo geral dos riscos e pontos positivos ESG, gravidade do evento (alta, média, baixa), Impactos ambientais, nota ESG da avaliação qualitativa, nota ESG final sugerida, justificativa da nota ESG final, recomendações para melhoria da nota e um nível de confiança na análise qualitativa.

#### Governance Analysis 2 (Stream 5)
O stream 2 de análise de governança (Governance Analysis 2) analisa informações do CEIS disponibilizadas pela CGU. O sistema basicamente avalia a fundamentação legal que embasou a sanção a fim de entender os motivos da aplicação. O conteúdo é analisado utilizando um prompt especializado que atua como um analista ESG senior sintetizando toda a informação em uma avaliação consolidada que inclui um resumo geral dos riscos e pontos positivos ESG, gravidade do evento (alta, média, baixa), Impactos ambientais, nota ESG da avaliação qualitativa, nota ESG final sugerida, justificativa da nota ESG final, recomendações para melhoria da nota e um nível de confiança na análise qualitativa.

#### Agregação Final

Após os cinco streams completarem as suas análises, um passo final de agregação sintetiza os resultados em uma recomendação de risco ESG unificada. O prompt de agregação recebe os outputs de todos os streams e age como um especialista em análise ESG encarregado de combinar as análises dos cinco streams em uma análise ESG unificada com uma recomendação de risco final. O resultado final fornece uma recomendação de ALTO, MÉDIO ou BAIXO risco, a justificativa do score final, o racional de decisão e a recomendação de ação além dos riscos chaves contidos em todas as dimensões analisadas.

### Inspiração

A abordagem deste projeto é baseada no projeto [RAGFOLIO](https://github.com/infoslack/RAGfolio) do Daniel Romero. A execução de streams independentes permite que cada fluxo de trabalho foque em sua especialidade produzindo uma análise final mais abrangente do que qualquer abordagem de análise individual poderia alcançar.

## Estrutura do Diretório

```
app/
├── analyzers/              	# Analysis stream implementations
│   ├── __init__.py
│   ├── quant_analyzer.py  		# Stream 1: análise quantitativa baseada em regras
│   ├── ibama_analyzer.py     	# Stream 2: análise de informações sobre embargos e autos de infração do Ibama
│   ├── MTE_analyzer.py   		# Stream 3: análise de informações da Lista Suja de Trabalho Escravo
│   ├── cnep_analyzer.py     	# Stream 4: análise de informações sobre CNEP
│   └── ceis_analyzer.py   		# Stream 5: análise de informações sobre CEIS
│
├── config/                 	# Arquivos de configurações
│   └── settings.py 			# Arquivo de configurações de ambiente e aplicação
│
├── models/                 	# Pydantic data models
│   └── agent.py      			# Modelos para resultados das análises e schemas da API
│
├── prompts/               		# LLM system prompts
│   ├── final_recommendation.md # Prompt de sistema para a agregação final dos streams
│   ├── ibama_analysis.md  		# Prompt de sistema para o Stream 2
│   ├── cnep_analysis.md     	# Prompt de sistema para o Stream 4
│   └── ceis_analysis.md    	# Prompt de sistema para o Stream 5
│
├── routers/               		# FastAPI route handlers
│   └── agent.py          		# Endpoint do agente analista ESG
│
├── services/              		# Lógica de negócio e integrações externas
│   ├── agent_serviceESG.py    	# Serviço de orquestração principal
│   ├── prompt_manager.py     	# Prompt loading and caching
│   └── retrieverESG.py         # Recupera informações para os streams
│
└── main.py               		# FastAPI application entry point


front/
└── streamlit_app.py			# Frontend app


app/
└── ingestion/              	# Implementação dos ingestores de dados
    ├── __init__.py
    ├── ingestion_ceis.py  		# Download e ingestão de dados do CEIS para um banco de dados sqlite
    ├── ingestion_cnep.py     	# Download e ingestão de dados do CNEP para um banco de dados sqlite
    ├── ingestion_ibama.py   	# Download e ingestão de dados do IBAMA (embargos e autos de infração) para um banco de dados sqlite
    ├── ingestion_mte.py     	# Download e ingestão de dados do MTE para um banco de dados sqlite
    └── ingestion_settings.py   # Arquivo de confiração dos ingestores de dados

```

## Componentes Chave

- **Analyzers**: Cinco streams independentes que processam diferentes fontes de dados
- **Services**: Lógica negocial para recuperação de dados, interação LLM e orquestração
- **Models**: Tipagem de dadoss usando Pydantic para as intereções com a API e resultados das análises
- **Prompts**: Templates de prompts de sistema para as diferentes tarefas de análise
- **Config**: Gerenciamento centralizado de configurações

## Setup e Instalção

### Prerequisitos
- Python 3.14+
- Groq API key for LLM access

### Instalação
```bash
pip install -r requirements.txt
```

### Configuration
1. Renomeie o arquivo .env-example para .env e define suas configurações:

2. Edite o arquivo `.env` com sua chave API e outrras configurações necessárias

3. Se assegure de que sua base de dados sqlite esteja populada com os dados necessários (IBAMA, MTE, CNEP e CEIS)


This will start:

### Rodando a API
1. No prompt de comando, navegue até o diretório raiz do seu projeto e execute o código abaixo:
```bash
uvicorn app.main:app --reload
```
A API estará disponível em `http://localhost:8000` com a documentação interativa em `http://localhost:8000/docs`.

### Rodando o Frontend
1. No prompt de comando, navegue até o diretório '\front' dentro do diretório raiz do seu projeto e execute o código abaixo:
```bash
streamlit run streamlit_app.py
```
O app frontend estará disponível em `http://localhost:8501/`

- Backend API: http://localhost:8000 com documentação interativa em /docs
- Interface Frontend: http://localhost:3000

### Exemplo de Uso com Python
```bash
import requests
import json

url = "http://127.0.0.1:8000/agentESG"

payload = {
    "PessoaConsultada": "07954125000108"
}

response = requests.post(url, json=payload)
```
Isto irá realizar a requisição para os cinco streams completos, retornando a nota quantitativa, análise Ibama, análise MTE, análise CNEP, análise CEIS e recomendação final.

### Exemplo de Retorno da API
A API irá retornar uma análise estruturada dos cinco streams e a recomendação final, conforme abaixo:

**Stream 1 - Análise Quantitativa**
```json
{
    "pessoa": "07954125000108",
    "nota_quantitativa": 8.0,
    "execution_time": 5.077399492263794,
```
**Stream 2 - Environment Analysis**
```json

    "Ibama_analysis": {
        "resumo_esg": "A empresa foi embargada por atividades ambientais ilegais, o que afeta negativamente sua nota ESG",
        "gravidade": "Alta",
        "impactos": "Lei Federal 9605/98, Decreto Federal 6514/08, embargada toda e qualquer atividade na área de coordenadas centrais Lat. 07º01'47'' S e Long 36º54'07,5'' W",
        "score_qualitativo": 6,
        "score_final": 6,
        "justificativa_score": "A nota foi reduzida devido à gravidade do evento",
        "recommendation": "Melhorar a gestão ambiental da empresa",
        "confidence_score": 0.9
    },
```
**Stream 3 - Social Analysis**
```json

    "MTE_analysis": {
        "eventos_mte": [
            {
                "data": "09/04/2025",
                "cpf_cnpj": "07954125000108",
                "descricao": "Empregador VULCANO EXPORT MINERACAO EXPORTACAO E IMPORTACAO LTDA incluído na lista de trabalho escravo",
                "pilar": "Social",
                "gravidade": "Alta",
                "fonte": "Lista de Trabalho Escravo (MTE)"
            }
        ]
    },
```
**Stream 4 - Governance Analysis 1 (CNEP)**
```json

    "CNEP_analysis": {
        "resumo_esg": "Não existem eventos para a pessoa pesquisada",
        "gravidade": "baixa",
        "impactos": "Não existem impactos, pois não existem eventos para a pessoa",
        "score_qualitativo": 8,
        "score_final": 8,
        "justificativa_score": "Não se aplica",
        "recommendation": "Não se aplica",
        "confidence_score": 0.5
    },
```

**Stream 5 - Governance Analysis 2 (CEIS)**
```json

    "CEIS_analysis": {
        "resumo_esg": "Não existem eventos para a pessoa pesquisada",
        "gravidade": "baixa",
        "impactos": "Não existem impactos, pois não existem eventos para a pessoa",
        "score_qualitativo": 8,
        "score_final": 8,
        "justificativa_score": "Não se aplica",
        "recommendation": "Não se aplica",
        "confidence_score": 0.0
    },
```

**Final Aggregated Recommendation**
```json

    "final_recommendation": {
        "risco_final": "ALTO RISCO",
        "confidence": 0.8,
        "rationale": "A empresa foi embargada por atividades ambientais ilegais e consta na lista de trabalho escravo, o que afeta negativamente sua nota ESG. A nota final é baixa devido à gravidade do evento e à inclusão na lista de trabalho escravo. Recomenda-se melhorar a gestão ambiental da empresa e evitar práticas de trabalho escravo.",
        "key_risks": [
            "Trabalho escravo",
            "Atividades ambientais ilegais"
        ],
        "justificativa_score": "A nota foi reduzida devido à gravidade do evento e inclusão na lista de trabalho escravo",
        "recommendation": "Melhorar a gestão ambiental da empresa e evitar práticas de trabalho escravo"
    }
}
```

### Pontos de Melhoria
- Realizar embedding das informações em cada stream antes de passa-las para o LLM analisar;

- Melhoria nos prompts dos streams;

- Acrescentar outras informações para refinar as análises.

### Agradecimentos
Agradeço ao [Daniel Romero](https://substack.com/@infoslack/posts) pela desenvolvimento, estruturação e compartilhamento do proejto RAGFOLIO com a comunidade. O projeto é uma verdadeira aula prática de engenharia de IA com uma estrutura muito didática.