from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

from app.schemas import IdeaRequest, ProductBrief


SYSTEM_PROMPT = """You are a senior product manager and product discovery specialist.
Turn an incomplete product idea into a practical, internally consistent first-pass product brief.
Do not ask follow-up questions. Make sensible, conservative assumptions and list them explicitly.
Separate facts inferred from the user's idea from assumptions and material uncertainties.
Do not claim market research, legal review, customer validation, or competitor analysis was performed unless evidence is provided.
Use original product naming and functionality; do not copy protected branding or proprietary assets.
Prioritize a coherent MVP. Avoid scope inflation. Include testable acceptance criteria for every user story.
Return ONLY one valid JSON object matching the requested schema. No markdown fences or commentary."""


class LLMConfigurationError(RuntimeError):
    pass


class LLMProviderError(RuntimeError):
    pass


def _fallback_list(idea: str, kind: str) -> list[str]:
    if kind == "pain":
        return ["Users currently rely on fragmented tools or manual steps to complete the core task.",
                "Users lack a simple, consistent experience for the primary workflow."]
    if kind == "outcome":
        return ["Enable users to complete the primary workflow with fewer steps.",
                "Provide a clear, reliable experience across desktop and mobile."]
    if kind == "value":
        return ["Validate demand with a focused MVP before investing in advanced capabilities.",
                "Create a foundation that can scale based on measured user behaviour."]
    return [f"The product should help users achieve the core outcome described by: {idea[:180]}"]


def demo_brief(request: IdeaRequest) -> ProductBrief:
    """Deterministic local demo. It is deliberately labelled as demo output, not AI analysis."""
    idea = request.idea.strip()
    lower = idea.lower()
    name = request.product_name_hint or "Idea Studio Project"
    if not request.product_name_hint:
        if "instagram" in lower or "photo" in lower or "social" in lower:
            name = "Social Photo Platform"
        elif "food" in lower or "restaurant" in lower:
            name = "Food Discovery Platform"
        elif "task" in lower or "project" in lower:
            name = "Project Workspace"
        else:
            name = "Product Concept"

    core_feature = "Create and manage the primary content" if any(x in lower for x in ["photo", "social", "instagram", "post"]) else "Complete the primary user workflow"
    feature_set = [
        {"name": "Account and onboarding", "description": "Let users create an account and establish a basic profile.",
         "user_stories": [{"story": "As a new user, I want to create an account so that I can access my personal workspace.", "priority": "MUST", "acceptance_criteria": ["A user can register with valid details.", "Invalid or duplicate details produce a clear validation message.", "A registered user can sign in and sign out."]}]},
        {"name": "Core experience", "description": core_feature + " through a simple, discoverable interface.",
         "user_stories": [{"story": "As a user, I want to " + core_feature.lower() + " so that I can get the main value of the product.", "priority": "MUST", "acceptance_criteria": ["The primary action is available from the main workspace.", "The system validates required inputs before saving.", "The user receives a clear success or error state."]}]},
        {"name": "Search and navigation", "description": "Help users find relevant content and move between key areas.",
         "user_stories": [{"story": "As a user, I want to find relevant items so that I can return to useful content quickly.", "priority": "SHOULD", "acceptance_criteria": ["Users can search by a relevant keyword.", "Empty results show a helpful message.", "Navigation remains usable on mobile screens."]}]}
    ]
    return ProductBrief(
        product_name=name,
        tagline="A focused first version built around the user's core job.",
        vision=f"Help the intended audience achieve the outcome behind this idea: {idea[:260]}",
        problem_statement="The intended users need a more straightforward and dependable way to complete the central task described in the idea. This problem statement is a hypothesis until validated with users.",
        target_users=["People who experience the problem described in the idea", "Administrators or operators responsible for managing the service"],
        personas=[
            {"name": "Primary user", "description": "A person who needs the product's main outcome.", "goals": ["Complete the main task quickly", "Understand the next step without training"], "frustrations": ["Fragmented workflows", "Unclear feedback"]},
            {"name": "Administrator", "description": "A person who configures and oversees the product.", "goals": ["Manage access and content", "Understand basic product activity"], "frustrations": ["Manual administration", "Limited visibility"]}
        ],
        user_pain_points=_fallback_list(idea, "pain"),
        desired_outcomes=_fallback_list(idea, "outcome"),
        business_value=_fallback_list(idea, "value"),
        success_metrics=["Activation rate: percentage of new users completing the first key action", "Task completion rate for the primary workflow", "Weekly active users or repeat usage", "Median time to complete the primary task"],
        assumptions=["The first release is a responsive web application.", "The MVP serves one primary user segment before expanding.", "Standard authentication and role-based access are sufficient initially.", "No payment processing is required unless explicitly stated."],
        uncertainties=["Exact target segment and geographic market need validation.", "Monetization and pricing model are not specified.", "Expected scale, availability requirements, and data retention are unknown.", "Any regulated or sensitive data requirements must be confirmed before production."],
        mvp_scope=["User registration and sign-in", "Primary user workspace", "Core create/read/update workflow", "Basic search and navigation", "Responsive layout", "Basic error handling and audit-friendly events"],
        out_of_scope=["Native mobile applications", "Complex recommendation or personalization systems", "Enterprise SSO and advanced analytics", "Payments unless required by the validated business model"],
        future_enhancements=["Notifications and collaboration", "Advanced analytics", "Personalization and automation", "Additional integrations based on user feedback"],
        epics=[
            {"name": "Enable user access", "business_outcome": "Users can securely access a personalized product experience.", "capabilities": [{"name": "Identity and onboarding", "description": "Create and manage user access.", "features": [feature_set[0]]}]},
            {"name": "Deliver the core product value", "business_outcome": "Users can complete the primary job the product exists to solve.", "capabilities": [{"name": "Primary workflow", "description": "Support the central user task from start to finish.", "features": [feature_set[1]]}, {"name": "Discovery and navigation", "description": "Help users locate information and move through the product.", "features": [feature_set[2]]}]}
        ],
        status="READY_FOR_REVIEW"
    )


