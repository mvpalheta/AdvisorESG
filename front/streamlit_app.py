import streamlit as st
import requests
import time
import re

# ======================
# Configurações
# ======================
API_URL = "http://localhost:8000/agentESG"

st.set_page_config(
    page_title="ESG Advisor",
    page_icon="📊",
    layout="centered"
)

st.markdown("""
<style>
.stMainBlockContainer {
    max-width: 60%; /* Set your desired width here (e.g., 75rem, 1000px, 80%) */
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.block-container {
    padding-top: 0rem; /* Adjust this value to your liking, e.g., 0rem for no space */
    padding-bottom: 0rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# Funções de checagem e limpeza de CPF/CNPJ
# =========================================

def only_digits(value: str) -> str:
    """Remove qualquer caractere que não seja número"""
    return re.sub(r"\D", "", value)


def is_valid_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc_digit(cpf, weights):
        total = sum(int(d) * w for d, w in zip(cpf, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    digit1 = calc_digit(cpf[:9], range(10, 1, -1))
    digit2 = calc_digit(cpf[:10], range(11, 1, -1))

    return cpf[-2:] == digit1 + digit2


def is_valid_cnpj(cnpj: str) -> bool:
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc_digit(cnpj, weights):
        total = sum(int(d) * w for d, w in zip(cnpj, weights))
        remainder = total % 11
        return "0" if remainder < 2 else str(11 - remainder)

    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_2 = [6] + weights_1

    digit1 = calc_digit(cnpj[:12], weights_1)
    digit2 = calc_digit(cnpj[:13], weights_2)

    return cnpj[-2:] == digit1 + digit2

def validate_document(value: str):
    """
    Retorna:
    - (True, "CPF" | "CNPJ", value_limpo)
    - (False, None, value_limpo)
    """
    cleaned = only_digits(value)

    if len(cleaned) == 11:
        return is_valid_cpf(cleaned), "CPF", cleaned

    if len(cleaned) == 14:
        return is_valid_cnpj(cleaned), "CNPJ", cleaned

    return False, None, cleaned

# Style

css = """
.st-key-my_blue_container {
    background-color: #F0F8FF; /* Light blue color */;
    border: 1px solid rgba(0, 128, 255, 0.2);
}
"""

st.html(f"<style>{css}</style>")

# ======================
# Header
# ======================
st.title("Inteligência ESG ao seu alcance")
st.text(
    "Analise os riscos ESG usando inteligência de múltiplos agentes."
)

st.divider()

# ======================
# Input
# ======================
col1, col2 = st.columns([5, 1], vertical_alignment="bottom")

with col1:
    cpfcnpj_input = st.text_input(
        "Entre com o CPF/CNPJ da Empresa / Pessoa consultada",
        placeholder="Ex: 12345678910",
    )

with col2:
    analyze = st.button("Analisar 🚀", use_container_width=True, type="primary")

# ======================
# Chamada à API
# ======================
if analyze and cpfcnpj_input:

    is_valid, doc_type, cleaned_cpfcnpj = validate_document(cpfcnpj_input)

    if not is_valid:
        st.error("CPF ou CNPJ inválido. Verifique os dígitos informados.")
        st.stop()

    #st.success(f"{doc_type} válido detectado.")

    with st.spinner("Running ESG analysis..."):
        payload = {"PessoaConsultada": cleaned_cpfcnpj}
        start = time.time()
        response = requests.post(API_URL, json=payload)
        elapsed = time.time() - start

    if response.status_code != 200:
        st.error(f"Erro na API: {response.text}")
        st.stop()

    result = response.json()

    # ======================
    # Recomendação final
    # ======================

    col1, col2 = st.columns([0.75, 0.25], vertical_alignment="bottom")

    with col1:
        st.subheader(f"Análise ESG para {result['pessoa']}")

    with col2:
        st.caption(f"⏱ Tempo decorrido: {result.get("execution_time", elapsed):.2f}s")
    
    st.markdown(f"**Score quantitativo:** {result['nota_quantitativa']}/10")

    if result["final_recommendation"]['risco_final'] == "ALTO RISCO":
        risco_final = f":red[{result['final_recommendation']['risco_final']}]"
    else:
        risco_final = result["final_recommendation"]['risco_final']

    with st.container(border=True, key="my_blue_container"):
        
        st.markdown(
            f"""
            :blue[**Recomendação Final: {risco_final}** - {result["final_recommendation"]['justificativa_score']}]

            :blue[{result["final_recommendation"]['rationale']}]

            :blue[**Recomendação:**]

            :blue[{result["final_recommendation"]['recommendation']}]

            """            
        )

    st.divider()

    # ======================
    # Scores ESG
    # ======================
    c1, c2 = st.columns(2, border=True)

    with c1:
        st.markdown("#### 🌱 Environment")
        st.markdown(f"**Score:** {result['Ibama_analysis']['score_qualitativo']}/10")
        st.write(result["Ibama_analysis"]["resumo_esg"])
        st.markdown(f"**Recomendação:** {result['Ibama_analysis']['recommendation']}")
        #st.write(result["Ibama_analysis"]["impactos"])
        #st.write(result["Ibama_analysis"]["recommendation"])

    with c2:
        st.markdown("#### 👥 Social")
        st.write(result['MTE_analysis']['eventos_mte'][0]['descricao'])

    with st.container(border=True):
        st.markdown("#### 🏛 Governance", text_alignment="center")

    c1, c2 = st.columns(2, border=True)

    with c1:
        st.markdown("#### CNEP")
        st.markdown(f"**Score:** {result['CNEP_analysis']['score_qualitativo']}/10")
        st.write(result["CNEP_analysis"]["resumo_esg"])
        st.markdown(f"**Recomendação:** {result['CNEP_analysis']['recommendation']}")
        #st.write(result["CNEP_analysis"]["impactos"])
        #st.write(result["CNEP_analysis"]["recommendation"])

    with c2:
        st.markdown("#### CEIS")
        st.markdown(f"**Score:** {result['CEIS_analysis']['score_qualitativo']}/10")
        st.write(result["CEIS_analysis"]["resumo_esg"])
        st.markdown(f"**Recomendação:** {result['CEIS_analysis']['recommendation']}")
        #st.write(result["CEIS_analysis"]["impactos"])
        #st.write(result["CEIS_analysis"]["recommendation"])

    st.divider()

    # ======================
    # Riscos e Oportunidades
    # ======================
    r1, = st.columns(1)

    with r1:
        st.markdown("#### ⚠ Key Risks")
        if result["final_recommendation"]["key_risks"]:
            riscos = ""
            for risk in result["final_recommendation"]["key_risks"]:
                riscos += "- " + risk + "\n"
            st.error(riscos)
        else:
            st.write("No major risks identified.")

elif analyze:
    st.warning("Informe uma empresa ou pessoa para análise.")
