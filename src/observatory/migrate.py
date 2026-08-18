"""Apply the rebuildable PostgreSQL schema for Outcomes and Observations."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Final

import psycopg
from psycopg import Connection

from observatory.settings import get_settings

DERIVATION_VERSIONS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS derivation_versions (
    derivation_version_id TEXT PRIMARY KEY
        CHECK (derivation_version_id ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    adapter_contract TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL
)
"""

OUTCOMES_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS outcomes (
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '^[0-9a-f]{64}$'),
    capture_id TEXT
        CHECK (capture_id IS NULL OR capture_id ~ '^[0-9a-f]{64}$'),
    derivation_version_id TEXT NOT NULL
        REFERENCES derivation_versions (derivation_version_id),
    classification TEXT NOT NULL,
    observation_count BIGINT NOT NULL
        CHECK (observation_count >= 0 AND observation_count <= 9007199254740991),
    CONSTRAINT outcomes_identity
        UNIQUE NULLS NOT DISTINCT (derivation_version_id, attempt_id, capture_id)
)
"""

OUTCOMES_IDENTITY_SQL: Final[str] = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'outcomes_identity'
    ) THEN
        ALTER TABLE outcomes
            ADD CONSTRAINT outcomes_identity
            UNIQUE NULLS NOT DISTINCT (derivation_version_id, attempt_id, capture_id);
    END IF;
END $$
"""

OBSERVATIONS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS observations (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{64}$'),
    derivation_version_id TEXT NOT NULL
        REFERENCES derivation_versions (derivation_version_id),
    within_capture_result_id TEXT NOT NULL
        CHECK (within_capture_result_id ~ '^result:[1-9][0-9]*$'),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '^[0-9a-f]{64}$'),
    provider TEXT NOT NULL,
    panel_id TEXT NOT NULL,
    subject_key TEXT NOT NULL,
    result_index BIGINT NOT NULL
        CHECK (result_index >= 1 AND result_index <= 9007199254740991),
    label TEXT NOT NULL,
    score BIGINT NOT NULL
        CHECK (score >= -9007199254740991 AND score <= 9007199254740991),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_result_id)
)
"""

PROVIDER_RECIPES_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS provider_recipes (
    derivation_version_id TEXT PRIMARY KEY
        CHECK (derivation_version_id ~ '^[0-9a-f]{64}$')
        REFERENCES derivation_versions (derivation_version_id),
    provider TEXT NOT NULL
        CHECK (provider ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    adapter_contract TEXT NOT NULL
        CHECK (adapter_contract ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    recipe_canonical_bytes BYTEA NOT NULL
        CHECK (octet_length(recipe_canonical_bytes) >= 1)
)
"""

PROVIDER_RECIPES_ADAPTER_VERSION_SQL: Final[str] = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'provider_recipes_adapter_version'
    ) THEN
        ALTER TABLE provider_recipes
            ADD CONSTRAINT provider_recipes_adapter_version
            UNIQUE (adapter_contract, derivation_version_id);
    END IF;
END $$
"""

PROVIDER_RECIPE_SELECTIONS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS provider_recipe_selections (
    adapter_contract TEXT PRIMARY KEY
        CHECK (adapter_contract ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    derivation_version_id TEXT NOT NULL
        CHECK (derivation_version_id ~ '^[0-9a-f]{64}$'),
    CONSTRAINT provider_recipe_selections_recipe
        FOREIGN KEY (adapter_contract, derivation_version_id)
        REFERENCES provider_recipes (adapter_contract, derivation_version_id)
)
"""