def _extract_json(content: str) -> dict[str, Any]:
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def generate_brief(request: IdeaRequest) -> tuple[ProductBrief, str, str, list[str]]:
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    model = os.getenv("LLM_MODEL", "demo-product-manager")
    if provider == "mock":
        return demo_brief(request), "mock", model, ["DEMO_MODE: This brief was generated by deterministic local rules, not an LLM. Configure an LLM provider for semantic product discovery."]

    if provider not in {"openai-compatible", "openai", "gemini-compatible", "groq-compatible", "custom"}:
        raise LLMConfigurationError(f"Unsupported LLM_PROVIDER '{provider}'. Use mock or an OpenAI-compatible provider.")

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GROQ_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    if not api_key:
        raise LLMConfigurationError("LLM_API_KEY is required when LLM_PROVIDER is not mock.")
    if not model or model == "demo-product-manager":
        raise LLMConfigurationError("Set LLM_MODEL to a model available from the selected provider.")

    user_prompt = {
        "idea": request.idea,
        "product_name_hint": request.product_name_hint,
        "additional_context": request.context,
        "required_schema": ProductBrief.model_json_schema(),
        "instructions": "Produce a complete first-pass product brief. Include 2-4 epics, 1-3 capabilities per epic, 1-4 features per capability, and 1-3 user stories per feature. Acceptance criteria must be observable and testable. Keep the MVP realistic."
    }
    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
        ]
    }
    try:
        with httpx.Client(timeout=httpx.Timeout(90.0, connect=15.0)) as client:
            response = client.post(f"{base_url}/chat/completions", headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        brief = ProductBrief.model_validate(_extract_json(content))
        return brief, provider, model, []
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise LLMProviderError(f"LLM request or structured response validation failed: {type(exc).__name__}: {exc}") from exc
