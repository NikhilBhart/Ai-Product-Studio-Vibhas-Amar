from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Persona(StrictModel):
    name: str
    description: str
    goals: list[str] = Field(min_length=1)
    frustrations: list[str] = Field(default_factory=list)


class UserStory(StrictModel):
    story: str
    priority: Literal["MUST", "SHOULD", "COULD"] = "SHOULD"
    acceptance_criteria: list[str] = Field(min_length=1)


class Feature(StrictModel):
    name: str
    description: str
    user_stories: list[UserStory] = Field(min_length=1)


class Capability(StrictModel):
    name: str
    description: str
    features: list[Feature] = Field(min_length=1)


class Epic(StrictModel):
    name: str
    business_outcome: str
    capabilities: list[Capability] = Field(min_length=1)


class ProductBrief(StrictModel):
    product_name: str
    tagline: str
    vision: str
    problem_statement: str
    target_users: list[str] = Field(min_length=1)
    personas: list[Persona] = Field(min_length=1)
    user_pain_points: list[str] = Field(min_length=1)
    desired_outcomes: list[str] = Field(min_length=1)
    business_value: list[str] = Field(min_length=1)
    success_metrics: list[str] = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    mvp_scope: list[str] = Field(min_length=1)
    out_of_scope: list[str] = Field(default_factory=list)
    future_enhancements: list[str] = Field(default_factory=list)
    epics: list[Epic] = Field(min_length=1)
    status: Literal["DRAFT", "READY_FOR_REVIEW"] = "READY_FOR_REVIEW"


class IdeaRequest(StrictModel):
    project_id: str | None = None
    idea: str = Field(min_length=5, max_length=8000)
    product_name_hint: str | None = Field(default=None, max_length=180)
    context: dict[str, str] = Field(default_factory=dict)


class DiscoveryResponse(StrictModel):
    product_brief: ProductBrief
    status: Literal["COMPLETED", "DRAFT"]
    provider: str
    model: str
    warnings: list[str] = Field(default_factory=list)
