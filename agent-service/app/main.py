from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.graph import discovery_graph
from app.schemas import DiscoveryResponse, IdeaRequest, ProductBrief
from app.llm import LLMConfigurationError, LLMProviderError

app = FastAPI(
    title="AI Product Studio Agent Service",
    description="LangGraph-powered product discovery and backlog generation.",
    version="0.2.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "UP", "service": "agent-service", "phase": 2}


@app.get("/v1/discovery/schema")
def discovery_schema():
    return ProductBrief.model_json_schema()


@app.post("/v1/discovery/run", response_model=DiscoveryResponse)
def run_discovery(request: IdeaRequest):
    try:
        state = discovery_graph.invoke({"request": request.model_dump(mode="json"), "status": "STARTED"})
        return DiscoveryResponse(
            product_brief=state["product_brief"],
            status="COMPLETED",
            provider=state["provider"],
            model=state["model"],
            warnings=state.get("warnings", []),
        )
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=424, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except (ValidationError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Product brief validation failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Discovery workflow failed. Check agent-service logs.") from exc