OBSERVATION_ENVELOPES_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS observation_envelopes (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{64}$'),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '^[0-9a-f]{64}$'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    provider TEXT NOT NULL
        CHECK (provider ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    adapter_contract TEXT NOT NULL
        CHECK (adapter_contract ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    observation_kind TEXT NOT NULL
        CHECK (observation_kind ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{64}$'),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT observation_envelopes_kind_identity
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

OBSERVATION_ENVELOPES_KIND_IDENTITY_SQL: Final[str] = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'observation_envelopes_kind_identity'
    ) THEN
        ALTER TABLE observation_envelopes
            ADD CONSTRAINT observation_envelopes_kind_identity
            UNIQUE (
                capture_id, derivation_version_id,
                within_capture_identity, observation_kind
            );
    END IF;
END $$
"""

DERIVATION_DIAGNOSTICS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS derivation_diagnostics (
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT
        CHECK (attempt_id IS NULL OR attempt_id ~ '^[0-9a-f]{64}$'),
    capture_id TEXT
        CHECK (capture_id IS NULL OR capture_id ~ '^[0-9a-f]{64}$'),
    diagnostic_code TEXT NOT NULL
        CHECK (diagnostic_code ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    provider_body_path TEXT NOT NULL
        CHECK (provider_body_path ~ '^(|(/([^/~]|~[01])*)+)$'),
    CONSTRAINT derivation_diagnostics_identity
        UNIQUE NULLS NOT DISTINCT (
            derivation_version_id, attempt_id, capture_id,
            diagnostic_code, provider_body_path
        ),
    CONSTRAINT derivation_diagnostics_event
        CHECK (attempt_id IS NOT NULL OR capture_id IS NOT NULL)
)
"""

_FIELD_STATE_CHECK: Final[str] = (
    "IN ('stated', 'json_null', 'absent', 'not_requested', 'inapplicable')"
)
KEYWORD_OVERVIEW_COVERAGE_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.coverage.v1"
)
KEYWORD_OVERVIEW_METRICS_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.metrics.v1"
)
KEYWORD_OVERVIEW_MONTHLY_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.monthly_search_volume.v1"
)
KEYWORD_OVERVIEW_TREND_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.search_volume_trend.v1"
)
KEYWORD_OVERVIEW_PROPERTIES_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.properties.v1"
)
KEYWORD_OVERVIEW_BACKLINKS_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.avg_backlinks.v1"
)
KEYWORD_OVERVIEW_INTENT_KIND: Final[str] = (
    "dataforseo.google.keyword_overview.search_intent.v1"
)
_METRICS_STATE_VALUE_COLUMNS: Final[tuple[str, ...]] = (
    "location_code",
    "language_code",
    "search_partners",
    "search_volume",
    "competition",
    "competition_level",
    "cpc",
    "low_top_of_page_bid",
    "high_top_of_page_bid",
    "categories",
    "provider_update_time",
)


def _state_value_consistency(table: str, column: str) -> str:
    return (
        f"CONSTRAINT {table}_{column}_consistency "
        f"CHECK ("
        f"({column}_state = 'stated' AND {column} IS NOT NULL) "
        f"OR "
        f"({column}_state <> 'stated' AND {column} IS NULL)"
        f")"
    )


_METRICS_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("keyword_overview_metrics", column)
    for column in _METRICS_STATE_VALUE_COLUMNS
)

KEYWORD_OVERVIEW_COVERAGE_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_coverage (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    covered BOOLEAN NOT NULL,
    returned_keyword TEXT,
    returned_keyword_state TEXT NOT NULL
        CHECK (returned_keyword_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_coverage_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_COVERAGE_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT keyword_overview_coverage_returned
        CHECK (
            (covered AND returned_keyword_state = 'stated'
                AND returned_keyword IS NOT NULL)
            OR
            ((NOT covered) AND returned_keyword IS NULL
                AND returned_keyword_state = 'absent')
        )
)
"""

KEYWORD_OVERVIEW_METRICS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_metrics (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    returned_keyword TEXT NOT NULL,
    location_code BIGINT,
    location_code_state TEXT NOT NULL
        CHECK (location_code_state {_FIELD_STATE_CHECK}),
    language_code TEXT,
    language_code_state TEXT NOT NULL
        CHECK (language_code_state {_FIELD_STATE_CHECK}),
    search_partners BOOLEAN,
    search_partners_state TEXT NOT NULL
        CHECK (search_partners_state {_FIELD_STATE_CHECK}),
    search_volume BIGINT,
    search_volume_state TEXT NOT NULL
        CHECK (search_volume_state {_FIELD_STATE_CHECK}),
    competition NUMERIC,
    competition_state TEXT NOT NULL
        CHECK (competition_state {_FIELD_STATE_CHECK}),
    competition_level TEXT,
    competition_level_state TEXT NOT NULL
        CHECK (competition_level_state {_FIELD_STATE_CHECK}),
    cpc NUMERIC,
    cpc_state TEXT NOT NULL
        CHECK (cpc_state {_FIELD_STATE_CHECK}),
    low_top_of_page_bid NUMERIC,
    low_top_of_page_bid_state TEXT NOT NULL
        CHECK (low_top_of_page_bid_state {_FIELD_STATE_CHECK}),
    high_top_of_page_bid NUMERIC,
    high_top_of_page_bid_state TEXT NOT NULL
        CHECK (high_top_of_page_bid_state {_FIELD_STATE_CHECK}),
    categories BIGINT[],
    categories_state TEXT NOT NULL
        CHECK (categories_state {_FIELD_STATE_CHECK}),
    provider_update_time TEXT,
    provider_update_time_state TEXT NOT NULL
        CHECK (provider_update_time_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_metrics_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_METRICS_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_METRICS_CONSISTENCY_SQL}
)
"""

_MONTHLY_CONSISTENCY_SQL: Final[str] = _state_value_consistency(
    "keyword_overview_monthly_search_volume", "search_volume"
)
_TREND_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("keyword_overview_search_volume_trend", column)
    for column in ("monthly", "quarterly", "yearly")
)
_PROPERTIES_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("keyword_overview_properties", column)
    for column in (
        "core_keyword",
        "synonym_clustering_algorithm",
        "keyword_difficulty",
        "detected_language",
        "is_another_language",
    )
)
_BACKLINKS_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("keyword_overview_avg_backlinks", column)
    for column in (
        "backlinks",
        "dofollow",
        "referring_pages",
        "referring_domains",
        "referring_main_domains",
        "rank",
        "main_domain_rank",
        "provider_update_time",
    )
)
_INTENT_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("keyword_overview_search_intent", column)
    for column in ("main_intent", "foreign_intent", "provider_update_time")
)

