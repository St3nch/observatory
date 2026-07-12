from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from .core import APPROVAL_REFERENCE, ProbeBlocked

CAMPAIGN_ID = "m13-dataforseo-exploratory-campaign-v0-1"
CAMPAIGN_APPROVAL_REFERENCE = "decisions/2026-07-12-m13-dataforseo-exploratory-campaign.md"
CAMPAIGN_BUDGET_USD = Decimal("50.00")
MAX_LATER_BATCH_RECIPES = 3
MAX_LATER_BATCH_COST_USD = Decimal("2.00")
CALIBRATION_SUCCESS_COUNT = 3


@dataclass(frozen=True)
class CampaignStage:
    stage_id: str
    name: str
    learning_objective: str
    spend_ceiling_usd: Decimal
    review_mode: str


@dataclass(frozen=True)
class CampaignRecipe:
    recipe_id: str
    stage_id: str
    family: str
    endpoint: str
    method: str
    request_payload: tuple[tuple[str, Any], ...]
    question_answered: str
    conservative_request_ceiling_usd: Decimal
    requires_prior_recipe: str | None
    source_documentation: str
    rights_class: str
    retention_class: str
    claim_use_warning: str
    live_status: str = "candidate"

    def request(self) -> list[dict[str, Any]]:
        task: dict[str, Any] = {}
        for key, value in self.request_payload:
            if isinstance(value, tuple):
                task[key] = list(value)
            else:
                task[key] = value
        return [task]

    def request_sha256(self) -> str:
        payload = json.dumps(self.request(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def duplicate_key(self) -> str:
        material = {
            "provider": "DataForSEO",
            "endpoint": self.endpoint,
            "request_payload_sha256": self.request_sha256(),
            "approval_reference": CAMPAIGN_APPROVAL_REFERENCE,
            "recipe_id": self.recipe_id,
        }
        payload = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def summary(self) -> dict[str, Any]:
        return {
            "campaign_id": CAMPAIGN_ID,
            "campaign_approval_reference": CAMPAIGN_APPROVAL_REFERENCE,
            "probe_approval_reference": APPROVAL_REFERENCE,
            "recipe_id": self.recipe_id,
            "stage_id": self.stage_id,
            "family": self.family,
            "provider": "DataForSEO",
            "endpoint": self.endpoint,
            "method": self.method,
            "request": self.request(),
            "request_sha256": self.request_sha256(),
            "duplicate_prevention_key": self.duplicate_key(),
            "question_answered": self.question_answered,
            "conservative_request_ceiling_usd": str(self.conservative_request_ceiling_usd),
            "requires_prior_recipe": self.requires_prior_recipe,
            "source_documentation": self.source_documentation,
            "rights_class": self.rights_class,
            "retention_class": self.retention_class,
            "claim_use_warning": self.claim_use_warning,
            "live_status": self.live_status,
            "network_execution_authorized": False,
        }


STAGES: tuple[CampaignStage, ...] = (
    CampaignStage("S0", "Billing sentinel", "Calibrate billing, usage reconciliation, raw evidence, and purge", Decimal("2.00"), "one_request_then_review"),
    CampaignStage("S1", "Core SERP surfaces", "Compare Google, Bing, and YouTube result envelopes", Decimal("8.00"), "one_request_then_review_until_three_successes"),
    CampaignStage("S2", "Variance and result families", "Test device, location, local, and AI-mode variance", Decimal("8.00"), "bounded_batch_after_promotion"),
    CampaignStage("S3", "Keyword and provider metrics", "Inspect keyword metrics, estimates, intent, and suggestion relationships", Decimal("10.00"), "bounded_batch_after_promotion"),
    CampaignStage("S4", "AI and GEO surfaces", "Inspect answer, citation, mention, and model evidence boundaries", Decimal("10.00"), "bounded_batch_after_promotion"),
    CampaignStage("S5", "Local, video, merchant, marketplace", "Rank later instrument candidates without broad admission", Decimal("7.00"), "bounded_batch_after_promotion"),
    CampaignStage("SR", "Reserve", "Justified repeats, provider drift, errors, or a missing high-value comparison", Decimal("5.00"), "explicit_justification_required"),
)


def _payload(**values: Any) -> tuple[tuple[str, Any], ...]:
    normalized: list[tuple[str, Any]] = []
    for key, value in values.items():
        if isinstance(value, list):
            normalized.append((key, tuple(value)))
        else:
            normalized.append((key, value))
    return tuple(normalized)


RECIPES: tuple[CampaignRecipe, ...] = (
    CampaignRecipe(
        "C00",
        "S0",
        "serp_google_organic",
        "/v3/serp/google/organic/live/advanced",
        "POST",
        _payload(keyword="observatory test page", location_code=2840, language_code="en", device="desktop", os="windows", depth=10),
        "Calibrate one-task billing, provider usage reconciliation, response envelope, raw hashing, and purge.",
        Decimal("0.10"),
        None,
        "https://docs.dataforseo.com/v3/serp/google/organic/live/advanced/",
        "provider_limited_internal_probe",
        "capture_and_purge_raw",
        "provider_testimony_only_not_truth",
        "promoted_for_preflight",
    ),
    CampaignRecipe(
        "C01",
        "S1",
        "serp_google_organic",
        "/v3/serp/google/organic/live/advanced",
        "POST",
        _payload(keyword="observatory test page", location_code=2840, language_code="en", device="mobile", os="android", depth=10),
        "Compare Google desktop and mobile response/item shape while holding query and locale constant.",
        Decimal("0.25"),
        "C00",
        "https://docs.dataforseo.com/v3/serp/google/organic/live/advanced/",
        "provider_limited_internal_probe",
        "capture_and_purge_raw",
        "single_sample_device_comparison_not_visibility_truth",
    ),
    CampaignRecipe(
        "C02",
        "S1",
        "serp_bing_organic",
        "/v3/serp/bing/organic/live/advanced",
        "POST",
        _payload(keyword="observatory test page", location_code=2840, language_code="en", device="desktop", os="windows", depth=10),
        "Compare engine-specific normalization and item types between Google and Bing.",
        Decimal("0.25"),
        "C01",
        "https://docs.dataforseo.com/v3/serp/bing/organic/live/advanced/",
        "provider_limited_internal_probe",
        "capture_and_purge_raw",
        "cross_engine_provider_shapes_not_equivalent_truth",
    ),
    CampaignRecipe(
        "C03",
        "S1",
        "serp_youtube_organic",
        "/v3/serp/youtube/organic/live/advanced",
        "POST",
        _payload(keyword="what is an observatory", location_code=2840, language_code="en", device="desktop"),
        "Inspect YouTube search result, video, channel, and ranking evidence shape.",
        Decimal("0.50"),
        "C02",
        "https://docs.dataforseo.com/v3/serp/youtube/organic/live/advanced/",
        "provider_limited_internal_probe",
        "capture_and_purge_raw",
        "youtube_provider_sample_not_creator_analytics_or_truth",
    ),
    CampaignRecipe(
        "C04",
        "S2",
        "serp_google_maps",
        "/v3/serp/google/maps/live/advanced",
        "POST",
        _payload(keyword="public library", location_code=2840, language_code="en", device="desktop"),
        "Inspect local result, place, rank, category, address, coordinate, and rating field shape.",
        Decimal("0.50"),
        "C03",
        "https://docs.dataforseo.com/v3/serp/google/maps/live/advanced/",
        "provider_limited_internal_probe",
        "capture_and_purge_raw",
        "single_local_sample_not_local_visibility_truth",
    ),
    CampaignRecipe(
        "C05",
        "S2",
        "serp_google_ai_mode",
        "/v3/serp/google/ai_mode/live/advanced",
        "POST",
        _payload(keyword="what is an observatory", location_code=2840, language_code="en", device="desktop"),
        "Inspect AI Mode answer blocks, references, citations, sources, and follow-up structures.",
        Decimal("1.00"),
        "C04",
        "https://docs.dataforseo.com/v3/serp/google/ai_mode/live/advanced/",
        "provider_limited_internal_probe",
        "capture_and_purge_raw",
        "single_generated_answer_sample_requires_sampling_caveat",
    ),
    CampaignRecipe(
        "C06",
        "S3",
        "labs_google_keyword_overview",
        "/v3/dataforseo_labs/google/keyword_overview/live",
        "POST",
        _payload(keywords=["observatory"], location_code=2840, language_code="en"),
        "Inspect search-volume, competition, CPC, difficulty, intent, and trend metric provenance.",
        Decimal("1.00"),
        "C05",
        "https://docs.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live/",
        "provider_metric_internal_probe",
        "capture_and_purge_raw",
        "provider_estimates_and_classifications_not_observed_web_truth",
    ),
    CampaignRecipe(
        "C07",
        "S3",
        "labs_google_keyword_ideas",
        "/v3/dataforseo_labs/google/keyword_ideas/live",
        "POST",
        _payload(keywords=["observatory"], location_code=2840, language_code="en", limit=10),
        "Inspect seed-to-suggestion relationships and repeated keyword metric fields.",
        Decimal("1.00"),
        "C06",
        "https://docs.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live/",
        "provider_metric_internal_probe",
        "capture_and_purge_raw",
        "keyword_ideas_are_provider_generated_candidates_not_recommendations",
    ),
)


def stage_map() -> dict[str, CampaignStage]:
    return {stage.stage_id: stage for stage in STAGES}


def recipe_map() -> dict[str, CampaignRecipe]:
    return {recipe.recipe_id: recipe for recipe in RECIPES}


def get_recipe(recipe_id: str) -> CampaignRecipe:
    try:
        return recipe_map()[recipe_id]
    except KeyError as exc:
        raise ProbeBlocked(f"unknown campaign recipe: {recipe_id}") from exc


def campaign_budget_summary() -> dict[str, Any]:
    stages = [
        {
            "stage_id": stage.stage_id,
            "name": stage.name,
            "spend_ceiling_usd": str(stage.spend_ceiling_usd),
            "review_mode": stage.review_mode,
        }
        for stage in STAGES
    ]
    total = sum((stage.spend_ceiling_usd for stage in STAGES), Decimal("0.00"))
    return {
        "campaign_id": CAMPAIGN_ID,
        "campaign_budget_usd": str(CAMPAIGN_BUDGET_USD),
        "allocated_budget_usd": str(total),
        "budget_balanced": total == CAMPAIGN_BUDGET_USD,
        "stages": stages,
        "network_execution_authorized": False,
    }


def list_recipes() -> list[dict[str, Any]]:
    return [recipe.summary() for recipe in RECIPES]


def validate_catalog() -> dict[str, Any]:
    errors: list[str] = []
    stage_ids = [stage.stage_id for stage in STAGES]
    recipe_ids = [recipe.recipe_id for recipe in RECIPES]

    if len(stage_ids) != len(set(stage_ids)):
        errors.append("duplicate_stage_id")
    if len(recipe_ids) != len(set(recipe_ids)):
        errors.append("duplicate_recipe_id")

    stages = stage_map()
    if sum((stage.spend_ceiling_usd for stage in STAGES), Decimal("0.00")) != CAMPAIGN_BUDGET_USD:
        errors.append("campaign_budget_not_balanced")

    prohibited_markers = ("customer", "searchclarity", "password", "credential", "secret")
    for recipe in RECIPES:
        if recipe.stage_id not in stages:
            errors.append(f"unknown_stage:{recipe.recipe_id}")
        if not recipe.endpoint.startswith("/v3/"):
            errors.append(f"invalid_endpoint:{recipe.recipe_id}")
        if recipe.method != "POST":
            errors.append(f"invalid_method:{recipe.recipe_id}")
        if recipe.conservative_request_ceiling_usd <= Decimal("0.00"):
            errors.append(f"invalid_cost_ceiling:{recipe.recipe_id}")
        serialized = json.dumps(recipe.request(), sort_keys=True).lower()
        if any(marker in serialized for marker in prohibited_markers):
            errors.append(f"prohibited_marker:{recipe.recipe_id}")
        if recipe.requires_prior_recipe and recipe.requires_prior_recipe not in recipe_ids:
            errors.append(f"missing_prior_recipe:{recipe.recipe_id}")

    if get_recipe("C00").live_status != "promoted_for_preflight":
        errors.append("c00_not_promoted_for_preflight")
    if any(recipe.live_status != "candidate" for recipe in RECIPES if recipe.recipe_id != "C00"):
        errors.append("later_recipe_promoted_too_early")

    return {
        "campaign_id": CAMPAIGN_ID,
        "valid": not errors,
        "errors": errors,
        "stage_count": len(STAGES),
        "recipe_count": len(RECIPES),
        "campaign_budget_usd": str(CAMPAIGN_BUDGET_USD),
        "network_execution_authorized": False,
    }


def validate_batch(recipe_ids: list[str], successful_reconciled_pulls: int, conservative_cost_usd: Decimal) -> None:
    if not recipe_ids:
        raise ProbeBlocked("campaign batch must contain at least one recipe")
    if len(recipe_ids) != len(set(recipe_ids)):
        raise ProbeBlocked("campaign batch contains duplicate recipe ids")
    for recipe_id in recipe_ids:
        get_recipe(recipe_id)
    if successful_reconciled_pulls < CALIBRATION_SUCCESS_COUNT and len(recipe_ids) != 1:
        raise ProbeBlocked("calibration mode permits exactly one recipe")
    if successful_reconciled_pulls >= CALIBRATION_SUCCESS_COUNT:
        if len(recipe_ids) > MAX_LATER_BATCH_RECIPES:
            raise ProbeBlocked("bounded campaign batch exceeds three recipes")
        if conservative_cost_usd > MAX_LATER_BATCH_COST_USD:
            raise ProbeBlocked("bounded campaign batch exceeds $2.00 conservative ceiling")
    if conservative_cost_usd <= Decimal("0.00"):
        raise ProbeBlocked("campaign batch cost ceiling must be positive")


def conservative_spend(response_costs: list[Decimal], usage_costs: list[Decimal]) -> Decimal:
    if len(response_costs) != len(usage_costs):
        raise ProbeBlocked("response and usage cost witness counts differ")
    total = Decimal("0.00")
    for response_cost, usage_cost in zip(response_costs, usage_costs, strict=True):
        if response_cost < 0 or usage_cost < 0:
            raise ProbeBlocked("cost witness cannot be negative")
        total += max(response_cost, usage_cost)
    if total > CAMPAIGN_BUDGET_USD:
        raise ProbeBlocked("conservative campaign spend exceeds $50.00")
    return total
