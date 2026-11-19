from app.llm import demo_brief
from app.schemas import DiscoveryResponse, IdeaRequest


def test_demo_discovery_returns_valid_hierarchical_product_brief():
    request = IdeaRequest(idea="Build a photo sharing social network")
    brief = demo_brief(request)
    result = DiscoveryResponse(
        product_brief=brief,
        status="COMPLETED",
        provider="mock",
        model="demo-product-manager",
        warnings=["DEMO_MODE"],
    )
    assert result.product_brief.product_name == "Social Photo Platform"
    assert len(result.product_brief.epics) >= 1
    assert all(cap.features for epic in result.product_brief.epics for cap in epic.capabilities)
    assert all(story.acceptance_criteria for epic in result.product_brief.epics for cap in epic.capabilities for feature in cap.features for story in feature.user_stories)
    assert "DEMO_MODE" in result.warnings[0]


def test_product_name_hint_is_respected():
    request = IdeaRequest(idea="Build an online learning platform", product_name_hint="LearnSpace")
    assert demo_brief(request).product_name == "LearnSpace"
