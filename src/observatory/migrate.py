"""Apply the rebuildable PostgreSQL schema for Outcomes and Observations."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Final

import psycopg
from psycopg import Connection, sql

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
        WHERE conrelid = 'outcomes'::regclass
          AND conname = 'outcomes_identity'
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
        WHERE conrelid = 'provider_recipes'::regclass
          AND conname = 'provider_recipes_adapter_version'
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
        WHERE conrelid = 'observation_envelopes'::regclass
          AND conname = 'observation_envelopes_kind_identity'
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
GOOGLE_ORGANIC_RANKED_V2_KIND: Final[str] = (
    "dataforseo.google.organic.ranked_result.v2"
)
GOOGLE_ORGANIC_TOP_STORY_KIND: Final[str] = (
    "dataforseo.google.organic.top_story_result.v1"
)
GOOGLE_ORGANIC_VIDEO_KIND: Final[str] = "dataforseo.google.organic.video_result.v1"
GOOGLE_ORGANIC_SITELINK_KIND: Final[str] = (
    "dataforseo.google.organic.organic_sitelink.v1"
)

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
        WHERE conrelid = 'google_organic_result_context'::regclass
          AND conname = 'google_organic_result_context_outcome'
    ) THEN
        ALTER TABLE google_organic_result_context
            ADD CONSTRAINT google_organic_result_context_outcome
            FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
            REFERENCES outcomes (derivation_version_id, attempt_id, capture_id);
    END IF;
END $$
"""

# --------------------------------------------------------------------------------------
# PF-18 expanded Google Organic relations
#
# These relations belong to the expanded Google Organic Recipe only. The accepted v1
# relations above stay historical v1 relations: ranked-result v2 gets its own typed
# table rather than a second shape inside `google_organic_ranked_results`, and the
# five semantically unchanged v1 kinds keep their existing tables, discriminated by
# `derivation_version_id` exactly as the Keyword Overview core/extended Recipes do.
# --------------------------------------------------------------------------------------

GOOGLE_ORGANIC_RANKED_V2_TABLE: Final[str] = "google_organic_ranked_results_v2"
GOOGLE_ORGANIC_TOP_STORY_TABLE: Final[str] = "google_organic_top_story_results"
GOOGLE_ORGANIC_TOP_STORY_OCCURRENCES_TABLE: Final[str] = (
    "google_organic_top_story_result_occurrences"
)
GOOGLE_ORGANIC_VIDEO_TABLE: Final[str] = "google_organic_video_results"
GOOGLE_ORGANIC_VIDEO_OCCURRENCES_TABLE: Final[str] = (
    "google_organic_video_result_occurrences"
)
GOOGLE_ORGANIC_SITELINK_TABLE: Final[str] = "google_organic_sitelinks"
GOOGLE_ORGANIC_SITELINK_OCCURRENCES_TABLE: Final[str] = (
    "google_organic_sitelink_occurrences"
)

PF18_TABLES: Final[tuple[str, ...]] = (
    GOOGLE_ORGANIC_RANKED_V2_TABLE,
    GOOGLE_ORGANIC_TOP_STORY_TABLE,
    GOOGLE_ORGANIC_TOP_STORY_OCCURRENCES_TABLE,
    GOOGLE_ORGANIC_VIDEO_TABLE,
    GOOGLE_ORGANIC_VIDEO_OCCURRENCES_TABLE,
    GOOGLE_ORGANIC_SITELINK_TABLE,
    GOOGLE_ORGANIC_SITELINK_OCCURRENCES_TABLE,
)

_RANKED_V2_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency(GOOGLE_ORGANIC_RANKED_V2_TABLE, column)
    for column in ("description", "website_name", "organic_item_timestamp")
)
_TOP_STORY_CONSISTENCY_SQL: Final[str] = _state_value_consistency(
    GOOGLE_ORGANIC_TOP_STORY_TABLE, "top_story_item_timestamp"
)
_VIDEO_CONSISTENCY_SQL: Final[str] = _state_value_consistency(
    GOOGLE_ORGANIC_VIDEO_TABLE, "video_item_timestamp"
)
_SITELINK_CONSISTENCY_SQL: Final[str] = _state_value_consistency(
    GOOGLE_ORGANIC_SITELINK_TABLE, "description"
)

# The expanded Recipe binds Top Stories and Video children to their exact parent SERP
# placement envelope. That FK needs a unique key on the reused v1 feature relation; it
# is additive and leaves every existing v1 column, row, and check unchanged.
GOOGLE_ORGANIC_FEATURES_PARENT_UNIQUE_SQL: Final[str] = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'google_organic_serp_features'::regclass
          AND conname = 'google_organic_serp_features_parent'
    ) THEN
        ALTER TABLE google_organic_serp_features
            ADD CONSTRAINT google_organic_serp_features_parent
            UNIQUE (
                capture_id, derivation_version_id,
                within_capture_identity, item_type
            );
    END IF;
END $$
"""

GOOGLE_ORGANIC_RANKED_V2_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_RANKED_V2_TABLE} (
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
    organic_item_timestamp TEXT,
    organic_item_timestamp_state TEXT NOT NULL
        CHECK (organic_item_timestamp_state {_FIELD_STATE_CHECK}),
    links_state TEXT NOT NULL
        CHECK (links_state {_FIELD_STATE_CHECK}),
    links_count BIGINT
        CHECK (links_count IS NULL OR links_count >= 0),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_ranked_results_v2_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_RANKED_V2_KIND}'),
    CONSTRAINT google_organic_ranked_results_v2_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT google_organic_ranked_results_v2_links_consistency
        CHECK (
            (links_state = 'stated' AND links_count IS NOT NULL)
            OR
            (links_state <> 'stated' AND links_count IS NULL)
        ),
    {_ENVELOPE_FK},
    {_RANKED_V2_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_TOP_STORY_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_TOP_STORY_TABLE} (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    parent_item_type TEXT NOT NULL
        CHECK (parent_item_type = 'top_stories'),
    parent_within_capture_identity TEXT NOT NULL
        CHECK (parent_within_capture_identity ~ '{_HEX64}'),
    parent_page BIGINT NOT NULL
        CHECK (parent_page >= 1),
    parent_position TEXT NOT NULL
        CHECK (parent_position IN ('left', 'right')),
    parent_rank_group BIGINT NOT NULL
        CHECK (parent_rank_group >= 1),
    parent_rank_absolute BIGINT NOT NULL
        CHECK (parent_rank_absolute >= 1),
    child_url TEXT NOT NULL,
    source TEXT NOT NULL,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    top_story_item_timestamp TEXT,
    top_story_item_timestamp_state TEXT NOT NULL
        CHECK (top_story_item_timestamp_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_top_story_results_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_TOP_STORY_KIND}'),
    CONSTRAINT google_organic_top_story_results_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK},
    FOREIGN KEY (
        capture_id, derivation_version_id,
        parent_within_capture_identity, parent_item_type
    )
        REFERENCES google_organic_serp_features (
            capture_id, derivation_version_id,
            within_capture_identity, item_type
        ),
    {_TOP_STORY_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_TOP_STORY_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_TOP_STORY_OCCURRENCES_TABLE} (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    child_index BIGINT NOT NULL
        CHECK (child_index >= 0),
    PRIMARY KEY (
        capture_id, derivation_version_id, within_capture_identity, child_index
    ),
    CONSTRAINT google_organic_top_story_result_occurrences_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_TOP_STORY_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES {GOOGLE_ORGANIC_TOP_STORY_TABLE} (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

GOOGLE_ORGANIC_VIDEO_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_VIDEO_TABLE} (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    parent_item_type TEXT NOT NULL
        CHECK (parent_item_type = 'video'),
    parent_within_capture_identity TEXT NOT NULL
        CHECK (parent_within_capture_identity ~ '{_HEX64}'),
    parent_page BIGINT NOT NULL
        CHECK (parent_page >= 1),
    parent_position TEXT NOT NULL
        CHECK (parent_position IN ('left', 'right')),
    parent_rank_group BIGINT NOT NULL
        CHECK (parent_rank_group >= 1),
    parent_rank_absolute BIGINT NOT NULL
        CHECK (parent_rank_absolute >= 1),
    child_url TEXT NOT NULL,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    video_item_timestamp TEXT,
    video_item_timestamp_state TEXT NOT NULL
        CHECK (video_item_timestamp_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_video_results_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_VIDEO_KIND}'),
    CONSTRAINT google_organic_video_results_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK},
    FOREIGN KEY (
        capture_id, derivation_version_id,
        parent_within_capture_identity, parent_item_type
    )
        REFERENCES google_organic_serp_features (
            capture_id, derivation_version_id,
            within_capture_identity, item_type
        ),
    {_VIDEO_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_VIDEO_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_VIDEO_OCCURRENCES_TABLE} (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    child_index BIGINT NOT NULL
        CHECK (child_index >= 0),
    PRIMARY KEY (
        capture_id, derivation_version_id, within_capture_identity, child_index
    ),
    CONSTRAINT google_organic_video_result_occurrences_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_VIDEO_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES {GOOGLE_ORGANIC_VIDEO_TABLE} (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

GOOGLE_ORGANIC_SITELINK_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_SITELINK_TABLE} (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL,
    parent_within_capture_identity TEXT NOT NULL
        CHECK (parent_within_capture_identity ~ '{_HEX64}'),
    parent_page BIGINT NOT NULL
        CHECK (parent_page >= 1),
    parent_position TEXT NOT NULL
        CHECK (parent_position IN ('left', 'right')),
    parent_rank_group BIGINT NOT NULL
        CHECK (parent_rank_group >= 1),
    parent_rank_absolute BIGINT NOT NULL
        CHECK (parent_rank_absolute >= 1),
    child_url TEXT NOT NULL,
    title TEXT NOT NULL,
    domain TEXT NOT NULL,
    description TEXT,
    description_state TEXT NOT NULL
        CHECK (description_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT google_organic_sitelinks_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_SITELINK_KIND}'),
    CONSTRAINT google_organic_sitelinks_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK},
    FOREIGN KEY (
        capture_id, derivation_version_id, parent_within_capture_identity
    )
        REFERENCES {GOOGLE_ORGANIC_RANKED_V2_TABLE} (
            capture_id, derivation_version_id, within_capture_identity
        ),
    {_SITELINK_CONSISTENCY_SQL}
)
"""