KEYWORD_OVERVIEW_MONTHLY_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_monthly_search_volume (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    year BIGINT NOT NULL
        CHECK (year >= 2000 AND year <= 2100),
    month BIGINT NOT NULL
        CHECK (month >= 1 AND month <= 12),
    search_volume BIGINT,
    search_volume_state TEXT NOT NULL
        CHECK (search_volume_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_monthly_search_volume_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_MONTHLY_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_MONTHLY_CONSISTENCY_SQL}
)
"""

KEYWORD_OVERVIEW_TREND_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_search_volume_trend (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    monthly BIGINT,
    monthly_state TEXT NOT NULL
        CHECK (monthly_state {_FIELD_STATE_CHECK}),
    quarterly BIGINT,
    quarterly_state TEXT NOT NULL
        CHECK (quarterly_state {_FIELD_STATE_CHECK}),
    yearly BIGINT,
    yearly_state TEXT NOT NULL
        CHECK (yearly_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_search_volume_trend_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_TREND_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_TREND_CONSISTENCY_SQL}
)
"""

KEYWORD_OVERVIEW_PROPERTIES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_properties (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    core_keyword TEXT,
    core_keyword_state TEXT NOT NULL
        CHECK (core_keyword_state {_FIELD_STATE_CHECK}),
    synonym_clustering_algorithm TEXT,
    synonym_clustering_algorithm_state TEXT NOT NULL
        CHECK (synonym_clustering_algorithm_state {_FIELD_STATE_CHECK}),
    keyword_difficulty BIGINT,
    keyword_difficulty_state TEXT NOT NULL
        CHECK (keyword_difficulty_state {_FIELD_STATE_CHECK}),
    detected_language TEXT,
    detected_language_state TEXT NOT NULL
        CHECK (detected_language_state {_FIELD_STATE_CHECK}),
    is_another_language BOOLEAN,
    is_another_language_state TEXT NOT NULL
        CHECK (is_another_language_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_properties_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_PROPERTIES_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_PROPERTIES_CONSISTENCY_SQL}
)
"""

KEYWORD_OVERVIEW_BACKLINKS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_avg_backlinks (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    backlinks NUMERIC,
    backlinks_state TEXT NOT NULL
        CHECK (backlinks_state {_FIELD_STATE_CHECK}),
    dofollow NUMERIC,
    dofollow_state TEXT NOT NULL
        CHECK (dofollow_state {_FIELD_STATE_CHECK}),
    referring_pages NUMERIC,
    referring_pages_state TEXT NOT NULL
        CHECK (referring_pages_state {_FIELD_STATE_CHECK}),
    referring_domains NUMERIC,
    referring_domains_state TEXT NOT NULL
        CHECK (referring_domains_state {_FIELD_STATE_CHECK}),
    referring_main_domains NUMERIC,
    referring_main_domains_state TEXT NOT NULL
        CHECK (referring_main_domains_state {_FIELD_STATE_CHECK}),
    rank NUMERIC,
    rank_state TEXT NOT NULL
        CHECK (rank_state {_FIELD_STATE_CHECK}),
    main_domain_rank NUMERIC,
    main_domain_rank_state TEXT NOT NULL
        CHECK (main_domain_rank_state {_FIELD_STATE_CHECK}),
    provider_update_time TEXT,
    provider_update_time_state TEXT NOT NULL
        CHECK (provider_update_time_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_avg_backlinks_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_BACKLINKS_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_BACKLINKS_CONSISTENCY_SQL}
)
"""

