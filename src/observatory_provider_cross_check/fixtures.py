from __future__ import annotations

from .models import ProviderSide

SCOPE_A = "scope_provider_alpha"
SCOPE_B = "scope_provider_beta"

_BASE_CONTEXT = {
    "subject_type": "keyword",
    "subject_value": "synthetic visibility query",
    "surface_family": "synthetic_serp",
    "locale": "en-US",
    "language": "en",
    "device": "desktop",
    "location": "US",
}


def _side(**overrides: object) -> ProviderSide:
    values = {
        "side_id": "side_a",
        "scope_id": SCOPE_A,
        "provider_name": "Synthetic Provider A",
        "provider_family": "synthetic_fixture",
        "endpoint_or_surface": "synthetic/rank",
        "metric_name": "rank_position",
        "metric_value": 8,
        "metric_unit": "position",
        "metric_definition": "ordinal position in bounded synthetic result set",
        "metric_posture": "provider_reported_value",
        "captured_at": "2026-07-12T18:00:00+00:00",
        "provider_reported_time": "2026-07-12T18:00:00+00:00",
        "freshness_status": "fresh",
        "volatility_class": "high",
        "rights_class": "synthetic_fixture_allowed",
        "retention_class": "synthetic_fixture_durable",
        "source_admission_status": "admitted_synthetic_fixture",
        "evidence_status": "active",
        "evidence_handle": "evh_m16_a_91f0",
        "context": dict(_BASE_CONTEXT),
    }
    values.update(overrides)
    return ProviderSide(**values)  # type: ignore[arg-type]


SIDES = {
    "rank_a": _side(),
    "rank_b": _side(
        side_id="side_b", provider_name="Synthetic Provider B", metric_value=11,
        evidence_handle="evh_m16_b_62ad",
    ),
    "estimate_a": _side(
        side_id="estimate_a", metric_name="volume_estimate", metric_value=90,
        metric_unit="estimated_monthly_searches", metric_definition="synthetic estimate over declared locale",
        metric_posture="provider_estimate", evidence_handle="evh_m16_c_10b7",
    ),
    "estimate_b": _side(
        side_id="estimate_b", provider_name="Synthetic Provider B", metric_name="volume_estimate",
        metric_value=140, metric_unit="estimated_monthly_searches",
        metric_definition="synthetic estimate over declared locale", metric_posture="provider_estimate",
        evidence_handle="evh_m16_d_a250",
    ),
    "difficulty_a": _side(
        side_id="difficulty_a", metric_name="keyword_difficulty", metric_value=42,
        metric_unit="proprietary_score", metric_definition=None, metric_posture="provider_model_output",
        evidence_handle="evh_m16_e_432d",
    ),
    "difficulty_b": _side(
        side_id="difficulty_b", provider_name="Synthetic Provider B", metric_name="keyword_difficulty",
        metric_value=71, metric_unit="proprietary_score", metric_definition=None,
        metric_posture="provider_model_output", evidence_handle="evh_m16_f_4ac1",
    ),
    "late_b": _side(
        side_id="late_b", provider_name="Synthetic Provider B", metric_value=11,
        captured_at="2026-07-05T18:00:00+00:00", provider_reported_time="2026-07-04T18:00:00+00:00",
        freshness_status="stale", evidence_handle="evh_m16_g_9b11",
    ),
    "absence_b": _side(
        side_id="absence_b", provider_name="Synthetic Provider B", metric_name="sampled_presence",
        metric_value=False, metric_unit=None, metric_definition="presence in bounded synthetic result sample",
        metric_posture="provider_sampled_observation", evidence_handle="evh_m16_h_a83f",
    ),
    "presence_a": _side(
        side_id="presence_a", metric_name="sampled_presence", metric_value=True, metric_unit=None,
        metric_definition="presence in bounded synthetic result sample",
        metric_posture="provider_sampled_observation", evidence_handle="evh_m16_i_803e",
    ),
    "rights_blocked": _side(
        side_id="rights_blocked", rights_class="blocked", evidence_status="blocked_by_rights",
        evidence_handle="evh_m16_j_33af",
    ),
    "unadmitted": _side(
        side_id="unadmitted", source_admission_status="not_admitted", evidence_handle="evh_m16_k_c111",
    ),
    "drift_blocked": _side(
        side_id="drift_blocked", evidence_status="blocked_by_payload_drift", evidence_handle="evh_m16_l_731b",
    ),
    "scope_b": _side(
        side_id="scope_b", scope_id=SCOPE_B, provider_name="Synthetic Provider B",
        evidence_handle="evh_m16_m_102c",
    ),
}