GOOGLE_ORGANIC_SITELINK_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS {GOOGLE_ORGANIC_SITELINK_OCCURRENCES_TABLE} (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    child_index BIGINT NOT NULL
        CHECK (child_index >= 0),
    PRIMARY KEY (
        capture_id, derivation_version_id, within_capture_identity, child_index
    ),
    CONSTRAINT google_organic_sitelink_occurrences_kind
        CHECK (observation_kind = '{GOOGLE_ORGANIC_SITELINK_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES {GOOGLE_ORGANIC_SITELINK_TABLE} (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

SEARCH_MENTIONS_ITEM_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.search_mentions.item.v1"
)
SEARCH_MENTIONS_MONTHLY_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.search_mentions.monthly_search_volume.v1"
)
SEARCH_MENTIONS_SOURCE_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.search_mentions.source.v1"
)
_IJSON_MAX: Final[str] = "9007199254740991"
_CLOCK_RE: Final[str] = (
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \+00:00$"
)
_SOURCE_OPTIONAL_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    _state_value_consistency("search_mentions_sources", column)
    for column in ("publication_date", "thumbnail", "markdown")
)
_TOKEN_CONSISTENCY_SQL: Final[str] = _state_value_consistency(
    "search_mentions_result_context", "search_after_token"
)

SEARCH_MENTIONS_ITEMS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_items (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    platform TEXT NOT NULL,
    model_name TEXT NOT NULL
        CHECK (char_length(model_name) >= 1),
    location_code BIGINT NOT NULL
        CHECK (location_code >= 0 AND location_code <= {_IJSON_MAX}),
    language_code TEXT NOT NULL,
    question TEXT NOT NULL
        CHECK (char_length(question) >= 1),
    answer TEXT NOT NULL,
    ai_search_volume BIGINT NOT NULL
        CHECK (ai_search_volume >= 0 AND ai_search_volume <= {_IJSON_MAX}),
    is_web_search_based BOOLEAN NOT NULL,
    first_response_at TEXT NOT NULL
        CHECK (first_response_at ~ '{_CLOCK_RE}'),
    last_response_at TEXT NOT NULL
        CHECK (last_response_at ~ '{_CLOCK_RE}'),
    search_results_state TEXT NOT NULL
        CHECK (search_results_state = 'json_null'),
    brand_entities_state TEXT NOT NULL
        CHECK (brand_entities_state = 'json_null'),
    fan_out_queries_state TEXT NOT NULL
        CHECK (fan_out_queries_state = 'json_null'),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT search_mentions_items_kind
        CHECK (observation_kind = '{SEARCH_MENTIONS_ITEM_KIND}'),
    CONSTRAINT search_mentions_items_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT search_mentions_items_clock_order
        CHECK (last_response_at >= first_response_at),
    {_ENVELOPE_FK}
)
"""

SEARCH_MENTIONS_ITEM_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_item_occurrences (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    PRIMARY KEY (
        capture_id, derivation_version_id,
        within_capture_identity, item_index
    ),
    CONSTRAINT search_mentions_item_occurrences_kind
        CHECK (observation_kind = '{SEARCH_MENTIONS_ITEM_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES search_mentions_items (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

SEARCH_MENTIONS_MONTHLY_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_monthly_search_volume (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    model_name TEXT NOT NULL
        CHECK (char_length(model_name) >= 1),
    question TEXT NOT NULL
        CHECK (char_length(question) >= 1),
    year BIGINT NOT NULL
        CHECK (year >= 1 AND year <= 9999),
    month BIGINT NOT NULL
        CHECK (month >= 1 AND month <= 12),
    search_volume BIGINT NOT NULL
        CHECK (search_volume >= 0 AND search_volume <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT search_mentions_monthly_kind
        CHECK (observation_kind = '{SEARCH_MENTIONS_MONTHLY_KIND}'),
    CONSTRAINT search_mentions_monthly_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK}
)
"""

SEARCH_MENTIONS_MONTHLY_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_monthly_occurrences (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    PRIMARY KEY (
        capture_id, derivation_version_id,
        within_capture_identity, item_index
    ),
    CONSTRAINT search_mentions_monthly_occurrences_kind
        CHECK (observation_kind = '{SEARCH_MENTIONS_MONTHLY_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES search_mentions_monthly_search_volume (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

SEARCH_MENTIONS_SOURCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_sources (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    model_name TEXT NOT NULL
        CHECK (char_length(model_name) >= 1),
    question TEXT NOT NULL
        CHECK (char_length(question) >= 1),
    url TEXT NOT NULL
        CHECK (char_length(url) >= 1),
    title TEXT NOT NULL,
    domain TEXT NOT NULL,
    source_name TEXT NOT NULL,
    snippet TEXT NOT NULL,
    publication_date TEXT,
    publication_date_state TEXT NOT NULL
        CHECK (publication_date_state {_FIELD_STATE_CHECK}),
    thumbnail TEXT,
    thumbnail_state TEXT NOT NULL
        CHECK (thumbnail_state {_FIELD_STATE_CHECK}),
    markdown TEXT,
    markdown_state TEXT NOT NULL
        CHECK (markdown_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT search_mentions_sources_kind
        CHECK (observation_kind = '{SEARCH_MENTIONS_SOURCE_KIND}'),
    CONSTRAINT search_mentions_sources_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK},
    {_SOURCE_OPTIONAL_CONSISTENCY_SQL}
)
"""

SEARCH_MENTIONS_SOURCE_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_source_occurrences (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    rank BIGINT NOT NULL
        CHECK (rank >= 1 AND rank <= {_IJSON_MAX}),
    PRIMARY KEY (
        capture_id, derivation_version_id,
        within_capture_identity, item_index, rank
    ),
    CONSTRAINT search_mentions_source_occurrences_kind
        CHECK (observation_kind = '{SEARCH_MENTIONS_SOURCE_KIND}'),
    FOREIGN KEY (
        capture_id, derivation_version_id,
        within_capture_identity, observation_kind
    )
        REFERENCES search_mentions_sources (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

SEARCH_MENTIONS_CONTEXT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS search_mentions_result_context (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '{_HEX64}'),
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    match_type TEXT NOT NULL,
    search_filter TEXT NOT NULL,
    search_scope TEXT[] NOT NULL,
    platform TEXT NOT NULL,
    location_code BIGINT NOT NULL
        CHECK (location_code >= 0 AND location_code <= {_IJSON_MAX}),
    language_code TEXT NOT NULL,
    request_limit BIGINT NOT NULL
        CHECK (request_limit >= 0 AND request_limit <= {_IJSON_MAX}),
    request_offset BIGINT NOT NULL
        CHECK (request_offset >= 0 AND request_offset <= {_IJSON_MAX}),
    total_count BIGINT NOT NULL
        CHECK (total_count >= 0 AND total_count <= {_IJSON_MAX}),
    result_offset BIGINT NOT NULL
        CHECK (result_offset >= 0 AND result_offset <= {_IJSON_MAX}),
    items_count BIGINT NOT NULL
        CHECK (items_count >= 0 AND items_count <= {_IJSON_MAX}),
    search_after_token TEXT,
    search_after_token_state TEXT NOT NULL
        CHECK (search_after_token_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id),
    CONSTRAINT search_mentions_result_context_outcome
        FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
        REFERENCES outcomes (derivation_version_id, attempt_id, capture_id),
    {_TOKEN_CONSISTENCY_SQL}
)
"""

TARGET_METRICS_TOTAL_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.target_metrics.total.v1"
)
TARGET_METRICS_SOURCE_DOMAIN_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.target_metrics.source_domain.v1"
)
_TM_OPTIONAL_STATES: Final[str] = "IN ('stated', 'json_null', 'absent')"
_TM_OPTIONAL_CONSISTENCY_SQL: Final[str] = ",\n    ".join(
    (
        f"CONSTRAINT target_metrics_result_context_{family}_consistency "
        f"CHECK ("
        f"({family}_state = 'stated' AND {family}_count IS NOT NULL) "
        f"OR "
        f"({family}_state <> 'stated' AND {family}_count IS NULL)"
        f")"
    )
    for family in (
        "search_results_domain",
        "brand_entities_title",
        "brand_entities_category",
    )
)

TARGET_METRICS_TOTALS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS target_metrics_totals (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    mentions BIGINT NOT NULL
        CHECK (mentions >= 0 AND mentions <= {_IJSON_MAX}),
    ai_search_volume BIGINT NOT NULL
        CHECK (ai_search_volume >= 0 AND ai_search_volume <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT target_metrics_totals_kind
        CHECK (observation_kind = '{TARGET_METRICS_TOTAL_KIND}'),
    CONSTRAINT target_metrics_totals_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK}
)
"""

TARGET_METRICS_SOURCE_DOMAINS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS target_metrics_source_domains (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    domain TEXT NOT NULL
        CHECK (char_length(domain) >= 1),
    mentions BIGINT NOT NULL
        CHECK (mentions >= 0 AND mentions <= {_IJSON_MAX}),
    ai_search_volume BIGINT NOT NULL
        CHECK (ai_search_volume >= 0 AND ai_search_volume <= {_IJSON_MAX}),
    provider_array_index BIGINT NOT NULL
        CHECK (provider_array_index >= 0 AND provider_array_index <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT target_metrics_source_domains_kind
        CHECK (observation_kind = '{TARGET_METRICS_SOURCE_DOMAIN_KIND}'),
    CONSTRAINT target_metrics_source_domains_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT target_metrics_source_domains_lexical
        UNIQUE (capture_id, derivation_version_id, provider_array_index),
    {_ENVELOPE_FK}
)
"""