KEYWORD_OVERVIEW_INTENT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS keyword_overview_search_intent (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{{64}}$'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{{64}}$'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    main_intent TEXT,
    main_intent_state TEXT NOT NULL
        CHECK (main_intent_state {_FIELD_STATE_CHECK}),
    foreign_intent TEXT[],
    foreign_intent_state TEXT NOT NULL
        CHECK (foreign_intent_state {_FIELD_STATE_CHECK}),
    provider_update_time TEXT,
    provider_update_time_state TEXT NOT NULL
        CHECK (provider_update_time_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT keyword_overview_search_intent_kind
        CHECK (observation_kind = '{KEYWORD_OVERVIEW_INTENT_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_INTENT_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_FEATURE_KIND: Final[str] = (
    "dataforseo.google.organic.serp_feature_presence.v1"
)
GOOGLE_ORGANIC_RANKED_KIND: Final[str] = "dataforseo.google.organic.ranked_result.v1"
GOOGLE_ORGANIC_AIO_PRESENCE_KIND: Final[str] = (
    "dataforseo.google.organic.ai_overview_presence.v1"
)
GOOGLE_ORGANIC_AIO_SOURCE_KIND: Final[str] = (
    "dataforseo.google.organic.ai_overview_source.v1"
)
GOOGLE_ORGANIC_QUESTION_KIND: Final[str] = (
    "dataforseo.google.organic.related_question.v1"
)
GOOGLE_ORGANIC_QUERY_KIND: Final[str] = "dataforseo.google.organic.related_query.v1"

_HEX64: Final[str] = "^[0-9a-f]{64}$"
_ENVELOPE_FK: Final[str] = """
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES observation_envelopes (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )"""
_RANKED_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("google_organic_ranked_results", column)
    for column in ("description", "website_name")
)
_AIO_SOURCE_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("google_organic_aio_sources", column)
    for column in ("domain", "title", "source")
)
_CONTEXT_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("google_organic_result_context", column)
    for column in (
        "returned_keyword",
        "se_domain",
        "result_datetime",
        "se_results_count",
        "pages_count",
    )
)

GOOGLE_ORGANIC_FEATURES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_serp_features (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    item_type TEXT NOT NULL,
    page BIGINT NOT NULL
        CHECK (page >= 1),
    position TEXT NOT NULL
        CHECK (position IN ('left', 'right')),
    rank_group BIGINT NOT NULL
        CHECK (rank_group >= 1),
    rank_absolute BIGINT NOT NULL
        CHECK (rank_absolute >= 1),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_serp_features_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_FEATURE_KIND}'),
    {_ENVELOPE_FK}
)
"""

GOOGLE_ORGANIC_RANKED_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_ranked_results (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    page BIGINT NOT NULL
        CHECK (page >= 1),
    position TEXT NOT NULL
        CHECK (position IN ('left', 'right')),
    rank_group BIGINT NOT NULL
        CHECK (rank_group >= 1),
    rank_absolute BIGINT NOT NULL
        CHECK (rank_absolute >= 1),
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    description_state TEXT NOT NULL
        CHECK (description_state {_FIELD_STATE_CHECK}),
    website_name TEXT,
    website_name_state TEXT NOT NULL
        CHECK (website_name_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_ranked_results_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_RANKED_KIND}'),
    {_ENVELOPE_FK},
    {_RANKED_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_AIO_PRESENCE_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_aio_presence (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    asynchronous_ai_overview BOOLEAN NOT NULL,
    page BIGINT NOT NULL
        CHECK (page >= 1),
    position TEXT NOT NULL
        CHECK (position IN ('left', 'right')),
    rank_group BIGINT NOT NULL
        CHECK (rank_group >= 1),
    rank_absolute BIGINT NOT NULL
        CHECK (rank_absolute >= 1),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_aio_presence_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_AIO_PRESENCE_KIND}'),
    {_ENVELOPE_FK}
)
"""

