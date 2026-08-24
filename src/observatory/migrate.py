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

SCHEMA_STATEMENTS: Final[tuple[str, ...]] = PRE_AI11_SCHEMA_STATEMENTS + (
    TARGET_METRICS_TOTALS_SQL,
    TARGET_METRICS_SOURCE_DOMAINS_SQL,
    TARGET_METRICS_CONTEXT_SQL,
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
        "google_organic_related_queries google_organic_result_context\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