TARGET_METRICS_CONTEXT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS target_metrics_result_context (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '{_HEX64}'),
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    match_type TEXT NOT NULL,
    search_filter TEXT NOT NULL,
    search_scope TEXT[] NOT NULL,
    platform TEXT NOT NULL,
    location_code BIGINT NOT NULL
        CHECK (location_code >= 0 AND location_code <= {_IJSON_MAX}),
    language_code TEXT NOT NULL,
    internal_list_limit BIGINT NOT NULL
        CHECK (internal_list_limit >= 0 AND internal_list_limit <= {_IJSON_MAX}),
    total_count BIGINT NOT NULL
        CHECK (total_count >= 0 AND total_count <= {_IJSON_MAX}),
    result_offset BIGINT NOT NULL
        CHECK (result_offset >= 0 AND result_offset <= {_IJSON_MAX}),
    items_count BIGINT NOT NULL
        CHECK (items_count >= 0 AND items_count <= {_IJSON_MAX}),
    items_state TEXT NOT NULL
        CHECK (items_state {_TM_OPTIONAL_STATES}),
    location_key BIGINT NOT NULL
        CHECK (location_key >= 0 AND location_key <= {_IJSON_MAX}),
    location_mentions BIGINT NOT NULL
        CHECK (location_mentions >= 0 AND location_mentions <= {_IJSON_MAX}),
    location_ai_search_volume BIGINT NOT NULL
        CHECK (location_ai_search_volume >= 0 AND location_ai_search_volume <= {_IJSON_MAX}),
    location_provider_array_index BIGINT NOT NULL
        CHECK (
            location_provider_array_index >= 0
            AND location_provider_array_index <= {_IJSON_MAX}
        ),
    location_row_count BIGINT NOT NULL
        CHECK (location_row_count >= 0 AND location_row_count <= {_IJSON_MAX}),
    language_key TEXT NOT NULL,
    language_mentions BIGINT NOT NULL
        CHECK (language_mentions >= 0 AND language_mentions <= {_IJSON_MAX}),
    language_ai_search_volume BIGINT NOT NULL
        CHECK (language_ai_search_volume >= 0 AND language_ai_search_volume <= {_IJSON_MAX}),
    language_provider_array_index BIGINT NOT NULL
        CHECK (
            language_provider_array_index >= 0
            AND language_provider_array_index <= {_IJSON_MAX}
        ),
    language_row_count BIGINT NOT NULL
        CHECK (language_row_count >= 0 AND language_row_count <= {_IJSON_MAX}),
    platform_key TEXT NOT NULL,
    platform_mentions BIGINT NOT NULL
        CHECK (platform_mentions >= 0 AND platform_mentions <= {_IJSON_MAX}),
    platform_ai_search_volume BIGINT NOT NULL
        CHECK (platform_ai_search_volume >= 0 AND platform_ai_search_volume <= {_IJSON_MAX}),
    platform_provider_array_index BIGINT NOT NULL
        CHECK (
            platform_provider_array_index >= 0
            AND platform_provider_array_index <= {_IJSON_MAX}
        ),
    platform_row_count BIGINT NOT NULL
        CHECK (platform_row_count >= 0 AND platform_row_count <= {_IJSON_MAX}),
    sources_domain_count BIGINT NOT NULL
        CHECK (sources_domain_count >= 0 AND sources_domain_count <= {_IJSON_MAX}),
    search_results_domain_count BIGINT
        CHECK (
            search_results_domain_count IS NULL
            OR (
                search_results_domain_count >= 0
                AND search_results_domain_count <= {_IJSON_MAX}
            )
        ),
    search_results_domain_state TEXT NOT NULL
        CHECK (search_results_domain_state {_TM_OPTIONAL_STATES}),
    brand_entities_title_count BIGINT
        CHECK (
            brand_entities_title_count IS NULL
            OR (
                brand_entities_title_count >= 0
                AND brand_entities_title_count <= {_IJSON_MAX}
            )
        ),
    brand_entities_title_state TEXT NOT NULL
        CHECK (brand_entities_title_state {_TM_OPTIONAL_STATES}),
    brand_entities_category_count BIGINT
        CHECK (
            brand_entities_category_count IS NULL
            OR (
                brand_entities_category_count >= 0
                AND brand_entities_category_count <= {_IJSON_MAX}
            )
        ),
    brand_entities_category_state TEXT NOT NULL
        CHECK (brand_entities_category_state {_TM_OPTIONAL_STATES}),
    PRIMARY KEY (capture_id, derivation_version_id),
    CONSTRAINT target_metrics_result_context_outcome
        FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
        REFERENCES outcomes (derivation_version_id, attempt_id, capture_id),
    {_TM_OPTIONAL_CONSISTENCY_SQL}
)
"""

HISTORICAL_MONTHLY_KIND: Final[str] = (
    "dataforseo.google.ai_optimization.llm_mentions_historical.monthly.v1"
)

LLM_MENTIONS_HISTORICAL_MONTHLY_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS llm_mentions_historical_monthly (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL,
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    year BIGINT NOT NULL
        CHECK (year >= 1 AND year <= 9999),
    month BIGINT NOT NULL
        CHECK (month >= 1 AND month <= 12),
    mentions BIGINT NOT NULL
        CHECK (mentions >= 0 AND mentions <= {_IJSON_MAX}),
    ai_search_volume BIGINT NOT NULL
        CHECK (ai_search_volume >= 0 AND ai_search_volume <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT llm_mentions_historical_monthly_kind
        CHECK (observation_kind = '{HISTORICAL_MONTHLY_KIND}'),
    CONSTRAINT llm_mentions_historical_monthly_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT llm_mentions_historical_monthly_period
        UNIQUE (capture_id, derivation_version_id, year, month),
    {_ENVELOPE_FK}
)
"""

LLM_MENTIONS_HISTORICAL_CONTEXT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS llm_mentions_historical_result_context (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '{_HEX64}'),
    requested_keyword TEXT NOT NULL
        CHECK (char_length(requested_keyword) >= 1),
    match_type TEXT NOT NULL,
    search_filter TEXT NOT NULL,
    search_scope TEXT[] NOT NULL,
    platform TEXT NOT NULL,
    location_code BIGINT NOT NULL
        CHECK (location_code >= 0 AND location_code <= {_IJSON_MAX}),
    language_code TEXT NOT NULL,
    date_from TEXT NOT NULL,
    date_to TEXT NOT NULL,
    items_count BIGINT NOT NULL
        CHECK (items_count >= 0 AND items_count <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id),
    CONSTRAINT llm_mentions_historical_result_context_outcome
        FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
        REFERENCES outcomes (derivation_version_id, attempt_id, capture_id)
)
"""

LLM_MENTIONS_HISTORICAL_UNRETURNED_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS llm_mentions_historical_unreturned_requested_periods (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    year BIGINT NOT NULL,
    month BIGINT NOT NULL,
    CONSTRAINT hist_unret_pk
        PRIMARY KEY (capture_id, derivation_version_id, year, month),
    CONSTRAINT hist_unret_year_ck
        CHECK (year >= 1 AND year <= 9999),
    CONSTRAINT hist_unret_month_ck
        CHECK (month >= 1 AND month <= 12),
    CONSTRAINT hist_unret_context_fk
        FOREIGN KEY (capture_id, derivation_version_id)
        REFERENCES llm_mentions_historical_result_context (
            capture_id, derivation_version_id
        )
)
"""

RELATED_KEYWORDS_KEYWORD_DATA_KIND: Final[str] = (
    "dataforseo.google.related_keywords.keyword_data.v1"
)
RELATED_KEYWORDS_MONTHLY_KIND: Final[str] = (
    "dataforseo.google.related_keywords.monthly_search_volume.v1"
)
RELATED_KEYWORDS_RELATIONSHIP_KIND: Final[str] = (
    "dataforseo.google.related_keywords.relationship.v1"
)
_RK04_LOCUS_CHECK: Final[str] = "IN ('seed_keyword_data', 'returned_item')"


def _rk04_consistency(name: str, column: str) -> str:
    """Short-named state/value consistency CHECK.

    `_state_value_consistency` derives its constraint name from the table name, which would
    exceed PostgreSQL's 63-byte identifier limit for several RK-04 relations and be silently
    truncated. RK-04 therefore names each constraint explicitly.
    """

    return (
        f"CONSTRAINT {name} "
        f"CHECK (({column}_state = 'stated' AND {column} IS NOT NULL) "
        f"OR ({column}_state <> 'stated' AND {column} IS NULL))"
    )


def _rk04_clock(column: str, name: str) -> str:
    """Structure-specific provider clock column pair.

    RK-04 exposes no generic `provider_update_time`. Each clock keeps the name of the exact
    provider structure that stated it, and the exact lexical value survives — including the
    year-1 SERP string, which acquires no sentinel meaning here.
    """

    return (
        f"{column} TEXT\n"
        f"        CHECK ({column} IS NULL OR {column} ~ '{_CLOCK_RE}'),\n"
        f"    {column}_state TEXT NOT NULL\n"
        f"        CHECK ({column}_state {_FIELD_STATE_CHECK}),\n"
        f"    {_rk04_consistency(name, column)}"
    )


def _rk04_nonneg(column: str) -> str:
    return f"CHECK ({column} IS NULL OR ({column} >= 0 AND {column} <= {_IJSON_MAX}))"


def _rk04_signed(column: str) -> str:
    return (
        f"CHECK ({column} IS NULL OR "
        f"({column} >= -{_IJSON_MAX} AND {column} <= {_IJSON_MAX}))"
    )


_RK04_SEMANTIC_KEY: Final[str] = f"""capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL"""


def _rk04_child_fk(constraint: str) -> str:
    return f"""CONSTRAINT {constraint}
        FOREIGN KEY (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
        REFERENCES related_keywords_keyword_data (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )"""


