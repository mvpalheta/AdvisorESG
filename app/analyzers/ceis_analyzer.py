#%%
# ====================================================
# Analista ESG - CEIS
# ====================================================
from app.config.settings import Settings

#%%
settings = Settings()
llm_model = settings.llm_model

def CeisAnalyzer(client, 
                  eventos,
                  nota_quant,
                  pessoa, 
                  response_model, 
                  prompt_manager, 
                  prompt_name="ceis_analysis"):
    """
    Combina regras fixas + análise LLM para devolver avaliação ESG.
    """

    system_prompt = prompt_manager.get_prompt(prompt_name)

    user_prompt = f"""
        Pessoa analisada: {pessoa}

        Eventos registrados:
        {eventos}

        Nota preliminar calculada pelas regras determinísticas: {nota_quant}/10

        Agora refine a nota considerando o contexto qualitativo fornecido através dos eventos registrados.
        Caso não existam eventos relevantes, siga as instruções do prompt de sistema
        e mantenha a nota determinística.
    """

    resposta = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        response_model=response_model,  # Instructor handles everything!
    )

    return resposta.model_dump() #caso queira a resposta como dicionário
