#%%
from app.services.retrieverESG import AgenteRetrieverESG
from app.models.agent import MTEAnalysis

#%%

def MTEAnalyzer(db_path, pessoa_consultada):

    retriever = AgenteRetrieverESG(db_path)
    eventos = retriever.eventos_trabalho_escravo(pessoa_consultada)

    if len(eventos) == 0:
        eventos = [{
                    "data": "Não se aplica",
                    "descricao": "Não existem eventos de trabalho escravo para a pessoa pesquisada",
                    "pilar": "Social",
                    "gravidade": "Não se aplica",
                    "fonte": "Lista de Trabalho Escravo (MTE)"
                }]

    return MTEAnalysis(eventos_mte=eventos)