RELATED_KEYWORDS_KEYWORD_DATA_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_keyword_data (
    {_RK04_SEMANTIC_KEY},
    requested_seed TEXT NOT NULL
        CHECK (char_length(requested_seed) >= 1),
    locus TEXT NOT NULL
        CHECK (locus {_RK04_LOCUS_CHECK}),
    keyword TEXT NOT NULL
        CHECK (char_length(keyword) >= 1),
    location_code BIGINT
        {_rk04_nonneg("location_code")},
    location_code_state TEXT NOT NULL
        CHECK (location_code_state {_FIELD_STATE_CHECK}),
    language_code TEXT,
    language_code_state TEXT NOT NULL
        CHECK (language_code_state {_FIELD_STATE_CHECK}),
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    keyword_info_state TEXT NOT NULL
        CHECK (keyword_info_state {_FIELD_STATE_CHECK}),
    keyword_properties_state TEXT NOT NULL
        CHECK (keyword_properties_state {_FIELD_STATE_CHECK}),
    avg_backlinks_state TEXT NOT NULL
        CHECK (avg_backlinks_state {_FIELD_STATE_CHECK}),
    search_intent_state TEXT NOT NULL
        CHECK (search_intent_state {_FIELD_STATE_CHECK}),
    serp_info_state TEXT NOT NULL
        CHECK (serp_info_state {_FIELD_STATE_CHECK}),
    bing_normalized_state TEXT NOT NULL
        CHECK (bing_normalized_state {_FIELD_STATE_CHECK}),
    clickstream_normalized_state TEXT NOT NULL
        CHECK (clickstream_normalized_state {_FIELD_STATE_CHECK}),
    clickstream_keyword_info_state TEXT NOT NULL
        CHECK (clickstream_keyword_info_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_keyword_data_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    CONSTRAINT rk04_keyword_data_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_rk04_consistency("rk04_kd_location_ck", "location_code")},
    {_rk04_consistency("rk04_kd_language_ck", "language_code")},
    {_rk04_consistency("rk04_kd_se_type_ck", "se_type")},
    {_ENVELOPE_FK}
)
"""

RELATED_KEYWORDS_KEYWORD_INFO_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_keyword_info (
    {_RK04_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    {_rk04_clock("keyword_info_last_updated_time", "rk04_ki_clock_ck")},
    competition NUMERIC,
    competition_state TEXT NOT NULL
        CHECK (competition_state {_FIELD_STATE_CHECK}),
    competition_level TEXT,
    competition_level_state TEXT NOT NULL
        CHECK (competition_level_state {_FIELD_STATE_CHECK}),
    cpc NUMERIC,
    cpc_state TEXT NOT NULL
        CHECK (cpc_state {_FIELD_STATE_CHECK}),
    search_volume BIGINT
        {_rk04_nonneg("search_volume")},
    search_volume_state TEXT NOT NULL
        CHECK (search_volume_state {_FIELD_STATE_CHECK}),
    low_top_of_page_bid NUMERIC,
    low_top_of_page_bid_state TEXT NOT NULL
        CHECK (low_top_of_page_bid_state {_FIELD_STATE_CHECK}),
    high_top_of_page_bid NUMERIC,
    high_top_of_page_bid_state TEXT NOT NULL
        CHECK (high_top_of_page_bid_state {_FIELD_STATE_CHECK}),
    categories BIGINT[],
    categories_state TEXT NOT NULL
        CHECK (categories_state {_FIELD_STATE_CHECK}),
    monthly_searches_state TEXT NOT NULL
        CHECK (monthly_searches_state {_FIELD_STATE_CHECK}),
    search_volume_trend_state TEXT NOT NULL
        CHECK (search_volume_trend_state {_FIELD_STATE_CHECK}),
    trend_monthly BIGINT
        {_rk04_signed("trend_monthly")},
    trend_monthly_state TEXT NOT NULL
        CHECK (trend_monthly_state {_FIELD_STATE_CHECK}),
    trend_quarterly BIGINT
        {_rk04_signed("trend_quarterly")},
    trend_quarterly_state TEXT NOT NULL
        CHECK (trend_quarterly_state {_FIELD_STATE_CHECK}),
    trend_yearly BIGINT
        {_rk04_signed("trend_yearly")},
    trend_yearly_state TEXT NOT NULL
        CHECK (trend_yearly_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_keyword_info_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rk04_consistency("rk04_ki_se_type_ck", "se_type")},
    {_rk04_consistency("rk04_ki_competition_ck", "competition")},
    {_rk04_consistency("rk04_ki_comp_level_ck", "competition_level")},
    {_rk04_consistency("rk04_ki_cpc_ck", "cpc")},
    {_rk04_consistency("rk04_ki_volume_ck", "search_volume")},
    {_rk04_consistency("rk04_ki_low_bid_ck", "low_top_of_page_bid")},
    {_rk04_consistency("rk04_ki_high_bid_ck", "high_top_of_page_bid")},
    {_rk04_consistency("rk04_ki_categories_ck", "categories")},
    {_rk04_consistency("rk04_ki_trend_m_ck", "trend_monthly")},
    {_rk04_consistency("rk04_ki_trend_q_ck", "trend_quarterly")},
    {_rk04_consistency("rk04_ki_trend_y_ck", "trend_yearly")},
    {_rk04_child_fk("rk04_keyword_info_parent")}
)
"""

RELATED_KEYWORDS_KEYWORD_PROPERTIES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_keyword_properties (
    {_RK04_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    core_keyword TEXT,
    core_keyword_state TEXT NOT NULL
        CHECK (core_keyword_state {_FIELD_STATE_CHECK}),
    synonym_clustering_algorithm TEXT,
    synonym_clustering_algorithm_state TEXT NOT NULL
        CHECK (synonym_clustering_algorithm_state {_FIELD_STATE_CHECK}),
    keyword_difficulty BIGINT
        {_rk04_nonneg("keyword_difficulty")},
    keyword_difficulty_state TEXT NOT NULL
        CHECK (keyword_difficulty_state {_FIELD_STATE_CHECK}),
    detected_language TEXT,
    detected_language_state TEXT NOT NULL
        CHECK (detected_language_state {_FIELD_STATE_CHECK}),
    is_another_language BOOLEAN,
    is_another_language_state TEXT NOT NULL
        CHECK (is_another_language_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_properties_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rk04_consistency("rk04_kp_se_type_ck", "se_type")},
    {_rk04_consistency("rk04_kp_core_ck", "core_keyword")},
    {_rk04_consistency("rk04_kp_algorithm_ck", "synonym_clustering_algorithm")},
    {_rk04_consistency("rk04_kp_difficulty_ck", "keyword_difficulty")},
    {_rk04_consistency("rk04_kp_language_ck", "detected_language")},
    {_rk04_consistency("rk04_kp_another_ck", "is_another_language")},
    {_rk04_child_fk("rk04_properties_parent")}
)
"""

RELATED_KEYWORDS_AVG_BACKLINKS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_avg_backlinks (
    {_RK04_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
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
    {_rk04_clock("avg_backlinks_last_updated_time", "rk04_bl_clock_ck")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_backlinks_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rk04_consistency("rk04_bl_se_type_ck", "se_type")},
    {_rk04_consistency("rk04_bl_backlinks_ck", "backlinks")},
    {_rk04_consistency("rk04_bl_dofollow_ck", "dofollow")},
    {_rk04_consistency("rk04_bl_ref_pages_ck", "referring_pages")},
    {_rk04_consistency("rk04_bl_ref_domains_ck", "referring_domains")},
    {_rk04_consistency("rk04_bl_ref_main_ck", "referring_main_domains")},
    {_rk04_consistency("rk04_bl_rank_ck", "rank")},
    {_rk04_consistency("rk04_bl_main_rank_ck", "main_domain_rank")},
    {_rk04_child_fk("rk04_backlinks_parent")}
)
"""

RELATED_KEYWORDS_SEARCH_INTENT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_search_intent (
    {_RK04_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    main_intent TEXT,
    main_intent_state TEXT NOT NULL
        CHECK (main_intent_state {_FIELD_STATE_CHECK}),
    foreign_intent TEXT[],
    foreign_intent_state TEXT NOT NULL
        CHECK (foreign_intent_state {_FIELD_STATE_CHECK}),
    {_rk04_clock("search_intent_last_updated_time", "rk04_si_clock_ck")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_intent_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rk04_consistency("rk04_si_se_type_ck", "se_type")},
    {_rk04_consistency("rk04_si_main_ck", "main_intent")},
    {_rk04_consistency("rk04_si_foreign_ck", "foreign_intent")},
    {_rk04_child_fk("rk04_intent_parent")}
)
"""

RELATED_KEYWORDS_SERP_INFO_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_serp_info (
    {_RK04_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    check_url TEXT,
    check_url_state TEXT NOT NULL
        CHECK (check_url_state {_FIELD_STATE_CHECK}),
    serp_item_types TEXT[],
    serp_item_types_state TEXT NOT NULL
        CHECK (serp_item_types_state {_FIELD_STATE_CHECK}),
    se_results_count BIGINT
        {_rk04_nonneg("se_results_count")},
    se_results_count_state TEXT NOT NULL
        CHECK (se_results_count_state {_FIELD_STATE_CHECK}),
    {_rk04_clock("serp_last_updated_time", "rk04_serp_last_ck")},
    {_rk04_clock("serp_previous_updated_time", "rk04_serp_prev_ck")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_serp_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rk04_consistency("rk04_serp_se_type_ck", "se_type")},
    {_rk04_consistency("rk04_serp_url_ck", "check_url")},
    {_rk04_consistency("rk04_serp_types_ck", "serp_item_types")},
    {_rk04_consistency("rk04_serp_count_ck", "se_results_count")},
    {_rk04_child_fk("rk04_serp_parent")}
)
"""

RELATED_KEYWORDS_MONTHLY_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_monthly_search_volume (
    {_RK04_SEMANTIC_KEY},
    requested_seed TEXT NOT NULL
        CHECK (char_length(requested_seed) >= 1),
    locus TEXT NOT NULL
        CHECK (locus {_RK04_LOCUS_CHECK}),
    keyword TEXT NOT NULL
        CHECK (char_length(keyword) >= 1),
    year BIGINT NOT NULL
        CHECK (year >= 1 AND year <= 9999),
    month BIGINT NOT NULL
        CHECK (month >= 1 AND month <= 12),
    search_volume BIGINT NOT NULL
        CHECK (search_volume >= 0 AND search_volume <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_monthly_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_MONTHLY_KIND}'),
    CONSTRAINT rk04_monthly_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK}
)
"""

RELATED_KEYWORDS_RELATIONSHIP_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_relationship (
    {_RK04_SEMANTIC_KEY},
    requested_seed TEXT NOT NULL
        CHECK (char_length(requested_seed) >= 1),
    source_keyword TEXT NOT NULL
        CHECK (char_length(source_keyword) >= 1),
    target_keyword TEXT NOT NULL
        CHECK (char_length(target_keyword) >= 1),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rk04_relationship_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_RELATIONSHIP_KIND}'),
    CONSTRAINT rk04_relationship_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK}
)
"""

RELATED_KEYWORDS_ITEM_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_keyword_data_item_occurrences (
    {_RK04_SEMANTIC_KEY},
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    depth BIGINT NOT NULL
        CHECK (depth >= 0 AND depth <= 4),
    item_se_type TEXT NOT NULL,
    related_keywords_state TEXT NOT NULL
        CHECK (related_keywords_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (
        capture_id, derivation_version_id,
        within_capture_identity, item_index
    ),
    CONSTRAINT rk04_item_occ_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rk04_child_fk("rk04_item_occ_parent")}
)
"""

RELATED_KEYWORDS_MONTHLY_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_monthly_item_occurrences (
    {_RK04_SEMANTIC_KEY},
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    PRIMARY KEY (
        capture_id, derivation_version_id,
        within_capture_identity, item_index
    ),
    CONSTRAINT rk04_monthly_occ_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_MONTHLY_KIND}'),
    CONSTRAINT rk04_monthly_occ_parent
        FOREIGN KEY (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
        REFERENCES related_keywords_monthly_search_volume (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

RELATED_KEYWORDS_RELATIONSHIP_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_relationship_occurrences (
    {_RK04_SEMANTIC_KEY},
    source_item_index BIGINT NOT NULL
        CHECK (source_item_index >= 0 AND source_item_index <= {_IJSON_MAX}),
    target_index BIGINT NOT NULL
        CHECK (target_index >= 0 AND target_index <= {_IJSON_MAX}),
    source_depth BIGINT NOT NULL
        CHECK (source_depth >= 0 AND source_depth <= 4),
    PRIMARY KEY (
        capture_id, derivation_version_id, within_capture_identity,
        source_item_index, target_index
    ),
    CONSTRAINT rk04_rel_occ_kind
        CHECK (observation_kind = '{RELATED_KEYWORDS_RELATIONSHIP_KIND}'),
    CONSTRAINT rk04_rel_occ_parent
        FOREIGN KEY (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
        REFERENCES related_keywords_relationship (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

RELATED_KEYWORDS_CONTEXT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS related_keywords_result_context (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '{_HEX64}'),
    requested_seed TEXT NOT NULL
        CHECK (char_length(requested_seed) >= 1),
    request_location_code BIGINT NOT NULL
        CHECK (request_location_code >= 0
               AND request_location_code <= {_IJSON_MAX}),
    request_language_code TEXT NOT NULL,
    request_depth BIGINT NOT NULL
        CHECK (request_depth >= 0 AND request_depth <= {_IJSON_MAX}),
    request_limit BIGINT NOT NULL
        CHECK (request_limit >= 0 AND request_limit <= {_IJSON_MAX}),
    request_offset BIGINT NOT NULL
        CHECK (request_offset >= 0 AND request_offset <= {_IJSON_MAX}),
    request_order_by TEXT[] NOT NULL,
    request_include_seed_keyword BOOLEAN NOT NULL,
    request_include_serp_info BOOLEAN NOT NULL,
    request_include_clickstream_data BOOLEAN NOT NULL,
    request_ignore_synonyms BOOLEAN NOT NULL,
    request_replace_with_core_keyword BOOLEAN NOT NULL,
    result_seed_keyword TEXT NOT NULL,
    result_location_code BIGINT
        {_rk04_nonneg("result_location_code")},
    result_location_code_state TEXT NOT NULL
        CHECK (result_location_code_state {_FIELD_STATE_CHECK}),
    result_language_code TEXT,
    result_language_code_state TEXT NOT NULL
        CHECK (result_language_code_state {_FIELD_STATE_CHECK}),
    result_se_type TEXT,
    result_se_type_state TEXT NOT NULL
        CHECK (result_se_type_state {_FIELD_STATE_CHECK}),
    total_count BIGINT NOT NULL
        CHECK (total_count >= 0 AND total_count <= {_IJSON_MAX}),
    items_count BIGINT NOT NULL
        CHECK (items_count >= 0 AND items_count <= {_IJSON_MAX}),
    seed_keyword_data_state TEXT NOT NULL
        CHECK (seed_keyword_data_state {_FIELD_STATE_CHECK}),
    derived_returned_item_count BIGINT NOT NULL
        CHECK (derived_returned_item_count >= 0
               AND derived_returned_item_count <= {_IJSON_MAX}),
    derived_relationship_occurrence_count BIGINT NOT NULL
        CHECK (derived_relationship_occurrence_count >= 0
               AND derived_relationship_occurrence_count <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id),
    CONSTRAINT rk04_context_outcome
        FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
        REFERENCES outcomes (derivation_version_id, attempt_id, capture_id),
    {_rk04_consistency("rk04_ctx_location_ck", "result_location_code")},
    {_rk04_consistency("rk04_ctx_language_ck", "result_language_code")},
    {_rk04_consistency("rk04_ctx_se_type_ck", "result_se_type")}
)
"""

RK04_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    RELATED_KEYWORDS_KEYWORD_DATA_SQL,
    RELATED_KEYWORDS_KEYWORD_INFO_SQL,
    RELATED_KEYWORDS_KEYWORD_PROPERTIES_SQL,
    RELATED_KEYWORDS_AVG_BACKLINKS_SQL,
    RELATED_KEYWORDS_SEARCH_INTENT_SQL,
    RELATED_KEYWORDS_SERP_INFO_SQL,
    RELATED_KEYWORDS_MONTHLY_SQL,
    RELATED_KEYWORDS_RELATIONSHIP_SQL,
    RELATED_KEYWORDS_ITEM_OCCURRENCES_SQL,
    RELATED_KEYWORDS_MONTHLY_OCCURRENCES_SQL,
    RELATED_KEYWORDS_RELATIONSHIP_OCCURRENCES_SQL,
    RELATED_KEYWORDS_CONTEXT_SQL,
)


