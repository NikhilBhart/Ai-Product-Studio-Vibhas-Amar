from __future__ import annotations

from typing import Any, TypedDict
from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from app.llm import generate_brief
from app.schemas import DiscoveryResponse, IdeaRequest


class DiscoveryState(TypedDict, total=False):
    request: dict[str, Any]
    product_brief: dict[str, Any]
    provider: str
    model: str
    warnings: list[str]
    status: str
    error: str


def generate_product_brief(state: DiscoveryState) -> DiscoveryState:
    request = IdeaRequest.model_validate(state["request"])
    brief, provider, model, warnings = generate_brief(request)
    return {
        "product_brief": brief.model_dump(mode="json"),
        "provider": provider,
        "model": model,
        "warnings": warnings,
        "status": "BRIEF_GENERATED"
    }


def validate_product_brief(state: DiscoveryState) -> DiscoveryState:
    brief = DiscoveryResponse(
        product_brief=state["product_brief"],
        status="COMPLETED",
        provider=state["provider"],
        model=state["model"],
        warnings=state.get("warnings", [])
    )
    return {"product_brief": brief.product_brief.model_dump(mode="json"), "status": "COMPLETED"}


def build_discovery_graph():
    graph = StateGraph(DiscoveryState)
    graph.add_node("generate_product_brief", generate_product_brief)
    graph.add_node("validate_product_brief", validate_product_brief)
    graph.add_edge(START, "generate_product_brief")
    graph.add_edge("generate_product_brief", "validate_product_brief")
    graph.add_edge("validate_product_brief", END)
    return graph.compile()


discovery_graph = build_discovery_graph()
