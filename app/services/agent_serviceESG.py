
from app.config.settings import Settings
from groq import Groq
import instructor
from pathlib import Path
import time

from app.services.retrieverESG import AgenteRetrieverESG
from app.services.prompt_manager import PromptManager
from app.models.agent import (
    IbamaAnalysis,
    MTEAnalysis,
    CnepAnalysis,
    CeisAnalysis,
    FinalRecommendationESG,
    AgentResponseESG,
)

from app.analyzers.quant_analyzer import aplicar_regras_basicas
from app.analyzers.Ibama_analyzer import IbamaAnalyzer
from app.analyzers.MTE_analyzer import MTEAnalyzer
from app.analyzers.cnep_analyzer import CnepAnalyzer
from app.analyzers.ceis_analyzer import CeisAnalyzer



class AgentServiceESG:

    """ESG Analysis Agent Service - Orchestrates all analysis streams"""

    def __init__(
        self, settings: Settings
    ):
        # Initialize LLM client and patch with Instructor
        base_client = Groq(api_key=settings.llm_api_key)
        self.client = instructor.from_groq(base_client)
        self.model = settings.llm_model

        # Initialize services
        prompts_dir = Path(__file__).parent.parent / "prompts"
        self.prompt_manager = PromptManager(prompts_dir)

        self.db_path = settings.db_path
        self.retriever = AgenteRetrieverESG(self.db_path)
        #self.nota_quat = aplicar_regras_basicas(self.retriever.eventos_ibama(PessoaConsultada))

    def ESG_Analyzer (self, PessoaConsultada):

        """Run complete ESG analysis with all streams + aggregation"""

        start_time = time.time()

        nota_quant = aplicar_regras_basicas(self.retriever.eventos_ibama(PessoaConsultada))

        AnaliseIbama = IbamaAnalyzer(self.client, 
                                     self.retriever.eventos_ibama(PessoaConsultada),
                                     nota_quant,
                                     PessoaConsultada, 
                                     IbamaAnalysis,
                                     self.prompt_manager)
        
        AnaliseMTE = MTEAnalyzer(self.db_path, PessoaConsultada)

        AnaliseCNEP = CnepAnalyzer(self.client, 
                                     self.retriever.eventos_cnep(PessoaConsultada),
                                     nota_quant,
                                     PessoaConsultada, 
                                     CnepAnalysis,
                                     self.prompt_manager)

        AnaliseCEIS = CeisAnalyzer(self.client, 
                                     self.retriever.eventos_ceis(PessoaConsultada),
                                     nota_quant,
                                     PessoaConsultada, 
                                     CeisAnalysis,
                                     self.prompt_manager)                

        # Run final recommendation
        final_recommendation = self._aggregate_analyses(
            PessoaConsultada, nota_quant, AnaliseIbama, AnaliseMTE, AnaliseCNEP, AnaliseCEIS
        )

        execution_time = time.time() - start_time

        return AgentResponseESG(
            pessoa=PessoaConsultada,
            nota_quantitativa=nota_quant,
            execution_time=execution_time,
            Ibama_analysis=AnaliseIbama,
            MTE_analysis=AnaliseMTE,
            CNEP_analysis=AnaliseCNEP,
            CEIS_analysis=AnaliseCEIS,
            final_recommendation=final_recommendation,
        )
    
    def _aggregate_analyses(
        self,
        PessoaConsultada: str,
        Nota_Quant: int,
        Ibama_analysis: IbamaAnalysis,
        MTE_analysis: MTEAnalysis,
        CNEP_analysis: CnepAnalysis,
        CEIS_analysis: CeisAnalysis,
    ) -> FinalRecommendationESG:
        """Aggregate all streams into final recommendation"""
        print(f"Starting final aggregation for {PessoaConsultada}")

        if len(self.retriever.eventos_ibama(PessoaConsultada)) == 0:
            Ibama_analysisAGG = "Não existem eventos para a pessoa pesquisada"
        else:
            Ibama_analysisAGG = Ibama_analysis

        if len(self.retriever.eventos_trabalho_escravo(PessoaConsultada)) == 0:
            MTE_analysisAGG = MTEAnalysis(eventos_mte=[{}])
        else:
            MTE_analysisAGG = MTE_analysis

        if len(self.retriever.eventos_cnep(PessoaConsultada)) == 0:
            CNEP_analysisAGG = "Não existem eventos para a pessoa pesquisada"
        else:
            CNEP_analysisAGG = CNEP_analysis

        if len(self.retriever.eventos_ceis(PessoaConsultada)) == 0:
            CEIS_analysisAGG = "Não existem eventos para a pessoa pesquisada"
        else:
            CEIS_analysisAGG = CEIS_analysis                        

        aggregation_input = f"""
        STREAM 1 - Quantitative ANALYSIS for {PessoaConsultada}:
        Nota preliminar calculada pelas regras determinísticas: {Nota_Quant}/10

        STREAM 2 - IBAMA ANALYSIS for {PessoaConsultada}:
        {Ibama_analysisAGG}
        
        STREAM 3 - MTE ANALYSIS for {PessoaConsultada}:
        {MTE_analysisAGG}

        STREAM 4 - CNEP ANALYSIS for {PessoaConsultada}:
        {CNEP_analysisAGG}

        STREAM 5 - CEIS ANALYSIS for {PessoaConsultada}:
        {CEIS_analysisAGG}
        """

        system_prompt = self.prompt_manager.get_prompt("final_recommendationESG")

        # Use Instructor for clean structured output - no manual JSON prompts needed!
        return self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": aggregation_input},
            ],
            response_model=FinalRecommendationESG,  # Instructor handles everything!
        )