# --------------------------------------------------------------------------------------
# RANK-05 — DataForSEO Google Ranked Keywords typed relations
#
# Exactly twelve relations on top of the generic Recipe/Outcome/envelope/diagnostic
# substrate. Four are kind-bound semantic parents, five are keyword-data children, two are
# provider occurrence relations, and one is the admitted result context.
#
# No relation exposes a generic `provider_update_time` or universal `last_updated`. The four
# time pillars stay separate: acquisition provenance never enters these tables, monthly
# `(year, month)` is a Data Period, the SERP/placement clocks keep `ranked_element_*` and
# `keyword_serp_*` source-local names, and each enrichment clock is named for the exact
# structure that stated it.
# --------------------------------------------------------------------------------------

RANKED_KEYWORDS_CORPUS_METRICS_KIND: Final[str] = (
    "dataforseo.google.ranked_keywords.corpus_metrics.v1"
)
RANKED_KEYWORDS_RANKED_RESULT_KIND: Final[str] = (
    "dataforseo.google.ranked_keywords.ranked_result.v1"
)
RANKED_KEYWORDS_KEYWORD_DATA_KIND: Final[str] = (
    "dataforseo.google.ranked_keywords.keyword_data.v1"
)
RANKED_KEYWORDS_MONTHLY_KIND: Final[str] = (
    "dataforseo.google.ranked_keywords.monthly_search_volume.v1"
)

_RANK05_FAMILY_CHECK: Final[str] = (
    "IN ('organic', 'paid', 'featured_snippet', 'local_pack', "
    "'ai_overview_reference')"
)
_RANK05_RANK_SYSTEM_CHECK: Final[str] = "IN ('rank_group', 'rank_absolute')"
_RANK05_BUCKET_COLUMNS: Final[tuple[str, ...]] = (
    "pos_1",
    "pos_2_3",
    "pos_4_10",
    "pos_11_20",
    "pos_21_30",
    "pos_31_40",
    "pos_41_50",
    "pos_51_60",
    "pos_61_70",
    "pos_71_80",
    "pos_81_90",
    "pos_91_100",
)
_RANK05_MOVEMENT_COLUMNS: Final[tuple[str, ...]] = (
    "is_new",
    "is_up",
    "is_down",
    "is_lost",
)


def _rank05_consistency(name: str, column: str) -> str:
    """Short-named state/value consistency CHECK for one RANK-05 column pair.

    Same reason as RK-04: `_state_value_consistency` derives its constraint name from the
    table name, and several Ranked table names would push a generated constraint name past
    PostgreSQL's 63-byte identifier limit and be silently truncated.
    """

    return (
        f"CONSTRAINT {name} "
        f"CHECK (({column}_state = 'stated' AND {column} IS NOT NULL) "
        f"OR ({column}_state <> 'stated' AND {column} IS NULL))"
    )


def _rank05_clock(column: str, name: str) -> str:
    """One structure-local provider clock column pair.

    Each Ranked clock carries the name of the exact provider structure that stated it. The
    Ranked-element and keyword-SERP loci agree in the frozen fixture; that agreement is
    testimony, so they still get two independent columns that may disagree.
    """

    return (
        f"{column} TEXT\n"
        f"        CHECK ({column} IS NULL OR {column} ~ '{_CLOCK_RE}'),\n"
        f"    {column}_state TEXT NOT NULL\n"
        f"        CHECK ({column}_state {_FIELD_STATE_CHECK}),\n"
        f"    {_rank05_consistency(name, column)}"
    )


def _rank05_nonneg(column: str) -> str:
    return f"CHECK ({column} IS NULL OR ({column} >= 0 AND {column} <= {_IJSON_MAX}))"


def _rank05_signed(column: str) -> str:
    return (
        f"CHECK ({column} IS NULL OR "
        f"({column} >= -{_IJSON_MAX} AND {column} <= {_IJSON_MAX}))"
    )


def _rank05_state_only(column: str) -> str:
    """A Field state persisted without any value column.

    Used for the five parser-v1 null-only unsupported SERP children and for the three
    [CHAZ] Option 1 prose fields, whose ABSENT/JSON_NULL/STATED distinction is preserved
    while the text itself stays Evidence-only under Recipe v1.
    """

    return (
        f"{column}_state TEXT NOT NULL\n"
        f"        CHECK ({column}_state {_FIELD_STATE_CHECK})"
    )


_RANK05_SEMANTIC_KEY: Final[str] = f"""capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '{_HEX64}'),
    observation_kind TEXT NOT NULL"""


def _rank05_keyword_child_fk(constraint: str) -> str:
    return f"""CONSTRAINT {constraint}
        FOREIGN KEY (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
        REFERENCES ranked_keywords_keyword_data (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )"""


_RANK05_BUCKETS_SQL: Final[str] = ",\n    ".join(
    f"{column} BIGINT NOT NULL\n"
    f"        CHECK ({column} >= 0 AND {column} <= {_IJSON_MAX})"
    for column in _RANK05_BUCKET_COLUMNS
)
_RANK05_MOVEMENT_SQL: Final[str] = ",\n    ".join(
    f"{column} BIGINT NOT NULL\n"
    f"        CHECK ({column} >= 0 AND {column} <= {_IJSON_MAX})"
    for column in _RANK05_MOVEMENT_COLUMNS
)