GOOGLE_ORGANIC_AIO_SOURCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_aio_sources (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    locus TEXT NOT NULL
        CHECK (locus IN ('top_level', 'element')),
    url TEXT NOT NULL,
    domain TEXT,
    domain_state TEXT NOT NULL
        CHECK (domain_state {_FIELD_STATE_CHECK}),
    title TEXT,
    title_state TEXT NOT NULL
        CHECK (title_state {_FIELD_STATE_CHECK}),
    source TEXT,
    source_state TEXT NOT NULL
        CHECK (source_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_aio_sources_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_AIO_SOURCE_KIND}'),
    CONSTRAINT google_organic_aio_sources_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind, locus
        ),
    {_ENVELOPE_FK},
    {_AIO_SOURCE_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_AIO_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_aio_source_occurrences (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    locus TEXT NOT NULL
        CHECK (locus IN ('top_level', 'element')),
    element_index BIGINT
        CHECK (element_index IS NULL OR element_index >= 0),
    reference_index BIGINT NOT NULL
        CHECK (reference_index >= 0),
    CONSTRAINT google_organic_aio_source_occurrences_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_AIO_SOURCE_KIND}'),
    CONSTRAINT google_organic_aio_source_occurrences_shape
        CHECK (
            (locus = 'top_level' AND element_index IS NULL
                AND reference_index >= 0)
            OR
            (locus = 'element' AND element_index >= 0
                AND reference_index >= 0)
        ),
    CONSTRAINT google_organic_aio_source_occurrences_identity
        UNIQUE NULLS NOT DISTINCT (
            capture_id, derivation_version_id, within_capture_identity,
            element_index, reference_index
        ),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind, locus
    )
        REFERENCES google_organic_aio_sources (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind, locus
        )
)
"""

GOOGLE_ORGANIC_QUESTIONS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_related_questions (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    title TEXT NOT NULL,
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_related_questions_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_QUESTION_KIND}'),
    {_ENVELOPE_FK}
)
"""

GOOGLE_ORGANIC_QUESTION_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_related_question_occurrences (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    page BIGINT NOT NULL
        CHECK (page >= 1),
    position TEXT NOT NULL
        CHECK (position IN ('left', 'right')),
    rank_group BIGINT NOT NULL
        CHECK (rank_group >= 1),
    rank_absolute BIGINT NOT NULL
        CHECK (rank_absolute >= 1),
    question_index BIGINT NOT NULL
        CHECK (question_index >= 0),
    PRIMARY KEY (
        capture_id, derivation_version_id, within_capture_identity,
        page, position, rank_group, rank_absolute, question_index
    ),
    CONSTRAINT google_organic_related_question_occurrences_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_QUESTION_KIND}'),
    {_ENVELOPE_FK}
)
"""

GOOGLE_ORGANIC_QUERIES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_related_queries (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    query TEXT NOT NULL,
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_related_queries_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_QUERY_KIND}'),
    {_ENVELOPE_FK}
)
"""

GOOGLE_ORGANIC_CONTEXT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS google_organic_result_context (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '{_HEX64}'),
    requested_keyword TEXT NOT NULL,
    returned_keyword TEXT,
    returned_keyword_state TEXT NOT NULL
        CHECK (returned_keyword_state {_FIELD_STATE_CHECK}),
    location_code BIGINT NOT NULL,
    language_code TEXT NOT NULL,
    se_domain TEXT,
    se_domain_state TEXT NOT NULL
        CHECK (se_domain_state {_FIELD_STATE_CHECK}),
    result_datetime TEXT,
    result_datetime_state TEXT NOT NULL
        CHECK (result_datetime_state {_FIELD_STATE_CHECK}),
    se_results_count BIGINT,
    se_results_count_state TEXT NOT NULL
        CHECK (se_results_count_state {_FIELD_STATE_CHECK}),
    pages_count BIGINT,
    pages_count_state TEXT NOT NULL
        CHECK (pages_count_state {_FIELD_STATE_CHECK}),
    items_count BIGINT NOT NULL
        CHECK (items_count >= 0),
    item_types TEXT[] NOT NULL,
    PRIMARY KEY (capture_id, derivation_version_id),
    CONSTRAINT google_organic_result_context_outcome
        FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
        REFERENCES outcomes (derivation_version_id, attempt_id, capture_id),
    {_CONTEXT_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_CONTEXT_OUTCOME_FK_SQL: Final[str] = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'google_organic_result_context_outcome'
    ) THEN
        ALTER TABLE google_organic_result_context
            ADD CONSTRAINT google_organic_result_context_outcome
            FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
            REFERENCES outcomes (derivation_version_id, attempt_id, capture_id);
    END IF;
