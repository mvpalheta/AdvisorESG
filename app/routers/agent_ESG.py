from fastapi import APIRouter, Depends, HTTPException
#from app.models.agent import AgentRequest, AgentResponse
from app.models.agent import AgentRequestESG, AgentResponseESG
from app.services.agent_serviceESG import AgentServiceESG
#from app.services.retriever import QdrantRetriever
#from app.services.embedder import QueryEmbedder
from app.config.settings import Settings

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agentESG", tags=["agentESG"])


def get_settings():
    return Settings()

def get_agent_service(
    settings: Settings = Depends(get_settings),
):
    return AgentServiceESG(settings=settings)


@router.post("", response_model=AgentResponseESG)
async def ESG_analyze(
    request: AgentRequestESG,
    agent_service: AgentServiceESG = Depends(get_agent_service),
):
    """
    Run complete ESG analysis with 4 streams:
    - Stream 1: Enviroment Analysis (IBAMA)
    - Stream 2: Social Analysis (MTE)
    - Stream 3: Governance Analysis (CNEP)
    - Stream 4: Governance Analysis (CEIS)
    - Aggregation: Final recommendation
    """
    try:
        if not request.PessoaConsultada and not request.message:
            raise HTTPException(
                status_code=400, detail="Either pessoa or message must be provided"
            )

        # Service handles all business logic
        result = agent_service.ESG_Analyzer(
            PessoaConsultada=request.PessoaConsultada,
            #message=request.message,
        )

        logger.info(
            f"Completed ESG analysis for {result.pessoa} in {result.execution_time:.2f}s"
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ESG analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"ESG analysis failed: {str(e)}"
        )