RANKED_KEYWORDS_CORPUS_METRICS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_corpus_metrics (
    {_RANK05_SEMANTIC_KEY},
    requested_target TEXT NOT NULL
        CHECK (char_length(requested_target) >= 1),
    aggregate_family TEXT NOT NULL
        CHECK (aggregate_family {_RANK05_FAMILY_CHECK}),
    rank_system TEXT NOT NULL
        CHECK (rank_system {_RANK05_RANK_SYSTEM_CHECK}),
    {_RANK05_BUCKETS_SQL},
    {_RANK05_MOVEMENT_SQL},
    count BIGINT
        {_rank05_nonneg("count")},
    count_state TEXT NOT NULL
        CHECK (count_state {_FIELD_STATE_CHECK}),
    etv NUMERIC,
    etv_state TEXT NOT NULL
        CHECK (etv_state {_FIELD_STATE_CHECK}),
    estimated_paid_traffic_cost NUMERIC,
    estimated_paid_traffic_cost_state TEXT NOT NULL
        CHECK (estimated_paid_traffic_cost_state {_FIELD_STATE_CHECK}),
    {_rank05_state_only("clickstream_etv")},
    {_rank05_state_only("clickstream_gender_distribution")},
    {_rank05_state_only("clickstream_age_distribution")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_corpus_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_CORPUS_METRICS_KIND}'),
    CONSTRAINT rank05_corpus_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT rank05_corpus_absolute_locus
        CHECK (
            rank_system = 'rank_group'
            OR (count_state = 'inapplicable'
                AND etv_state = 'inapplicable'
                AND estimated_paid_traffic_cost_state = 'inapplicable')
        ),
    {_rank05_consistency("rank05_cm_count_ck", "count")},
    {_rank05_consistency("rank05_cm_etv_ck", "etv")},
    {_rank05_consistency("rank05_cm_cost_ck", "estimated_paid_traffic_cost")},
    {_ENVELOPE_FK}
)
"""

RANKED_KEYWORDS_RANKED_RESULTS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_ranked_results (
    {_RANK05_SEMANTIC_KEY},
    requested_target TEXT NOT NULL
        CHECK (char_length(requested_target) >= 1),
    keyword TEXT NOT NULL
        CHECK (char_length(keyword) >= 1),
    serp_item_type TEXT NOT NULL
        CHECK (char_length(serp_item_type) >= 1),
    rank_group BIGINT NOT NULL
        CHECK (rank_group >= 0 AND rank_group <= {_IJSON_MAX}),
    rank_absolute BIGINT NOT NULL
        CHECK (rank_absolute >= 0 AND rank_absolute <= {_IJSON_MAX}),
    ranked_element_se_type TEXT,
    ranked_element_se_type_state TEXT NOT NULL
        CHECK (ranked_element_se_type_state {_FIELD_STATE_CHECK}),
    ranked_element_check_url TEXT,
    ranked_element_check_url_state TEXT NOT NULL
        CHECK (ranked_element_check_url_state {_FIELD_STATE_CHECK}),
    ranked_element_se_results_count BIGINT
        {_rank05_nonneg("ranked_element_se_results_count")},
    ranked_element_se_results_count_state TEXT NOT NULL
        CHECK (ranked_element_se_results_count_state {_FIELD_STATE_CHECK}),
    ranked_element_keyword_difficulty BIGINT
        {_rank05_nonneg("ranked_element_keyword_difficulty")},
    ranked_element_keyword_difficulty_state TEXT NOT NULL
        CHECK (ranked_element_keyword_difficulty_state {_FIELD_STATE_CHECK}),
    ranked_element_is_lost BOOLEAN,
    ranked_element_is_lost_state TEXT NOT NULL
        CHECK (ranked_element_is_lost_state {_FIELD_STATE_CHECK}),
    ranked_element_serp_item_types TEXT[],
    ranked_element_serp_item_types_state TEXT NOT NULL
        CHECK (ranked_element_serp_item_types_state {_FIELD_STATE_CHECK}),
    {_rank05_clock("ranked_element_last_updated_time", "rank05_rr_el_last_ck")},
    {_rank05_clock("ranked_element_previous_updated_time", "rank05_rr_el_prev_ck")},
    serp_item_se_type TEXT,
    serp_item_se_type_state TEXT NOT NULL
        CHECK (serp_item_se_type_state {_FIELD_STATE_CHECK}),
    url TEXT NOT NULL
        CHECK (char_length(url) >= 1),
    position TEXT,
    position_state TEXT NOT NULL
        CHECK (position_state {_FIELD_STATE_CHECK}),
    xpath TEXT,
    xpath_state TEXT NOT NULL
        CHECK (xpath_state {_FIELD_STATE_CHECK}),
    domain TEXT,
    domain_state TEXT NOT NULL
        CHECK (domain_state {_FIELD_STATE_CHECK}),
    main_domain TEXT,
    main_domain_state TEXT NOT NULL
        CHECK (main_domain_state {_FIELD_STATE_CHECK}),
    website_name TEXT,
    website_name_state TEXT NOT NULL
        CHECK (website_name_state {_FIELD_STATE_CHECK}),
    relative_url TEXT,
    relative_url_state TEXT NOT NULL
        CHECK (relative_url_state {_FIELD_STATE_CHECK}),
    title TEXT,
    title_state TEXT NOT NULL
        CHECK (title_state {_FIELD_STATE_CHECK}),
    description TEXT,
    description_state TEXT NOT NULL
        CHECK (description_state {_FIELD_STATE_CHECK}),
    {_rank05_state_only("breadcrumb")},
    {_rank05_state_only("pre_snippet")},
    {_rank05_state_only("highlighted")},
    is_image BOOLEAN,
    is_image_state TEXT NOT NULL
        CHECK (is_image_state {_FIELD_STATE_CHECK}),
    is_video BOOLEAN,
    is_video_state TEXT NOT NULL
        CHECK (is_video_state {_FIELD_STATE_CHECK}),
    is_featured_snippet BOOLEAN,
    is_featured_snippet_state TEXT NOT NULL
        CHECK (is_featured_snippet_state {_FIELD_STATE_CHECK}),
    is_malicious BOOLEAN,
    is_malicious_state TEXT NOT NULL
        CHECK (is_malicious_state {_FIELD_STATE_CHECK}),
    amp_version BOOLEAN,
    amp_version_state TEXT NOT NULL
        CHECK (amp_version_state {_FIELD_STATE_CHECK}),
    etv NUMERIC,
    etv_state TEXT NOT NULL
        CHECK (etv_state {_FIELD_STATE_CHECK}),
    estimated_paid_traffic_cost NUMERIC,
    estimated_paid_traffic_cost_state TEXT NOT NULL
        CHECK (estimated_paid_traffic_cost_state {_FIELD_STATE_CHECK}),
    {_rank05_state_only("clickstream_etv")},
    rank_changes_state TEXT NOT NULL
        CHECK (rank_changes_state {_FIELD_STATE_CHECK}),
    rank_changes_is_new BOOLEAN,
    rank_changes_is_new_state TEXT NOT NULL
        CHECK (rank_changes_is_new_state {_FIELD_STATE_CHECK}),
    rank_changes_is_up BOOLEAN,
    rank_changes_is_up_state TEXT NOT NULL
        CHECK (rank_changes_is_up_state {_FIELD_STATE_CHECK}),
    rank_changes_is_down BOOLEAN,
    rank_changes_is_down_state TEXT NOT NULL
        CHECK (rank_changes_is_down_state {_FIELD_STATE_CHECK}),
    rank_changes_previous_rank_absolute BIGINT
        {_rank05_nonneg("rank_changes_previous_rank_absolute")},
    rank_changes_previous_rank_absolute_state TEXT NOT NULL
        CHECK (rank_changes_previous_rank_absolute_state {_FIELD_STATE_CHECK}),
    rank_info_state TEXT NOT NULL
        CHECK (rank_info_state {_FIELD_STATE_CHECK}),
    rank_info_page_rank BIGINT
        {_rank05_nonneg("rank_info_page_rank")},
    rank_info_page_rank_state TEXT NOT NULL
        CHECK (rank_info_page_rank_state {_FIELD_STATE_CHECK}),
    rank_info_main_domain_rank BIGINT
        {_rank05_nonneg("rank_info_main_domain_rank")},
    rank_info_main_domain_rank_state TEXT NOT NULL
        CHECK (rank_info_main_domain_rank_state {_FIELD_STATE_CHECK}),
    {_rank05_state_only("about_this_result")},
    {_rank05_state_only("backlinks_info")},
    {_rank05_state_only("extended_snippet")},
    {_rank05_state_only("links")},
    {_rank05_state_only("rating")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_ranked_result_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_RANKED_RESULT_KIND}'),
    CONSTRAINT rank05_ranked_result_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_rank05_consistency("rank05_rr_el_se_type_ck", "ranked_element_se_type")},
    {_rank05_consistency("rank05_rr_el_check_url_ck", "ranked_element_check_url")},
    {_rank05_consistency("rank05_rr_el_results_ck", "ranked_element_se_results_count")},
    {_rank05_consistency("rank05_rr_el_kd_ck", "ranked_element_keyword_difficulty")},
    {_rank05_consistency("rank05_rr_el_lost_ck", "ranked_element_is_lost")},
    {_rank05_consistency("rank05_rr_el_types_ck", "ranked_element_serp_item_types")},
    {_rank05_consistency("rank05_rr_si_se_type_ck", "serp_item_se_type")},
    {_rank05_consistency("rank05_rr_position_ck", "position")},
    {_rank05_consistency("rank05_rr_xpath_ck", "xpath")},
    {_rank05_consistency("rank05_rr_domain_ck", "domain")},
    {_rank05_consistency("rank05_rr_main_domain_ck", "main_domain")},
    {_rank05_consistency("rank05_rr_website_ck", "website_name")},
    {_rank05_consistency("rank05_rr_relative_ck", "relative_url")},
    {_rank05_consistency("rank05_rr_title_ck", "title")},
    {_rank05_consistency("rank05_rr_description_ck", "description")},
    {_rank05_consistency("rank05_rr_is_image_ck", "is_image")},
    {_rank05_consistency("rank05_rr_is_video_ck", "is_video")},
    {_rank05_consistency("rank05_rr_is_fs_ck", "is_featured_snippet")},
    {_rank05_consistency("rank05_rr_is_malicious_ck", "is_malicious")},
    {_rank05_consistency("rank05_rr_amp_ck", "amp_version")},
    {_rank05_consistency("rank05_rr_etv_ck", "etv")},
    {_rank05_consistency("rank05_rr_cost_ck", "estimated_paid_traffic_cost")},
    {_rank05_consistency("rank05_rr_rc_new_ck", "rank_changes_is_new")},
    {_rank05_consistency("rank05_rr_rc_up_ck", "rank_changes_is_up")},
    {_rank05_consistency("rank05_rr_rc_down_ck", "rank_changes_is_down")},
    {_rank05_consistency("rank05_rr_rc_prev_ck", "rank_changes_previous_rank_absolute")},
    {_rank05_consistency("rank05_rr_ri_page_ck", "rank_info_page_rank")},
    {_rank05_consistency("rank05_rr_ri_main_ck", "rank_info_main_domain_rank")},
    {_ENVELOPE_FK}
)
"""

