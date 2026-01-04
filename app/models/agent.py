from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# MAIN OUTPUT MODELS (Keep only these 5)

class IbamaAnalysis(BaseModel):
    """Consolidated Stream 1 Analysis from IBAMA"""

    resumo_esg: str = Field(description="Resumo geral dos riscos e pontos positivos ESG")
    gravidade: str = Field(description="Gravidade do evento (alta, média ou baixa)")
    impactos: str = Field(description="Impactos ambientais detalhados")
    score_qualitativo: int = Field(description="Nota ESG da avaliação qualitativa (0 a 10)")
    score_final: int = Field(description="Nota ESG final (0 a 10)")
    justificativa_score: str = Field(description="Justificativa da nota ESG final")
    recommendation: str = Field(description="Recomendações para melhoria da nota")
    confidence_score: float = Field(description="Analysis confidence 0-1")

class MTEAnalysis(BaseModel):
    """Consolidated Stream 2 Analysis from MTE"""

    eventos_mte: List[Dict[str, Any]] = Field(description="Ocorrencia de eventos de trabalho escravo")

class CnepAnalysis(BaseModel):
    """Consolidated Stream 3 Analysis from CNEP"""

    resumo_esg: str = Field(description="Resumo geral dos riscos e pontos positivos ESG")
    gravidade: str = Field(description="Gravidade do evento (alta, média ou baixa)")
    impactos: str = Field(description="Impactos detalhados")
    score_qualitativo: int = Field(description="Nota ESG da avaliação qualitativa (0 a 10)")
    score_final: int = Field(description="Nota ESG final (0 a 10)")
    justificativa_score: str = Field(description="Justificativa da nota ESG final")
    recommendation: str = Field(description="Recomendações para melhoria da nota")
    confidence_score: float = Field(description="Analysis confidence 0-1")

class CeisAnalysis(BaseModel):
    """Consolidated Stream 4 Analysis from CEIS"""

    resumo_esg: str = Field(description="Resumo geral dos riscos e pontos positivos")
    gravidade: str = Field(description="Gravidade do evento (alta, média ou baixa)")
    impactos: str = Field(description="Impactos detalhados")
    score_qualitativo: int = Field(description="Nota ESG da avaliação qualitativa (0 a 10)")
    score_final: int = Field(description="Nota ESG final (0 a 10)")
    justificativa_score: str = Field(description="Justificativa da nota ESG final")
    recommendation: str = Field(description="Recomendações para melhoria da nota")
    confidence_score: float = Field(description="Analysis confidence 0-1")

class FinalRecommendationESG(BaseModel):
    """Final consolidated ESG recommendation"""

    risco_final: str = Field(description="ALTO RISCO, MÉDIO RISCO, or BAIXO RISCO")
    confidence: float = Field(description="Confidence in recommendation 0-1")
    rationale: str = Field(description="Rationale combining all streams")
    key_risks: List[str] = Field(description="Top risks from all streams")
    justificativa_score: str = Field(description="Justificativa da avaliação final")
    recommendation: str = Field(description="Recomendações para melhoria da nota")


# API REQUEST/RESPONSE MODELS
class AgentRequestESG(BaseModel):
    """Request model for agent analysis"""

    PessoaConsultada: Optional[str] = Field(
        default=None, description="CPF/CNPJ da pessoa a ser avaliada"
    )
    message: Optional[str] = Field(
        default=None, description="Message to extract ticker from"
    )

class AgentResponseESG(BaseModel):
    """Response model for agent analysis"""

    pessoa: str = Field(description="CPF/CNPJ da pessoa a ser avaliada")
    nota_quantitativa: float = Field(description="Quantitative score")
    execution_time: float = Field(description="Total execution time in seconds")

    # Main stream results
    Ibama_analysis: IbamaAnalysis = Field(
        description="Stream 1 - Ibama analysis results"
    )
    MTE_analysis: MTEAnalysis = Field(
        description="Stream 2 - MTE analysis results")
    
    CNEP_analysis: CnepAnalysis = Field(
        description="Stream 3 - CNEP analysis results")

    CEIS_analysis: CeisAnalysis = Field(
        description="Stream 4 - CEIS analysis results")        

    # Final recommendation
    final_recommendation: FinalRecommendationESG = Field(
        description="Aggregated final recommendation"
    )
