#%%
# ====================================================
# Analista ESG - Quantitativo
# ====================================================
#%%

def aplicar_regras_basicas(eventos):
    """
    Aplica regras determinísticas simples para calcular nota preliminar.
    """
    nota = 10
    total_multas = 0
    embargos = 0
    altas = 0

    for ev in eventos:
        if ev.get("valor"):
            try:
                total_multas += float(str(ev["valor"]).replace(",", "."))
            except:
                pass
        if ev["fonte"] == "Termo de Embargo (IBAMA)":
            embargos += 1
        if ev["gravidade"] == "Alta":
            altas += 1

    # Penalizações
    if embargos > 0:
        nota -= embargos * 2
    if altas > 3:
        nota -= 2
    if total_multas > 1_000_000:
        nota -= 2

    return max(nota, 0)  # nunca menor que 0