RANKED_KEYWORDS_KEYWORD_DATA_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_keyword_data (
    {_RANK05_SEMANTIC_KEY},
    requested_target TEXT NOT NULL
        CHECK (char_length(requested_target) >= 1),
    keyword TEXT NOT NULL
        CHECK (char_length(keyword) >= 1),
    location_code BIGINT
        {_rank05_nonneg("location_code")},
    location_code_state TEXT NOT NULL
        CHECK (location_code_state {_FIELD_STATE_CHECK}),
    language_code TEXT,
    language_code_state TEXT NOT NULL
        CHECK (language_code_state {_FIELD_STATE_CHECK}),
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    keyword_info_state TEXT NOT NULL
        CHECK (keyword_info_state {_FIELD_STATE_CHECK}),
    keyword_properties_state TEXT NOT NULL
        CHECK (keyword_properties_state {_FIELD_STATE_CHECK}),
    avg_backlinks_state TEXT NOT NULL
        CHECK (avg_backlinks_state {_FIELD_STATE_CHECK}),
    search_intent_state TEXT NOT NULL
        CHECK (search_intent_state {_FIELD_STATE_CHECK}),
    keyword_serp_info_state TEXT NOT NULL
        CHECK (keyword_serp_info_state {_FIELD_STATE_CHECK}),
    bing_normalized_state TEXT NOT NULL
        CHECK (bing_normalized_state {_FIELD_STATE_CHECK}),
    clickstream_normalized_state TEXT NOT NULL
        CHECK (clickstream_normalized_state {_FIELD_STATE_CHECK}),
    clickstream_keyword_info_state TEXT NOT NULL
        CHECK (clickstream_keyword_info_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_keyword_data_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    CONSTRAINT rank05_keyword_data_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_rank05_consistency("rank05_kd_location_ck", "location_code")},
    {_rank05_consistency("rank05_kd_language_ck", "language_code")},
    {_rank05_consistency("rank05_kd_se_type_ck", "se_type")},
    {_ENVELOPE_FK}
)
"""

RANKED_KEYWORDS_KEYWORD_INFO_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_keyword_info (
    {_RANK05_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    {_rank05_clock("keyword_info_last_updated_time", "rank05_ki_clock_ck")},
    competition NUMERIC,
    competition_state TEXT NOT NULL
        CHECK (competition_state {_FIELD_STATE_CHECK}),
    competition_level TEXT,
    competition_level_state TEXT NOT NULL
        CHECK (competition_level_state {_FIELD_STATE_CHECK}),
    cpc NUMERIC,
    cpc_state TEXT NOT NULL
        CHECK (cpc_state {_FIELD_STATE_CHECK}),
    search_volume BIGINT
        {_rank05_nonneg("search_volume")},
    search_volume_state TEXT NOT NULL
        CHECK (search_volume_state {_FIELD_STATE_CHECK}),
    low_top_of_page_bid NUMERIC,
    low_top_of_page_bid_state TEXT NOT NULL
        CHECK (low_top_of_page_bid_state {_FIELD_STATE_CHECK}),
    high_top_of_page_bid NUMERIC,
    high_top_of_page_bid_state TEXT NOT NULL
        CHECK (high_top_of_page_bid_state {_FIELD_STATE_CHECK}),
    categories BIGINT[],
    categories_state TEXT NOT NULL
        CHECK (categories_state {_FIELD_STATE_CHECK}),
    monthly_searches_state TEXT NOT NULL
        CHECK (monthly_searches_state {_FIELD_STATE_CHECK}),
    search_volume_trend_state TEXT NOT NULL
        CHECK (search_volume_trend_state {_FIELD_STATE_CHECK}),
    trend_monthly BIGINT
        {_rank05_signed("trend_monthly")},
    trend_monthly_state TEXT NOT NULL
        CHECK (trend_monthly_state {_FIELD_STATE_CHECK}),
    trend_quarterly BIGINT
        {_rank05_signed("trend_quarterly")},
    trend_quarterly_state TEXT NOT NULL
        CHECK (trend_quarterly_state {_FIELD_STATE_CHECK}),
    trend_yearly BIGINT
        {_rank05_signed("trend_yearly")},
    trend_yearly_state TEXT NOT NULL
        CHECK (trend_yearly_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_keyword_info_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rank05_consistency("rank05_ki_se_type_ck", "se_type")},
    {_rank05_consistency("rank05_ki_competition_ck", "competition")},
    {_rank05_consistency("rank05_ki_comp_level_ck", "competition_level")},
    {_rank05_consistency("rank05_ki_cpc_ck", "cpc")},
    {_rank05_consistency("rank05_ki_volume_ck", "search_volume")},
    {_rank05_consistency("rank05_ki_low_bid_ck", "low_top_of_page_bid")},
    {_rank05_consistency("rank05_ki_high_bid_ck", "high_top_of_page_bid")},
    {_rank05_consistency("rank05_ki_categories_ck", "categories")},
    {_rank05_consistency("rank05_ki_trend_m_ck", "trend_monthly")},
    {_rank05_consistency("rank05_ki_trend_q_ck", "trend_quarterly")},
    {_rank05_consistency("rank05_ki_trend_y_ck", "trend_yearly")},
    {_rank05_keyword_child_fk("rank05_keyword_info_parent")}
)
"""