END $$
"""

PRE_PF12_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    DERIVATION_VERSIONS_SQL,
    OUTCOMES_SQL,
    OUTCOMES_IDENTITY_SQL,
    OBSERVATIONS_SQL,
    PROVIDER_RECIPES_SQL,
    PROVIDER_RECIPES_ADAPTER_VERSION_SQL,
    PROVIDER_RECIPE_SELECTIONS_SQL,
    OBSERVATION_ENVELOPES_SQL,
    OBSERVATION_ENVELOPES_KIND_IDENTITY_SQL,
    DERIVATION_DIAGNOSTICS_SQL,
    KEYWORD_OVERVIEW_COVERAGE_SQL,
    KEYWORD_OVERVIEW_METRICS_SQL,
    KEYWORD_OVERVIEW_MONTHLY_SQL,
    KEYWORD_OVERVIEW_TREND_SQL,
    KEYWORD_OVERVIEW_PROPERTIES_SQL,
    KEYWORD_OVERVIEW_BACKLINKS_SQL,
    KEYWORD_OVERVIEW_INTENT_SQL,
)

SCHEMA_STATEMENTS: Final[tuple[str, ...]] = PRE_PF12_SCHEMA_STATEMENTS + (
    GOOGLE_ORGANIC_FEATURES_SQL,
    GOOGLE_ORGANIC_RANKED_SQL,
    GOOGLE_ORGANIC_AIO_PRESENCE_SQL,
    GOOGLE_ORGANIC_AIO_SOURCES_SQL,
    GOOGLE_ORGANIC_AIO_OCCURRENCES_SQL,
    GOOGLE_ORGANIC_QUESTIONS_SQL,
    GOOGLE_ORGANIC_QUESTION_OCCURRENCES_SQL,
    GOOGLE_ORGANIC_QUERIES_SQL,
    GOOGLE_ORGANIC_CONTEXT_SQL,
    GOOGLE_ORGANIC_CONTEXT_OUTCOME_FK_SQL,
)

WIDEN_IJSON_COLUMNS_SQL: Final[tuple[str, ...]] = (
    "ALTER TABLE outcomes ALTER COLUMN observation_count TYPE BIGINT",
    "ALTER TABLE observations ALTER COLUMN result_index TYPE BIGINT",
    "ALTER TABLE observations ALTER COLUMN score TYPE BIGINT",
)


def resolve_database_url(explicit: str | None) -> str:
    if explicit:
        return explicit
    configured = get_settings().database_url
    if configured:
        return configured
    raise ValueError("database URL is required (--database-url or OBSERVATORY_DATABASE_URL)")


def connect(dsn: str) -> Connection[Any]:
    return psycopg.connect(dsn)


def apply_schema(connection: Connection[Any]) -> None:
    """Create rebuildable tables if missing; widen leftover INTEGER I-JSON columns."""

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    for statement in WIDEN_IJSON_COLUMNS_SQL:
        connection.execute(statement)
    connection.commit()


def apply_migrations(dsn: str) -> None:
    with connect(dsn) as connection:
        apply_schema(connection)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.migrate",
        description="Create rebuildable PostgreSQL tables for derivation.",
    )
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    apply_migrations(dsn)
    sys.stdout.write(
        "migrated derivation_versions outcomes observations "
        "provider_recipes provider_recipe_selections observation_envelopes "
        "derivation_diagnostics keyword_overview_coverage "
        "keyword_overview_metrics keyword_overview_monthly_search_volume "
        "keyword_overview_search_volume_trend keyword_overview_properties "
        "keyword_overview_avg_backlinks keyword_overview_search_intent "
        "google_organic_serp_features google_organic_ranked_results "
        "google_organic_aio_presence google_organic_aio_sources "
        "google_organic_aio_source_occurrences "
        "google_organic_related_questions "
        "google_organic_related_question_occurrences "
        "google_organic_related_queries google_organic_result_context\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