RANKED_KEYWORDS_KEYWORD_PROPERTIES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_keyword_properties (
    {_RANK05_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    core_keyword TEXT,
    core_keyword_state TEXT NOT NULL
        CHECK (core_keyword_state {_FIELD_STATE_CHECK}),
    synonym_clustering_algorithm TEXT,
    synonym_clustering_algorithm_state TEXT NOT NULL
        CHECK (synonym_clustering_algorithm_state {_FIELD_STATE_CHECK}),
    keyword_difficulty BIGINT
        {_rank05_nonneg("keyword_difficulty")},
    keyword_difficulty_state TEXT NOT NULL
        CHECK (keyword_difficulty_state {_FIELD_STATE_CHECK}),
    detected_language TEXT,
    detected_language_state TEXT NOT NULL
        CHECK (detected_language_state {_FIELD_STATE_CHECK}),
    is_another_language BOOLEAN,
    is_another_language_state TEXT NOT NULL
        CHECK (is_another_language_state {_FIELD_STATE_CHECK}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_properties_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rank05_consistency("rank05_kp_se_type_ck", "se_type")},
    {_rank05_consistency("rank05_kp_core_ck", "core_keyword")},
    {_rank05_consistency("rank05_kp_algorithm_ck", "synonym_clustering_algorithm")},
    {_rank05_consistency("rank05_kp_difficulty_ck", "keyword_difficulty")},
    {_rank05_consistency("rank05_kp_language_ck", "detected_language")},
    {_rank05_consistency("rank05_kp_another_ck", "is_another_language")},
    {_rank05_keyword_child_fk("rank05_properties_parent")}
)
"""

RANKED_KEYWORDS_AVG_BACKLINKS_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_avg_backlinks (
    {_RANK05_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
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
    {_rank05_clock("avg_backlinks_last_updated_time", "rank05_bl_clock_ck")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_backlinks_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rank05_consistency("rank05_bl_se_type_ck", "se_type")},
    {_rank05_consistency("rank05_bl_backlinks_ck", "backlinks")},
    {_rank05_consistency("rank05_bl_dofollow_ck", "dofollow")},
    {_rank05_consistency("rank05_bl_ref_pages_ck", "referring_pages")},
    {_rank05_consistency("rank05_bl_ref_domains_ck", "referring_domains")},
    {_rank05_consistency("rank05_bl_ref_main_ck", "referring_main_domains")},
    {_rank05_consistency("rank05_bl_rank_ck", "rank")},
    {_rank05_consistency("rank05_bl_main_rank_ck", "main_domain_rank")},
    {_rank05_keyword_child_fk("rank05_backlinks_parent")}
)
"""

RANKED_KEYWORDS_SEARCH_INTENT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_search_intent (
    {_RANK05_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    main_intent TEXT,
    main_intent_state TEXT NOT NULL
        CHECK (main_intent_state {_FIELD_STATE_CHECK}),
    foreign_intent TEXT[],
    foreign_intent_state TEXT NOT NULL
        CHECK (foreign_intent_state {_FIELD_STATE_CHECK}),
    {_rank05_clock("search_intent_last_updated_time", "rank05_si_clock_ck")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_intent_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rank05_consistency("rank05_si_se_type_ck", "se_type")},
    {_rank05_consistency("rank05_si_main_ck", "main_intent")},
    {_rank05_consistency("rank05_si_foreign_ck", "foreign_intent")},
    {_rank05_keyword_child_fk("rank05_intent_parent")}
)
"""

RANKED_KEYWORDS_KEYWORD_SERP_INFO_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_keyword_serp_info (
    {_RANK05_SEMANTIC_KEY},
    se_type TEXT,
    se_type_state TEXT NOT NULL
        CHECK (se_type_state {_FIELD_STATE_CHECK}),
    check_url TEXT,
    check_url_state TEXT NOT NULL
        CHECK (check_url_state {_FIELD_STATE_CHECK}),
    serp_item_types TEXT[],
    serp_item_types_state TEXT NOT NULL
        CHECK (serp_item_types_state {_FIELD_STATE_CHECK}),
    se_results_count BIGINT
        {_rank05_nonneg("se_results_count")},
    se_results_count_state TEXT NOT NULL
        CHECK (se_results_count_state {_FIELD_STATE_CHECK}),
    {_rank05_clock("keyword_serp_last_updated_time", "rank05_kserp_last_ck")},
    {_rank05_clock("keyword_serp_previous_updated_time", "rank05_kserp_prev_ck")},
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_keyword_serp_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    {_rank05_consistency("rank05_kserp_se_type_ck", "se_type")},
    {_rank05_consistency("rank05_kserp_url_ck", "check_url")},
    {_rank05_consistency("rank05_kserp_types_ck", "serp_item_types")},
    {_rank05_consistency("rank05_kserp_count_ck", "se_results_count")},
    {_rank05_keyword_child_fk("rank05_keyword_serp_parent")}
)
"""

RANKED_KEYWORDS_MONTHLY_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_monthly_search_volume (
    {_RANK05_SEMANTIC_KEY},
    requested_target TEXT NOT NULL
        CHECK (char_length(requested_target) >= 1),
    keyword TEXT NOT NULL
        CHECK (char_length(keyword) >= 1),
    year BIGINT NOT NULL
        CHECK (year >= 1 AND year <= 9999),
    month BIGINT NOT NULL
        CHECK (month >= 1 AND month <= 12),
    search_volume BIGINT NOT NULL
        CHECK (search_volume >= 0 AND search_volume <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity),
    CONSTRAINT rank05_monthly_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_MONTHLY_KIND}'),
    CONSTRAINT rank05_monthly_parent
        UNIQUE (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    {_ENVELOPE_FK}
)
"""

RANKED_KEYWORDS_ITEM_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_item_occurrences (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL,
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    ranked_result_identity TEXT NOT NULL
        CHECK (ranked_result_identity ~ '{_HEX64}'),
    ranked_result_kind TEXT NOT NULL,
    keyword_data_identity TEXT NOT NULL
        CHECK (keyword_data_identity ~ '{_HEX64}'),
    keyword_data_kind TEXT NOT NULL,
    item_se_type TEXT NOT NULL,
    PRIMARY KEY (capture_id, derivation_version_id, item_index),
    CONSTRAINT rank05_item_occ_result_kind
        CHECK (ranked_result_kind = '{RANKED_KEYWORDS_RANKED_RESULT_KIND}'),
    CONSTRAINT rank05_item_occ_keyword_kind
        CHECK (keyword_data_kind = '{RANKED_KEYWORDS_KEYWORD_DATA_KIND}'),
    CONSTRAINT rank05_item_occ_result_parent
        FOREIGN KEY (
            capture_id, derivation_version_id,
            ranked_result_identity, ranked_result_kind
        )
        REFERENCES ranked_keywords_ranked_results (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        ),
    CONSTRAINT rank05_item_occ_keyword_parent
        FOREIGN KEY (
            capture_id, derivation_version_id,
            keyword_data_identity, keyword_data_kind
        )
        REFERENCES ranked_keywords_keyword_data (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

RANKED_KEYWORDS_MONTHLY_OCCURRENCES_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_monthly_item_occurrences (
    {_RANK05_SEMANTIC_KEY},
    item_index BIGINT NOT NULL
        CHECK (item_index >= 0 AND item_index <= {_IJSON_MAX}),
    PRIMARY KEY (
        capture_id, derivation_version_id,
        within_capture_identity, item_index
    ),
    CONSTRAINT rank05_monthly_occ_kind
        CHECK (observation_kind = '{RANKED_KEYWORDS_MONTHLY_KIND}'),
    CONSTRAINT rank05_monthly_occ_parent
        FOREIGN KEY (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
        REFERENCES ranked_keywords_monthly_search_volume (
            capture_id, derivation_version_id,
            within_capture_identity, observation_kind
        )
)
"""

RANKED_KEYWORDS_CONTEXT_SQL: Final[str] = f"""
CREATE TABLE IF NOT EXISTS ranked_keywords_result_context (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '{_HEX64}'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '{_HEX64}'),
    requested_target TEXT NOT NULL
        CHECK (char_length(requested_target) >= 1),
    request_location_code BIGINT NOT NULL
        CHECK (request_location_code >= 0
               AND request_location_code <= {_IJSON_MAX}),
    request_language_code TEXT NOT NULL,
    request_item_types TEXT[] NOT NULL,
    request_ignore_synonyms BOOLEAN NOT NULL,
    request_include_clickstream_data BOOLEAN NOT NULL,
    request_limit BIGINT NOT NULL
        CHECK (request_limit >= 0 AND request_limit <= {_IJSON_MAX}),
    request_offset BIGINT NOT NULL
        CHECK (request_offset >= 0 AND request_offset <= {_IJSON_MAX}),
    request_load_rank_absolute BOOLEAN NOT NULL,
    request_historical_serp_mode TEXT NOT NULL,
    request_order_by TEXT[] NOT NULL,
    result_target TEXT,
    result_target_state TEXT NOT NULL
        CHECK (result_target_state {_FIELD_STATE_CHECK}),
    result_location_code BIGINT
        {_rank05_nonneg("result_location_code")},
    result_location_code_state TEXT NOT NULL
        CHECK (result_location_code_state {_FIELD_STATE_CHECK}),
    result_language_code TEXT,
    result_language_code_state TEXT NOT NULL
        CHECK (result_language_code_state {_FIELD_STATE_CHECK}),
    result_se_type TEXT,
    result_se_type_state TEXT NOT NULL
        CHECK (result_se_type_state {_FIELD_STATE_CHECK}),
    total_count BIGINT NOT NULL
        CHECK (total_count >= 0 AND total_count <= {_IJSON_MAX}),
    items_count BIGINT NOT NULL
        CHECK (items_count >= 0 AND items_count <= {_IJSON_MAX}),
    PRIMARY KEY (capture_id, derivation_version_id),
    CONSTRAINT rank05_context_outcome
        FOREIGN KEY (derivation_version_id, attempt_id, capture_id)
        REFERENCES outcomes (derivation_version_id, attempt_id, capture_id),
    {_rank05_consistency("rank05_ctx_target_ck", "result_target")},
    {_rank05_consistency("rank05_ctx_location_ck", "result_location_code")},
    {_rank05_consistency("rank05_ctx_language_ck", "result_language_code")},
    {_rank05_consistency("rank05_ctx_se_type_ck", "result_se_type")}
)
"""

RANK05_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    RANKED_KEYWORDS_CORPUS_METRICS_SQL,
    RANKED_KEYWORDS_RANKED_RESULTS_SQL,
    RANKED_KEYWORDS_KEYWORD_DATA_SQL,
    RANKED_KEYWORDS_KEYWORD_INFO_SQL,
    RANKED_KEYWORDS_KEYWORD_PROPERTIES_SQL,
    RANKED_KEYWORDS_AVG_BACKLINKS_SQL,
    RANKED_KEYWORDS_SEARCH_INTENT_SQL,
    RANKED_KEYWORDS_KEYWORD_SERP_INFO_SQL,
    RANKED_KEYWORDS_MONTHLY_SQL,
    RANKED_KEYWORDS_ITEM_OCCURRENCES_SQL,
    RANKED_KEYWORDS_MONTHLY_OCCURRENCES_SQL,
    RANKED_KEYWORDS_CONTEXT_SQL,
)



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

PRE_AI05_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = PRE_PF12_SCHEMA_STATEMENTS + (
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

PRE_AI11_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = PRE_AI05_SCHEMA_STATEMENTS + (
    SEARCH_MENTIONS_ITEMS_SQL,
    SEARCH_MENTIONS_ITEM_OCCURRENCES_SQL,
    SEARCH_MENTIONS_MONTHLY_SQL,
    SEARCH_MENTIONS_MONTHLY_OCCURRENCES_SQL,
    SEARCH_MENTIONS_SOURCES_SQL,
    SEARCH_MENTIONS_SOURCE_OCCURRENCES_SQL,
    SEARCH_MENTIONS_CONTEXT_SQL,
)

PRE_AI16_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = PRE_AI11_SCHEMA_STATEMENTS + (
    TARGET_METRICS_TOTALS_SQL,
    TARGET_METRICS_SOURCE_DOMAINS_SQL,
    TARGET_METRICS_CONTEXT_SQL,
)

PRE_RK04_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = PRE_AI16_SCHEMA_STATEMENTS + (
    LLM_MENTIONS_HISTORICAL_MONTHLY_SQL,
    LLM_MENTIONS_HISTORICAL_CONTEXT_SQL,
    LLM_MENTIONS_HISTORICAL_UNRETURNED_SQL,
)

PRE_RANK05_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    PRE_RK04_SCHEMA_STATEMENTS + RK04_SCHEMA_STATEMENTS
)

PF18_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    GOOGLE_ORGANIC_FEATURES_PARENT_UNIQUE_SQL,
    GOOGLE_ORGANIC_RANKED_V2_SQL,
    GOOGLE_ORGANIC_TOP_STORY_SQL,
    GOOGLE_ORGANIC_TOP_STORY_OCCURRENCES_SQL,
    GOOGLE_ORGANIC_VIDEO_SQL,
    GOOGLE_ORGANIC_VIDEO_OCCURRENCES_SQL,
    GOOGLE_ORGANIC_SITELINK_SQL,
    GOOGLE_ORGANIC_SITELINK_OCCURRENCES_SQL,
)

PRE_PF18_SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    PRE_RANK05_SCHEMA_STATEMENTS + RANK05_SCHEMA_STATEMENTS
)

SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    PRE_PF18_SCHEMA_STATEMENTS + PF18_SCHEMA_STATEMENTS
)

WIDEN_IJSON_COLUMNS: Final[tuple[tuple[str, str], ...]] = (
    ("outcomes", "observation_count"),
    ("observations", "result_index"),
    ("observations", "score"),
)
WIDEN_IJSON_COLUMNS_SQL: Final[tuple[str, ...]] = tuple(
    f"ALTER TABLE {table} ALTER COLUMN {column} TYPE BIGINT"
    for table, column in WIDEN_IJSON_COLUMNS
)


class SchemaError(Exception):
    """Rebuildable schema migration refused."""


def _widen_ijson_columns(connection: Connection[Any]) -> tuple[str, ...]:
    """Widen leftover INTEGER I-JSON columns; skip already-BIGINT columns."""

    actions: list[str] = []
    for table, column in WIDEN_IJSON_COLUMNS:
        row = connection.execute(
            """
            SELECT t.typname
            FROM pg_attribute AS a
            JOIN pg_class AS c ON c.oid = a.attrelid
            JOIN pg_namespace AS n ON n.oid = c.relnamespace
            JOIN pg_type AS t ON t.oid = a.atttypid
            WHERE n.nspname = current_schema()
              AND c.relname = %s
              AND a.attname = %s
              AND a.attnum > 0
              AND NOT a.attisdropped
            """,
            (table, column),
        ).fetchone()
        if row is None:
            raise SchemaError(f"{table}.{column} is missing")
        typname = str(row[0])
        if typname == "int8":
            actions.append("skip")
            continue
        if typname != "int4":
            raise SchemaError(f"{table}.{column} has unexpected type {typname}")
        connection.execute(
            sql.SQL("ALTER TABLE {} ALTER COLUMN {} TYPE BIGINT").format(
                sql.Identifier(table), sql.Identifier(column)
            )
        )
        actions.append("alter")
    return tuple(actions)


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
    _widen_ijson_columns(connection)
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
        "google_organic_related_queries google_organic_result_context "
        "google_organic_ranked_results_v2 google_organic_top_story_results "
        "google_organic_top_story_result_occurrences "
        "google_organic_video_results google_organic_video_result_occurrences "
        "google_organic_sitelinks google_organic_sitelink_occurrences\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
