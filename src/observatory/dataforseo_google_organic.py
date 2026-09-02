"""DataForSEO Google Organic Live Advanced strict parser and first recipe."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Final
from urllib.parse import urlparse

from observatory.capture_event import ORGANIC_ADAPTER_CONTRACT
from observatory.dataforseo_keyword_overview import (
    Field,
    FieldState,
    ParseClassification,
    ParseDiagnostic,
)
from observatory.provider_recipe import (
    IDENTITY_SCHEMA,
    IDENTITY_VERSION,
    SCHEMA,
    SCHEMA_VERSION,
    recipe_bytes,
    recipe_derivation_version_id,
    validate_recipe,
)

PROVIDER: Final[str] = "dataforseo"
PARSER_CONTRACT: Final[str] = (
    "dataforseo-serp-google-organic-live-advanced-paid-probe-parser-v1"
)
SUCCESS_STATUS: Final[int] = 20000

FEATURE_PRESENCE_KIND: Final[str] = "dataforseo.google.organic.serp_feature_presence.v1"
ORGANIC_PLACEMENT_KIND: Final[str] = "dataforseo.google.organic.ranked_result.v1"
AIO_PRESENCE_KIND: Final[str] = "dataforseo.google.organic.ai_overview_presence.v1"
AIO_SOURCE_KIND: Final[str] = "dataforseo.google.organic.ai_overview_source.v1"
RELATED_QUESTION_KIND: Final[str] = "dataforseo.google.organic.related_question.v1"
RELATED_QUERY_KIND: Final[str] = "dataforseo.google.organic.related_query.v1"

PARSER_CONTRACT_V2: Final[str] = (
    "dataforseo-serp-google-organic-live-advanced-paid-probe-parser-v2"
)

ORGANIC_PLACEMENT_V2_KIND: Final[str] = "dataforseo.google.organic.ranked_result.v2"
TOP_STORY_RESULT_KIND: Final[str] = "dataforseo.google.organic.top_story_result.v1"
VIDEO_RESULT_KIND: Final[str] = "dataforseo.google.organic.video_result.v1"
ORGANIC_SITELINK_KIND: Final[str] = "dataforseo.google.organic.organic_sitelink.v1"

TOP_STORY_ELEMENT_TYPE: Final[str] = "top_stories_element"
VIDEO_ELEMENT_TYPE: Final[str] = "video_element"
LINK_ELEMENT_TYPE: Final[str] = "link_element"

KNOWN_ITEM_TYPES: Final[frozenset[str]] = frozenset(
    {
        "ai_overview",
        "organic",
        "people_also_ask",
        "related_searches",
        "top_stories",
        "video",
    }
)
POSITIONS: Final[frozenset[str]] = frozenset({"left", "right"})
AIO_LOCI: Final[frozenset[str]] = frozenset({"top_level", "element"})

_RESULT_DATETIME_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \+00:00$"
)
_UTC_CLOCK_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \+00:00$"
)

_ROOT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "version",
        "status_code",
        "status_message",
        "time",
        "cost",
        "tasks_count",
        "tasks_error",
        "tasks",
    }
)
_TASK_KEYS: Final[frozenset[str]] = frozenset(
    {
        "id",
        "status_code",
        "status_message",
        "time",
        "cost",
        "result_count",
        "path",
        "data",
        "result",
    }
)
_RESULT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "keyword",
        "type",
        "se_domain",
        "location_code",
        "language_code",
        "check_url",
        "datetime",
        "spell",
        "refinement_chips",
        "item_types",
        "se_results_count",
        "pages_count",
        "items_count",
        "items",
    }
)
_ITEM_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "rank_group",
        "rank_absolute",
        "page",
        "position",
        "xpath",
        "domain",
        "title",
        "url",
        "cache_url",
        "related_search_url",
        "breadcrumb",
        "website_name",
        "is_image",
        "is_video",
        "is_featured_snippet",
        "is_malicious",
        "is_web_story",
        "checks",
        "description",
        "pre_snippet",
        "extended_snippet",
        "images",
        "amp_version",
        "rating",
        "price",
        "highlighted",
        "links",
        "faq",
        "extended_people_also_search",
        "about_this_result",
        "related_result",
        "timestamp",
        "rectangle",
        "asynchronous_ai_overview",
        "markdown",
        "items",
        "references",
    }
)
_AIO_ELEMENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "position",
        "title",
        "text",
        "markdown",
        "links",
        "images",
        "references",
    }
)
_AIO_REFERENCE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "position",
        "source",
        "domain",
        "url",
        "title",
        "text",
    }
)
_PAA_ELEMENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "title",
        "seed_question",
        "xpath",
        "expanded_element",
    }
)
_TOP_STORY_ELEMENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "source",
        "domain",
        "title",
        "url",
        "timestamp",
        "date",
        "image_url",
        "amp_version",
        "badges",
    }
)
_VIDEO_ELEMENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "source",
        "title",
        "url",
        "timestamp",
    }
)
_LINK_ELEMENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "type",
        "title",
        "url",
        "domain",
        "description",
    }
)


class GoogleOrganicParseError(Exception):
    """Strict Google Organic parse or reconciliation failed."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class SerpFeaturePlacement:
    item_type: str
    page: int
    position: str
    rank_group: int
    rank_absolute: int


@dataclass(frozen=True)
class OrganicPlacement:
    url: str
    domain: str
    title: str
    description: Field[str]
    website_name: Field[str]
    page: int
    position: str
    rank_group: int
    rank_absolute: int


@dataclass(frozen=True)
class AiOverviewPresence:
    asynchronous_ai_overview: bool
    page: int
    position: str
    rank_group: int
    rank_absolute: int


@dataclass(frozen=True)
class AiOverviewSource:
    locus: str
    element_index: int | None
    reference_index: int
    url: str
    domain: Field[str]
    title: Field[str]
    source: Field[str]


@dataclass(frozen=True)
class RelatedQuestion:
    question_index: int
    title: str
    page: int
    position: str
    rank_group: int
    rank_absolute: int


@dataclass(frozen=True)
class RelatedQuery:
    query: str


@dataclass(frozen=True)
class OrganicSitelink:
    """One returned `link_element` child of an exact organic ranked placement.

    `child_index` is returned occurrence/order testimony, never rank or identity.
    `url` is exact provider URL testimony, never a canonical Page identity.
    """

    child_index: int
    title: str
    url: str
    domain: str
    description: Field[str]


@dataclass(frozen=True)
class OrganicPlacementV2:
    """Ranked-result v2: the accepted v1 placement plus item-time and links state.

    `organic_item_timestamp` is exact provider-stated structure-local item/result
    timestamp testimony. It is not Capture time, result retrieval `datetime`,
    Provider Update Time, Data Period, or an Observatory-certified publication
    instant, and it never inherits from a sibling clock, `date`, or `pre_snippet`.
    `links_state` records the parent `links` family independently of child rows so
    absent, JSON null, stated-empty, and stated-populated stay distinct.
    """

    url: str
    domain: str
    title: str
    description: Field[str]
    website_name: Field[str]
    page: int
    position: str
    rank_group: int
    rank_absolute: int
    organic_item_timestamp: Field[str]
    links_state: FieldState
    sitelinks: tuple[OrganicSitelink, ...]

    @property
    def links_count(self) -> int | None:
        """Returned sitelink child count, or None when `links` was not stated."""

        if self.links_state is not FieldState.STATED:
            return None
        return len(self.sitelinks)


@dataclass(frozen=True)
class TopStoryChild:
    """One returned `top_stories_element` child.

    `top_story_item_timestamp` is exact provider-stated structure-local item
    timestamp testimony, never a certified publication instant and never derived
    from the sibling relative `date` string.
    """

    child_index: int
    source: str
    domain: str
    title: str
    url: str
    top_story_item_timestamp: Field[str]


@dataclass(frozen=True)
class TopStoryGroup:
    """One returned `top_stories` parent placement and its exact children."""

    page: int
    position: str
    rank_group: int
    rank_absolute: int
    children: tuple[TopStoryChild, ...]


@dataclass(frozen=True)
class VideoChild:
    """One returned `video_element` child.

    PF-10 states no child `domain`; parser-v2 never derives one from the URL.
    `video_item_timestamp` is exact provider-stated structure-local item timestamp
    testimony, never a certified publication instant.
    """

    child_index: int
    source: str
    title: str
    url: str
    video_item_timestamp: Field[str]


@dataclass(frozen=True)
class VideoGroup:
    """One returned `video` parent placement and its exact children."""

    page: int
    position: str
    rank_group: int
    rank_absolute: int
    children: tuple[VideoChild, ...]


@dataclass(frozen=True)
class GoogleOrganicIR:
    outcome: ParseClassification
    requested_keyword: str
    returned_keyword: Field[str]
    location_code: int
    language_code: str
    se_domain: Field[str]
    check_url: Field[str]
    result_datetime: Field[str]
    se_results_count: Field[int]
    pages_count: Field[int]
    items_count: int
    item_types: tuple[str, ...]
    feature_placements: tuple[SerpFeaturePlacement, ...]
    organic_placements: tuple[OrganicPlacement, ...]
    ai_overview: AiOverviewPresence | None
    ai_overview_sources: tuple[AiOverviewSource, ...]
    related_questions: tuple[RelatedQuestion, ...]
    related_queries: tuple[RelatedQuery, ...]
    diagnostics: tuple[ParseDiagnostic, ...]
    status_code: Field[int]
    task_status_code: Field[int]
    cost: Field[Decimal]


@dataclass(frozen=True)
class GoogleOrganicExpandedIR:
    """Parser-v2 intermediate result for the expanded Google Organic Recipe."""

    outcome: ParseClassification
    requested_keyword: str
    returned_keyword: Field[str]
    location_code: int
    language_code: str
    se_domain: Field[str]
    check_url: Field[str]
    result_datetime: Field[str]
    se_results_count: Field[int]
    pages_count: Field[int]
    items_count: int
    item_types: tuple[str, ...]
    feature_placements: tuple[SerpFeaturePlacement, ...]
    organic_placements: tuple[OrganicPlacementV2, ...]
    top_story_groups: tuple[TopStoryGroup, ...]
    video_groups: tuple[VideoGroup, ...]
    ai_overview: AiOverviewPresence | None
    ai_overview_sources: tuple[AiOverviewSource, ...]
    related_questions: tuple[RelatedQuestion, ...]
    related_queries: tuple[RelatedQuery, ...]
    diagnostics: tuple[ParseDiagnostic, ...]
    status_code: Field[int]
    task_status_code: Field[int]
    cost: Field[Decimal]


def normalize_keyword(value: str) -> str:
    """Normalization used only to match requested vs returned keyword."""

    return " ".join(value.casefold().split())


def parse_google_organic(
    body: bytes,
    parameters: Mapping[str, object],
) -> GoogleOrganicIR:
    """Parse exact Google Organic body bytes against verified Attempt parameters."""

    requested = _require_str(parameters.get("keyword"), "/attempt/keyword")
    location = _require_int(parameters.get("location_code"), "/attempt/location_code")
    language = _require_str(parameters.get("language_code"), "/attempt/language_code")
    document = _decode_json(body)
    root = _object(document, "")
    diagnostics: list[ParseDiagnostic] = []
    _collect_unknown(root, _ROOT_KEYS, "", diagnostics)
    status = _require_stated_int(root, "status_code", "/status_code")
    task_list = _require_array(root.get("tasks"), "/tasks")
    tasks_count = _require_stated_int(root, "tasks_count", "/tasks_count")
    if tasks_count.value != len(task_list):
        raise GoogleOrganicParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    _require_stated_int(root, "tasks_error", "/tasks_error")
    if len(task_list) != 1:
        raise GoogleOrganicParseError("tasks_length", "/tasks", "exactly one task is required")
    task = _object(task_list[0], "/tasks/0")
    _collect_unknown(task, _TASK_KEYS, "/tasks/0", diagnostics)
    task_status = _require_stated_int(task, "status_code", "/tasks/0/status_code")
    if status.value == SUCCESS_STATUS and task_status.value != SUCCESS_STATUS:
        return _error_ir(
            requested=requested,
            location=location,
            language=language,
            diagnostics=diagnostics,
            status=status,
            task_status=task_status,
            root=root,
        )
    if status.value != SUCCESS_STATUS and task_status.value == SUCCESS_STATUS:
        raise GoogleOrganicParseError(
            "inconsistent_status",
            "/status_code",
            "top-level and task status are inconsistent",
        )
    if status.value != SUCCESS_STATUS:
        return _error_ir(
            requested=requested,
            location=location,
            language=language,
            diagnostics=diagnostics,
            status=status,
            task_status=task_status,
            root=root,
        )
    result_list = _require_array(task.get("result"), "/tasks/0/result")
    result_count = _require_stated_int(task, "result_count", "/tasks/0/result_count")
    if result_count.value != len(result_list):
        raise GoogleOrganicParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise GoogleOrganicParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    result = _object(result_list[0], "/tasks/0/result/0")
    _collect_unknown(result, _RESULT_KEYS, "/tasks/0/result/0", diagnostics)
    returned_keyword = _optional_str(result, "keyword", "/tasks/0/result/0/keyword")
    _reconcile_keyword(requested, returned_keyword)
    _reconcile_attempt_context(result, location, language)
    if result.get("type") != "organic":
        raise GoogleOrganicParseError(
            "unknown_enum", "/tasks/0/result/0/type", "result type must be organic"
        )
    items_value = result.get("items")
    if "items" not in result:
        raise GoogleOrganicParseError(
            "missing_field", "/tasks/0/result/0/items", "items missing"
        )
    if items_value is None:
        raise GoogleOrganicParseError(
            "wrong_type", "/tasks/0/result/0/items", "items must not be JSON null"
        )
    items_list = _require_array(items_value, "/tasks/0/result/0/items")
    items_count = _require_stated_int(result, "items_count", "/tasks/0/result/0/items_count")
    if items_count.value != len(items_list):
        raise GoogleOrganicParseError(
            "count_mismatch",
            "/tasks/0/result/0/items_count",
            "items_count does not match items length",
        )
    item_types = _parse_item_types(result.get("item_types"), "/tasks/0/result/0/item_types")
    parsed_items = [
        _parse_top_item(item, f"/tasks/0/result/0/items/{index}", diagnostics)
        for index, item in enumerate(items_list)
    ]
    _require_unique_placements(parsed_items)
    feature_placements = tuple(
        SerpFeaturePlacement(
            item_type=item.item_type,
            page=item.page,
            position=item.position,
            rank_group=item.rank_group,
            rank_absolute=item.rank_absolute,
        )
        for item in parsed_items
    )
    organic_placements = tuple(
        item.organic for item in parsed_items if item.organic is not None
    )
    aio_items = [item for item in parsed_items if item.ai_overview is not None]
    if len(aio_items) > 1:
        raise GoogleOrganicParseError(
            "duplicate_ai_overview",
            "/tasks/0/result/0/items",
            "more than one ai_overview item is not admitted",
        )
    ai_overview = aio_items[0].ai_overview if aio_items else None
    ai_overview_sources = tuple(
        source for item in parsed_items for source in item.ai_overview_sources
    )
    related_questions = tuple(
        question for item in parsed_items for question in item.related_questions
    )
    related_queries = _dedupe_related_queries(
        [query for item in parsed_items for query in item.related_queries]
    )
    return GoogleOrganicIR(
        outcome=ParseClassification.ADMITTED,
        requested_keyword=requested,
        returned_keyword=returned_keyword,
        location_code=location,
        language_code=language,
        se_domain=_optional_str(result, "se_domain", "/tasks/0/result/0/se_domain"),
        check_url=_optional_url(result, "check_url", "/tasks/0/result/0/check_url"),
        result_datetime=_optional_result_datetime(
            result, "datetime", "/tasks/0/result/0/datetime"
        ),
        se_results_count=_optional_int(
            result, "se_results_count", "/tasks/0/result/0/se_results_count"
        ),
        pages_count=_optional_int(result, "pages_count", "/tasks/0/result/0/pages_count"),
        items_count=items_count.value or 0,
        item_types=item_types,
        feature_placements=feature_placements,
        organic_placements=organic_placements,
        ai_overview=ai_overview,
        ai_overview_sources=ai_overview_sources,
        related_questions=related_questions,
        related_queries=related_queries,
        diagnostics=tuple(diagnostics),
        status_code=status,
        task_status_code=task_status,
        cost=_optional_decimal(root, "cost", "/cost"),
    )


def parse_google_organic_v2(
    body: bytes,
    parameters: Mapping[str, object],
) -> GoogleOrganicExpandedIR:
    """Parse exact Google Organic body bytes under parser contract v2.

    Parser-v2 keeps every accepted v1 envelope, reconciliation, feature, AI
    Overview, PAA, and related-query rule and additionally walks the Top Stories,
    Video, and organic `links` child structures strictly. It is deliberately a
    local duplicate of the v1 envelope walk: the two parser contracts are separate
    frozen versions and v1 must not change behind its own contract.
    """

    requested = _require_str(parameters.get("keyword"), "/attempt/keyword")
    location = _require_int(parameters.get("location_code"), "/attempt/location_code")
    language = _require_str(parameters.get("language_code"), "/attempt/language_code")
    document = _decode_json(body)
    root = _object(document, "")
    diagnostics: list[ParseDiagnostic] = []
    _collect_unknown(root, _ROOT_KEYS, "", diagnostics)
    status = _require_stated_int(root, "status_code", "/status_code")
    task_list = _require_array(root.get("tasks"), "/tasks")
    tasks_count = _require_stated_int(root, "tasks_count", "/tasks_count")
    if tasks_count.value != len(task_list):
        raise GoogleOrganicParseError(
            "count_mismatch", "/tasks_count", "tasks_count does not match tasks length"
        )
    _require_stated_int(root, "tasks_error", "/tasks_error")
    if len(task_list) != 1:
        raise GoogleOrganicParseError("tasks_length", "/tasks", "exactly one task is required")
    task = _object(task_list[0], "/tasks/0")
    _collect_unknown(task, _TASK_KEYS, "/tasks/0", diagnostics)
    task_status = _require_stated_int(task, "status_code", "/tasks/0/status_code")
    if status.value == SUCCESS_STATUS and task_status.value != SUCCESS_STATUS:
        return _expanded_error_ir(
            requested=requested,
            location=location,
            language=language,
            diagnostics=diagnostics,
            status=status,
            task_status=task_status,
            root=root,
        )
    if status.value != SUCCESS_STATUS and task_status.value == SUCCESS_STATUS:
        raise GoogleOrganicParseError(
            "inconsistent_status",
            "/status_code",
            "top-level and task status are inconsistent",
        )
    if status.value != SUCCESS_STATUS:
        return _expanded_error_ir(
            requested=requested,
            location=location,
            language=language,
            diagnostics=diagnostics,
            status=status,
            task_status=task_status,
            root=root,
        )
    result_list = _require_array(task.get("result"), "/tasks/0/result")
    result_count = _require_stated_int(task, "result_count", "/tasks/0/result_count")
    if result_count.value != len(result_list):
        raise GoogleOrganicParseError(
            "count_mismatch",
            "/tasks/0/result_count",
            "result_count does not match result length",
        )
    if len(result_list) != 1:
        raise GoogleOrganicParseError(
            "result_length", "/tasks/0/result", "exactly one result is required"
        )
    result = _object(result_list[0], "/tasks/0/result/0")
    _collect_unknown(result, _RESULT_KEYS, "/tasks/0/result/0", diagnostics)
    returned_keyword = _optional_str(result, "keyword", "/tasks/0/result/0/keyword")
    _reconcile_keyword(requested, returned_keyword)
    _reconcile_attempt_context(result, location, language)
    if result.get("type") != "organic":
        raise GoogleOrganicParseError(
            "unknown_enum", "/tasks/0/result/0/type", "result type must be organic"
        )
    items_value = result.get("items")
    if "items" not in result:
        raise GoogleOrganicParseError(
            "missing_field", "/tasks/0/result/0/items", "items missing"
        )
    if items_value is None:
        raise GoogleOrganicParseError(
            "wrong_type", "/tasks/0/result/0/items", "items must not be JSON null"
        )
    items_list = _require_array(items_value, "/tasks/0/result/0/items")
    items_count = _require_stated_int(result, "items_count", "/tasks/0/result/0/items_count")
    if items_count.value != len(items_list):
        raise GoogleOrganicParseError(
            "count_mismatch",
            "/tasks/0/result/0/items_count",
            "items_count does not match items length",
        )
    item_types = _parse_item_types(result.get("item_types"), "/tasks/0/result/0/item_types")
    parsed_items = [
        _parse_top_item_v2(item, f"/tasks/0/result/0/items/{index}", diagnostics)
        for index, item in enumerate(items_list)
    ]
    _require_unique_placements_v2(parsed_items)
    feature_placements = tuple(
        SerpFeaturePlacement(
            item_type=item.item_type,
            page=item.page,
            position=item.position,
            rank_group=item.rank_group,
            rank_absolute=item.rank_absolute,
        )
        for item in parsed_items
    )
    organic_placements = tuple(
        item.organic for item in parsed_items if item.organic is not None
    )
    top_story_groups = tuple(
        item.top_story_group for item in parsed_items if item.top_story_group is not None
    )
    video_groups = tuple(
        item.video_group for item in parsed_items if item.video_group is not None
    )
    aio_items = [item for item in parsed_items if item.ai_overview is not None]
    if len(aio_items) > 1:
        raise GoogleOrganicParseError(
            "duplicate_ai_overview",
            "/tasks/0/result/0/items",
            "more than one ai_overview item is not admitted",
        )
    ai_overview = aio_items[0].ai_overview if aio_items else None
    ai_overview_sources = tuple(
        source for item in parsed_items for source in item.ai_overview_sources
    )
    related_questions = tuple(
        question for item in parsed_items for question in item.related_questions
    )
    related_queries = _dedupe_related_queries(
        [query for item in parsed_items for query in item.related_queries]
    )
    return GoogleOrganicExpandedIR(
        outcome=ParseClassification.ADMITTED,
        requested_keyword=requested,
        returned_keyword=returned_keyword,
        location_code=location,
        language_code=language,
        se_domain=_optional_str(result, "se_domain", "/tasks/0/result/0/se_domain"),
        check_url=_optional_url(result, "check_url", "/tasks/0/result/0/check_url"),
        result_datetime=_optional_result_datetime(
            result, "datetime", "/tasks/0/result/0/datetime"
        ),
        se_results_count=_optional_int(
            result, "se_results_count", "/tasks/0/result/0/se_results_count"
        ),
        pages_count=_optional_int(result, "pages_count", "/tasks/0/result/0/pages_count"),
        items_count=items_count.value or 0,
        item_types=item_types,
        feature_placements=feature_placements,
        organic_placements=organic_placements,
        top_story_groups=top_story_groups,
        video_groups=video_groups,
        ai_overview=ai_overview,
        ai_overview_sources=ai_overview_sources,
        related_questions=related_questions,
        related_queries=related_queries,
        diagnostics=tuple(diagnostics),
        status_code=status,
        task_status_code=task_status,
        cost=_optional_decimal(root, "cost", "/cost"),
    )


def google_organic_recipe() -> dict[str, object]:
    """Return the first Google Organic Derivation Recipe document."""

    kinds = [
        {
            "axes": {
                "item_type": "string",
                "page": "integer",
                "position": "string",
                "rank_absolute": "integer",
                "rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": FEATURE_PRESENCE_KIND,
        },
        {
            "axes": {
                "page": "integer",
                "position": "string",
                "rank_absolute": "integer",
                "rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": ORGANIC_PLACEMENT_KIND,
        },
        {
            "axes": {"requested_keyword": "string"},
            "observation_kind": AIO_PRESENCE_KIND,
        },
        {
            "axes": {
                "locus": "string",
                "requested_keyword": "string",
                "url": "string",
            },
            "observation_kind": AIO_SOURCE_KIND,
        },
        {
            "axes": {
                "requested_keyword": "string",
                "title": "string",
            },
            "observation_kind": RELATED_QUESTION_KIND,
        },
        {
            "axes": {
                "query": "string",
                "requested_keyword": "string",
            },
            "observation_kind": RELATED_QUERY_KIND,
        },
    ]
    return validate_recipe(
        {
            "adapter_contract": ORGANIC_ADAPTER_CONTRACT,
            "admission": {
                "capture_outcomes": [
                    "no_response",
                    "observation_admitted",
                    "observation_admitted_empty",
                    "provider_envelope_rejected",
                    "provider_error",
                    "reconciliation_failed",
                    "response_partial",
                    "transport_complete_non_admissible",
                ],
                "rule": "recipe_closed_classifications",
            },
            "data_period": {
                "inheritance": "never_from_capture",
                "rule": "provider_stated_or_unstated",
            },
            "extension_policy": {
                "closed_objects": [],
                "extension_permitted_objects": [
                    "/",
                    "/ai_overview_element",
                    "/ai_overview_reference",
                    "/items",
                    "/people_also_ask_element",
                    "/result",
                    "/tasks",
                ],
                "unknown_closed_field": "fail_closed",
                "unknown_extension_field": "diagnostic",
            },
            "field_state": {
                "states": [
                    "absent",
                    "inapplicable",
                    "json_null",
                    "not_requested",
                    "stated",
                ]
            },
            "numeric": {"normalization": "exact_decimal"},
            "observation_identity": {
                "document_schema": IDENTITY_SCHEMA,
                "document_version": IDENTITY_VERSION,
                "kinds": kinds,
            },
            "observation_kinds": [
                FEATURE_PRESENCE_KIND,
                ORGANIC_PLACEMENT_KIND,
                AIO_PRESENCE_KIND,
                AIO_SOURCE_KIND,
                RELATED_QUESTION_KIND,
                RELATED_QUERY_KIND,
            ],
            "parser_contract": PARSER_CONTRACT,
            "provider": PROVIDER,
            "provider_update_time": {
                "inheritance": "never_from_capture_or_sibling",
                "rule": "structure_stated_or_unstated",
            },
            "reconciliation": {"rule": "exact_requested_subject_normalized"},
            "schema": SCHEMA,
            "version": SCHEMA_VERSION,
        }
    )


def google_organic_expanded_recipe() -> dict[str, object]:
    """Return the PF-18 expanded Google Organic Derivation Recipe document.

    The expanded Recipe is a separate content-addressed identity under parser
    contract v2. It keeps every accepted v1 semantic kind unchanged, replaces
    ranked-result v1 with ranked-result v2 inside this Recipe only, and adds the
    three MVP child kinds. Registering or deriving it never changes the operator
    Recipe selection.
    """

    kinds = [
        {
            "axes": {
                "item_type": "string",
                "page": "integer",
                "position": "string",
                "rank_absolute": "integer",
                "rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": FEATURE_PRESENCE_KIND,
        },
        {
            "axes": {
                "page": "integer",
                "position": "string",
                "rank_absolute": "integer",
                "rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": ORGANIC_PLACEMENT_V2_KIND,
        },
        {
            "axes": {"requested_keyword": "string"},
            "observation_kind": AIO_PRESENCE_KIND,
        },
        {
            "axes": {
                "locus": "string",
                "requested_keyword": "string",
                "url": "string",
            },
            "observation_kind": AIO_SOURCE_KIND,
        },
        {
            "axes": {
                "requested_keyword": "string",
                "title": "string",
            },
            "observation_kind": RELATED_QUESTION_KIND,
        },
        {
            "axes": {
                "query": "string",
                "requested_keyword": "string",
            },
            "observation_kind": RELATED_QUERY_KIND,
        },
        {
            "axes": {
                "child_url": "string",
                "parent_page": "integer",
                "parent_position": "string",
                "parent_rank_absolute": "integer",
                "parent_rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": TOP_STORY_RESULT_KIND,
        },
        {
            "axes": {
                "child_url": "string",
                "parent_page": "integer",
                "parent_position": "string",
                "parent_rank_absolute": "integer",
                "parent_rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": VIDEO_RESULT_KIND,
        },
        {
            "axes": {
                "child_url": "string",
                "parent_page": "integer",
                "parent_position": "string",
                "parent_rank_absolute": "integer",
                "parent_rank_group": "integer",
                "requested_keyword": "string",
            },
            "observation_kind": ORGANIC_SITELINK_KIND,
        },
    ]
    return validate_recipe(
        {
            "adapter_contract": ORGANIC_ADAPTER_CONTRACT,
            "admission": {
                "capture_outcomes": [
                    "no_response",
                    "observation_admitted",
                    "observation_admitted_empty",
                    "provider_envelope_rejected",
                    "provider_error",
                    "reconciliation_failed",
                    "response_partial",
                    "transport_complete_non_admissible",
                ],
                "rule": "recipe_closed_classifications",
            },
            "data_period": {
                "inheritance": "never_from_capture",
                "rule": "provider_stated_or_unstated",
            },
            "extension_policy": {
                "closed_objects": [],
                "extension_permitted_objects": [
                    "/",
                    "/ai_overview_element",
                    "/ai_overview_reference",
                    "/items",
                    "/link_element",
                    "/people_also_ask_element",
                    "/result",
                    "/tasks",
                    "/top_stories_element",
                    "/video_element",
                ],
                "unknown_closed_field": "fail_closed",
                "unknown_extension_field": "diagnostic",
            },
            "field_state": {
                "states": [
                    "absent",
                    "inapplicable",
                    "json_null",
                    "not_requested",
                    "stated",
                ]
            },
            "numeric": {"normalization": "exact_decimal"},
            "observation_identity": {
                "document_schema": IDENTITY_SCHEMA,
                "document_version": IDENTITY_VERSION,
                "kinds": kinds,
            },
            "observation_kinds": [
                FEATURE_PRESENCE_KIND,
                ORGANIC_PLACEMENT_V2_KIND,
                AIO_PRESENCE_KIND,
                AIO_SOURCE_KIND,
                RELATED_QUESTION_KIND,
                RELATED_QUERY_KIND,
                TOP_STORY_RESULT_KIND,
                VIDEO_RESULT_KIND,
                ORGANIC_SITELINK_KIND,
            ],
            "parser_contract": PARSER_CONTRACT_V2,
            "provider": PROVIDER,
            "provider_update_time": {
                "inheritance": "never_from_capture_or_sibling",
                "rule": "structure_stated_or_unstated",
            },
            "reconciliation": {"rule": "exact_requested_subject_normalized"},
            "schema": SCHEMA,
            "version": SCHEMA_VERSION,
        }
    )


GOOGLE_ORGANIC_RECIPE: Final[dict[str, object]] = google_organic_recipe()
GOOGLE_ORGANIC_RECIPE_BYTES: Final[bytes] = recipe_bytes(GOOGLE_ORGANIC_RECIPE)
GOOGLE_ORGANIC_RECIPE_ID: Final[str] = recipe_derivation_version_id(GOOGLE_ORGANIC_RECIPE)
GOOGLE_ORGANIC_EXPANDED_RECIPE: Final[dict[str, object]] = (
    google_organic_expanded_recipe()
)
GOOGLE_ORGANIC_EXPANDED_RECIPE_BYTES: Final[bytes] = recipe_bytes(
    GOOGLE_ORGANIC_EXPANDED_RECIPE
)
GOOGLE_ORGANIC_EXPANDED_RECIPE_ID: Final[str] = recipe_derivation_version_id(
    GOOGLE_ORGANIC_EXPANDED_RECIPE
)


@dataclass(frozen=True)
class _ParsedTopItem:
    item_type: str
    page: int
    position: str
    rank_group: int
    rank_absolute: int
    organic: OrganicPlacement | None
    ai_overview: AiOverviewPresence | None
    ai_overview_sources: tuple[AiOverviewSource, ...]
    related_questions: tuple[RelatedQuestion, ...]
    related_queries: tuple[str, ...]


@dataclass(frozen=True)
class _ParsedTopItemV2:
    item_type: str
    page: int
    position: str
    rank_group: int
    rank_absolute: int
    organic: OrganicPlacementV2 | None
    top_story_group: TopStoryGroup | None
    video_group: VideoGroup | None
    ai_overview: AiOverviewPresence | None
    ai_overview_sources: tuple[AiOverviewSource, ...]
    related_questions: tuple[RelatedQuestion, ...]
    related_queries: tuple[str, ...]


def _expanded_error_ir(
    *,
    requested: str,
    location: int,
    language: str,
    diagnostics: list[ParseDiagnostic],
    status: Field[int],
    task_status: Field[int],
    root: Mapping[str, object],
) -> GoogleOrganicExpandedIR:
    return GoogleOrganicExpandedIR(
        outcome=ParseClassification.PROVIDER_ERROR,
        requested_keyword=requested,
        returned_keyword=Field[str].absent(),
        location_code=location,
        language_code=language,
        se_domain=Field[str].absent(),
        check_url=Field[str].absent(),
        result_datetime=Field[str].absent(),
        se_results_count=Field[int].absent(),
        pages_count=Field[int].absent(),
        items_count=0,
        item_types=(),
        feature_placements=(),
        organic_placements=(),
        top_story_groups=(),
        video_groups=(),
        ai_overview=None,
        ai_overview_sources=(),
        related_questions=(),
        related_queries=(),
        diagnostics=tuple(diagnostics),
        status_code=status,
        task_status_code=task_status,
        cost=_optional_decimal(root, "cost", "/cost"),
    )


def _parse_top_item_v2(
    value: object,
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> _ParsedTopItemV2:
    item = _object(value, path)
    _collect_unknown(item, _ITEM_KEYS, path, diagnostics)
    _reject_related_result_drift(item, path)
    item_type = _require_str(item.get("type"), f"{path}/type")
    if item_type not in KNOWN_ITEM_TYPES:
        raise GoogleOrganicParseError(
            "unknown_enum", f"{path}/type", "item type is not in the closed set"
        )
    page = _require_int(item.get("page"), f"{path}/page")
    position = _require_str(item.get("position"), f"{path}/position")
    if position not in POSITIONS:
        raise GoogleOrganicParseError(
            "unknown_enum", f"{path}/position", "position must be left or right"
        )
    rank_group = _require_int(item.get("rank_group"), f"{path}/rank_group")
    rank_absolute = _require_int(item.get("rank_absolute"), f"{path}/rank_absolute")
    if page < 1 or rank_group < 1 or rank_absolute < 1:
        raise GoogleOrganicParseError(
            "invalid_rank", path, "page and rank axes must be positive"
        )
    organic: OrganicPlacementV2 | None = None
    top_story_group: TopStoryGroup | None = None
    video_group: VideoGroup | None = None
    ai_overview: AiOverviewPresence | None = None
    sources: tuple[AiOverviewSource, ...] = ()
    questions: tuple[RelatedQuestion, ...] = ()
    queries: tuple[str, ...] = ()
    if item_type == "organic":
        links_state, sitelinks = _parse_organic_links(item, path, diagnostics)
        organic = OrganicPlacementV2(
            url=_require_http_url(item.get("url"), f"{path}/url"),
            domain=_require_str(item.get("domain"), f"{path}/domain"),
            title=_require_str(item.get("title"), f"{path}/title"),
            description=_optional_str(item, "description", f"{path}/description"),
            website_name=_optional_str(item, "website_name", f"{path}/website_name"),
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
            organic_item_timestamp=_optional_organic_item_timestamp(
                item, "timestamp", f"{path}/timestamp"
            ),
            links_state=links_state,
            sitelinks=sitelinks,
        )
    elif item_type == "top_stories":
        top_story_group = TopStoryGroup(
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
            children=_parse_top_story_children(item, path, diagnostics),
        )
    elif item_type == "video":
        video_group = VideoGroup(
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
            children=_parse_video_children(item, path, diagnostics),
        )
    elif item_type == "ai_overview":
        async_flag = _require_bool(
            item.get("asynchronous_ai_overview"),
            f"{path}/asynchronous_ai_overview",
        )
        ai_overview = AiOverviewPresence(
            asynchronous_ai_overview=async_flag,
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
        )
        sources = _parse_ai_overview_sources(item, path, diagnostics)
    elif item_type == "people_also_ask":
        questions = _parse_paa_questions(
            item.get("items"),
            f"{path}/items",
            diagnostics,
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
        )
    elif item_type == "related_searches":
        queries = _parse_related_search_strings(item.get("items"), f"{path}/items")
    return _ParsedTopItemV2(
        item_type=item_type,
        page=page,
        position=position,
        rank_group=rank_group,
        rank_absolute=rank_absolute,
        organic=organic,
        top_story_group=top_story_group,
        video_group=video_group,
        ai_overview=ai_overview,
        ai_overview_sources=sources,
        related_questions=questions,
        related_queries=queries,
    )


def _reject_related_result_drift(item: Mapping[str, object], path: str) -> None:
    """`related_result` is deliberately outside PF-18; a populated one fails closed."""

    if "related_result" not in item:
        return
    if item["related_result"] is None:
        return
    raise GoogleOrganicParseError(
        "parser_version_drift",
        f"{path}/related_result",
        "populated related_result is not typed by parser-v2",
    )


def _parse_top_story_children(
    item: Mapping[str, object],
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> tuple[TopStoryChild, ...]:
    raw = _require_child_array(item, path, "top_stories")
    children: list[TopStoryChild] = []
    for index, element in enumerate(raw):
        child_path = f"{path}/items/{index}"
        obj = _object(element, child_path)
        _collect_unknown(obj, _TOP_STORY_ELEMENT_KEYS, child_path, diagnostics)
        child_type = _require_str(obj.get("type"), f"{child_path}/type")
        if child_type != TOP_STORY_ELEMENT_TYPE:
            raise GoogleOrganicParseError(
                "unknown_enum",
                f"{child_path}/type",
                "top stories child must be top_stories_element",
            )
        children.append(
            TopStoryChild(
                child_index=index,
                source=_require_str(obj.get("source"), f"{child_path}/source"),
                domain=_require_str(obj.get("domain"), f"{child_path}/domain"),
                title=_require_str(obj.get("title"), f"{child_path}/title"),
                url=_require_http_url(obj.get("url"), f"{child_path}/url"),
                top_story_item_timestamp=_optional_top_story_item_timestamp(
                    obj, "timestamp", f"{child_path}/timestamp"
                ),
            )
        )
    _require_agreeing_children(
        [(child.url, _top_story_testimony(child)) for child in children],
        f"{path}/items",
        "top stories",
    )
    return tuple(children)


def _parse_video_children(
    item: Mapping[str, object],
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> tuple[VideoChild, ...]:
    raw = _require_child_array(item, path, "video")
    children: list[VideoChild] = []
    for index, element in enumerate(raw):
        child_path = f"{path}/items/{index}"
        obj = _object(element, child_path)
        _collect_unknown(obj, _VIDEO_ELEMENT_KEYS, child_path, diagnostics)
        child_type = _require_str(obj.get("type"), f"{child_path}/type")
        if child_type != VIDEO_ELEMENT_TYPE:
            raise GoogleOrganicParseError(
                "unknown_enum",
                f"{child_path}/type",
                "video child must be video_element",
            )
        children.append(
            VideoChild(
                child_index=index,
                source=_require_str(obj.get("source"), f"{child_path}/source"),
                title=_require_str(obj.get("title"), f"{child_path}/title"),
                url=_require_http_url(obj.get("url"), f"{child_path}/url"),
                video_item_timestamp=_optional_video_item_timestamp(
                    obj, "timestamp", f"{child_path}/timestamp"
                ),
            )
        )
    _require_agreeing_children(
        [(child.url, _video_testimony(child)) for child in children],
        f"{path}/items",
        "video",
    )
    return tuple(children)


def _parse_organic_links(
    item: Mapping[str, object],
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> tuple[FieldState, tuple[OrganicSitelink, ...]]:
    """Return the parent `links` family state and every stated sitelink child.

    Absent, JSON null, stated-empty, and stated-populated stay distinct: the state
    is the parent testimony and the child rows are separate occurrence testimony.
    """

    links_path = f"{path}/links"
    if "links" not in item:
        return FieldState.ABSENT, ()
    value = item["links"]
    if value is None:
        return FieldState.JSON_NULL, ()
    raw = _require_array(value, links_path)
    children: list[OrganicSitelink] = []
    for index, element in enumerate(raw):
        child_path = f"{links_path}/{index}"
        obj = _object(element, child_path)
        _collect_unknown(obj, _LINK_ELEMENT_KEYS, child_path, diagnostics)
        child_type = _require_str(obj.get("type"), f"{child_path}/type")
        if child_type != LINK_ELEMENT_TYPE:
            raise GoogleOrganicParseError(
                "unknown_enum",
                f"{child_path}/type",
                "organic links child must be link_element",
            )
        children.append(
            OrganicSitelink(
                child_index=index,
                title=_require_str(obj.get("title"), f"{child_path}/title"),
                url=_require_http_url(obj.get("url"), f"{child_path}/url"),
                domain=_require_str(obj.get("domain"), f"{child_path}/domain"),
                description=_optional_str(
                    obj, "description", f"{child_path}/description"
                ),
            )
        )
    _require_agreeing_children(
        [(child.url, _sitelink_testimony(child)) for child in children],
        links_path,
        "organic links",
    )
    return FieldState.STATED, tuple(children)


def _require_child_array(
    item: Mapping[str, object], path: str, subject: str
) -> list[object]:
    if "items" not in item:
        raise GoogleOrganicParseError(
            "missing_field", f"{path}/items", f"{subject} child items missing"
        )
    value = item["items"]
    if value is None:
        raise GoogleOrganicParseError(
            "wrong_type", f"{path}/items", f"{subject} child items must not be JSON null"
        )
    return _require_array(value, f"{path}/items")


def _top_story_testimony(child: TopStoryChild) -> tuple[object, ...]:
    return (
        child.source,
        child.domain,
        child.title,
        child.top_story_item_timestamp.state,
        child.top_story_item_timestamp.value,
    )


def _video_testimony(child: VideoChild) -> tuple[object, ...]:
    return (
        child.source,
        child.title,
        child.video_item_timestamp.state,
        child.video_item_timestamp.value,
    )


def _sitelink_testimony(child: OrganicSitelink) -> tuple[object, ...]:
    return (
        child.title,
        child.domain,
        child.description.state,
        child.description.value,
    )


def _require_agreeing_children(
    rows: list[tuple[str, tuple[object, ...]]],
    path: str,
    subject: str,
) -> None:
    """Repeated child URLs under one parent must carry identical testimony.

    Agreeing repeats stay one semantic fact with several occurrences. Conflicting
    repeats are provider drift and fail closed for the whole Capture.
    """

    seen: dict[str, tuple[object, ...]] = {}
    for url, testimony in rows:
        stored = seen.get(url)
        if stored is None:
            seen[url] = testimony
            continue
        if stored != testimony:
            raise GoogleOrganicParseError(
                "duplicate_child_disagreement",
                path,
                f"{subject} repeats one child URL with conflicting testimony",
            )


def _require_unique_placements_v2(items: list[_ParsedTopItemV2]) -> None:
    absolute: set[tuple[str, int]] = set()
    grouped: set[tuple[str, str, int]] = set()
    for item in items:
        abs_key = (item.position, item.rank_absolute)
        if abs_key in absolute:
            raise GoogleOrganicParseError(
                "duplicate_rank",
                "/tasks/0/result/0/items",
                "duplicate rank_absolute in the same position sequence",
            )
        absolute.add(abs_key)
        group_key = (item.item_type, item.position, item.rank_group)
        if group_key in grouped:
            raise GoogleOrganicParseError(
                "duplicate_rank",
                "/tasks/0/result/0/items",
                "duplicate rank_group for the same item type and position",
            )
        grouped.add(group_key)


def _error_ir(
    *,
    requested: str,
    location: int,
    language: str,
    diagnostics: list[ParseDiagnostic],
    status: Field[int],
    task_status: Field[int],
    root: Mapping[str, object],
) -> GoogleOrganicIR:
    return GoogleOrganicIR(
        outcome=ParseClassification.PROVIDER_ERROR,
        requested_keyword=requested,
        returned_keyword=Field[str].absent(),
        location_code=location,
        language_code=language,
        se_domain=Field[str].absent(),
        check_url=Field[str].absent(),
        result_datetime=Field[str].absent(),
        se_results_count=Field[int].absent(),
        pages_count=Field[int].absent(),
        items_count=0,
        item_types=(),
        feature_placements=(),
        organic_placements=(),
        ai_overview=None,
        ai_overview_sources=(),
        related_questions=(),
        related_queries=(),
        diagnostics=tuple(diagnostics),
        status_code=status,
        task_status_code=task_status,
        cost=_optional_decimal(root, "cost", "/cost"),
    )


def _reconcile_keyword(requested: str, returned: Field[str]) -> None:
    if returned.state is not FieldState.STATED or returned.value is None:
        raise GoogleOrganicParseError(
            "reconciliation_failed",
            "/tasks/0/result/0/keyword",
            "returned keyword is missing",
        )
    if normalize_keyword(requested) != normalize_keyword(returned.value):
        raise GoogleOrganicParseError(
            "reconciliation_failed",
            "/tasks/0/result/0/keyword",
            "returned keyword does not match requested subject",
        )


def _reconcile_attempt_context(
    result: Mapping[str, object], location: int, language: str
) -> None:
    returned_location = _optional_int(
        result, "location_code", "/tasks/0/result/0/location_code"
    )
    if (
        returned_location.state is FieldState.STATED
        and returned_location.value != location
    ):
        raise GoogleOrganicParseError(
            "reconciliation_failed",
            "/tasks/0/result/0/location_code",
            "returned location_code does not match the Attempt",
        )
    returned_language = _optional_str(
        result, "language_code", "/tasks/0/result/0/language_code"
    )
    if (
        returned_language.state is FieldState.STATED
        and returned_language.value != language
    ):
        raise GoogleOrganicParseError(
            "reconciliation_failed",
            "/tasks/0/result/0/language_code",
            "returned language_code does not match the Attempt",
        )


def _parse_item_types(value: object, path: str) -> tuple[str, ...]:
    raw = _require_array(value, path)
    types: list[str] = []
    for index, item in enumerate(raw):
        text = _require_str(item, f"{path}/{index}")
        if text not in KNOWN_ITEM_TYPES:
            raise GoogleOrganicParseError(
                "unknown_enum", f"{path}/{index}", "item type is not in the closed set"
            )
        types.append(text)
    return tuple(types)


def _parse_top_item(
    value: object,
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> _ParsedTopItem:
    item = _object(value, path)
    _collect_unknown(item, _ITEM_KEYS, path, diagnostics)
    item_type = _require_str(item.get("type"), f"{path}/type")
    if item_type not in KNOWN_ITEM_TYPES:
        raise GoogleOrganicParseError(
            "unknown_enum", f"{path}/type", "item type is not in the closed set"
        )
    page = _require_int(item.get("page"), f"{path}/page")
    position = _require_str(item.get("position"), f"{path}/position")
    if position not in POSITIONS:
        raise GoogleOrganicParseError(
            "unknown_enum", f"{path}/position", "position must be left or right"
        )
    rank_group = _require_int(item.get("rank_group"), f"{path}/rank_group")
    rank_absolute = _require_int(item.get("rank_absolute"), f"{path}/rank_absolute")
    if page < 1 or rank_group < 1 or rank_absolute < 1:
        raise GoogleOrganicParseError(
            "invalid_rank", path, "page and rank axes must be positive"
        )
    organic: OrganicPlacement | None = None
    ai_overview: AiOverviewPresence | None = None
    sources: tuple[AiOverviewSource, ...] = ()
    questions: tuple[RelatedQuestion, ...] = ()
    queries: tuple[str, ...] = ()
    if item_type == "organic":
        organic = OrganicPlacement(
            url=_require_http_url(item.get("url"), f"{path}/url"),
            domain=_require_str(item.get("domain"), f"{path}/domain"),
            title=_require_str(item.get("title"), f"{path}/title"),
            description=_optional_str(item, "description", f"{path}/description"),
            website_name=_optional_str(item, "website_name", f"{path}/website_name"),
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
        )
    elif item_type == "ai_overview":
        async_flag = _require_bool(
            item.get("asynchronous_ai_overview"),
            f"{path}/asynchronous_ai_overview",
        )
        ai_overview = AiOverviewPresence(
            asynchronous_ai_overview=async_flag,
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
        )
        sources = _parse_ai_overview_sources(item, path, diagnostics)
    elif item_type == "people_also_ask":
        questions = _parse_paa_questions(
            item.get("items"),
            f"{path}/items",
            diagnostics,
            page=page,
            position=position,
            rank_group=rank_group,
            rank_absolute=rank_absolute,
        )
    elif item_type == "related_searches":
        queries = _parse_related_search_strings(item.get("items"), f"{path}/items")
    return _ParsedTopItem(
        item_type=item_type,
        page=page,
        position=position,
        rank_group=rank_group,
        rank_absolute=rank_absolute,
        organic=organic,
        ai_overview=ai_overview,
        ai_overview_sources=sources,
        related_questions=questions,
        related_queries=queries,
    )


def _parse_ai_overview_sources(
    item: Mapping[str, object],
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> tuple[AiOverviewSource, ...]:
    sources: list[AiOverviewSource] = []
    if "references" not in item:
        raise GoogleOrganicParseError(
            "missing_field", f"{path}/references", "top-level AIO references missing"
        )
    refs = _require_array(item.get("references"), f"{path}/references")
    for index, raw in enumerate(refs):
        sources.append(
            _parse_aio_reference(
                raw,
                f"{path}/references/{index}",
                locus="top_level",
                element_index=None,
                reference_index=index,
                diagnostics=diagnostics,
            )
        )
    if "items" not in item:
        raise GoogleOrganicParseError(
            "missing_field", f"{path}/items", "AIO items missing"
        )
    element_list = _require_array(item.get("items"), f"{path}/items")
    for element_index, raw_element in enumerate(element_list):
        element = _object(raw_element, f"{path}/items/{element_index}")
        _collect_unknown(
            element,
            _AIO_ELEMENT_KEYS,
            f"{path}/items/{element_index}",
            diagnostics,
        )
        element_type = _require_str(
            element.get("type"), f"{path}/items/{element_index}/type"
        )
        if element_type != "ai_overview_element":
            raise GoogleOrganicParseError(
                "unknown_enum",
                f"{path}/items/{element_index}/type",
                "AIO child must be ai_overview_element",
            )
        refs_value = element.get("references")
        if refs_value is None:
            continue
        refs = _require_array(refs_value, f"{path}/items/{element_index}/references")
        for reference_index, raw in enumerate(refs):
            sources.append(
                _parse_aio_reference(
                    raw,
                    f"{path}/items/{element_index}/references/{reference_index}",
                    locus="element",
                    element_index=element_index,
                    reference_index=reference_index,
                    diagnostics=diagnostics,
                )
            )
    return tuple(sources)


def _parse_aio_reference(
    value: object,
    path: str,
    *,
    locus: str,
    element_index: int | None,
    reference_index: int,
    diagnostics: list[ParseDiagnostic],
) -> AiOverviewSource:
    obj = _object(value, path)
    _collect_unknown(obj, _AIO_REFERENCE_KEYS, path, diagnostics)
    ref_type = _require_str(obj.get("type"), f"{path}/type")
    if ref_type != "ai_overview_reference":
        raise GoogleOrganicParseError(
            "unknown_enum", f"{path}/type", "AIO reference type is invalid"
        )
    if locus not in AIO_LOCI:
        raise GoogleOrganicParseError("unknown_enum", path, "AIO source locus is invalid")
    if locus == "element" and element_index is None:
        raise GoogleOrganicParseError(
            "aio_source_locus",
            path,
            "element-level AIO source is missing its element index",
        )
    if locus == "top_level" and element_index is not None:
        raise GoogleOrganicParseError(
            "aio_source_locus",
            path,
            "top-level AIO source must not carry an element index",
        )
    return AiOverviewSource(
        locus=locus,
        element_index=element_index,
        reference_index=reference_index,
        url=_require_http_url(obj.get("url"), f"{path}/url"),
        domain=_optional_str(obj, "domain", f"{path}/domain"),
        title=_optional_str(obj, "title", f"{path}/title"),
        source=_optional_str(obj, "source", f"{path}/source"),
    )


def _parse_paa_questions(
    value: object,
    path: str,
    diagnostics: list[ParseDiagnostic],
    *,
    page: int,
    position: str,
    rank_group: int,
    rank_absolute: int,
) -> tuple[RelatedQuestion, ...]:
    if value is None:
        raise GoogleOrganicParseError("wrong_type", path, "PAA items must be an array")
    raw = _require_array(value, path)
    questions: list[RelatedQuestion] = []
    for index, item in enumerate(raw):
        obj = _object(item, f"{path}/{index}")
        _collect_unknown(obj, _PAA_ELEMENT_KEYS, f"{path}/{index}", diagnostics)
        qtype = _require_str(obj.get("type"), f"{path}/{index}/type")
        if qtype != "people_also_ask_element":
            raise GoogleOrganicParseError(
                "unknown_enum",
                f"{path}/{index}/type",
                "PAA child must be people_also_ask_element",
            )
        title = _require_str(obj.get("title"), f"{path}/{index}/title")
        questions.append(
            RelatedQuestion(
                question_index=index,
                title=title,
                page=page,
                position=position,
                rank_group=rank_group,
                rank_absolute=rank_absolute,
            )
        )
    return tuple(questions)


def _parse_related_search_strings(value: object, path: str) -> tuple[str, ...]:
    raw = _require_array(value, path)
    queries: list[str] = []
    for index, item in enumerate(raw):
        queries.append(_require_str(item, f"{path}/{index}"))
    return tuple(queries)


def _dedupe_related_queries(queries: list[str]) -> tuple[RelatedQuery, ...]:
    seen: set[str] = set()
    unique: list[RelatedQuery] = []
    for query in queries:
        if query in seen:
            continue
        seen.add(query)
        unique.append(RelatedQuery(query=query))
    return tuple(unique)


def _require_unique_placements(items: list[_ParsedTopItem]) -> None:
    absolute: set[tuple[str, int]] = set()
    grouped: set[tuple[str, str, int]] = set()
    for item in items:
        abs_key = (item.position, item.rank_absolute)
        if abs_key in absolute:
            raise GoogleOrganicParseError(
                "duplicate_rank",
                "/tasks/0/result/0/items",
                "duplicate rank_absolute in the same position sequence",
            )
        absolute.add(abs_key)
        group_key = (item.item_type, item.position, item.rank_group)
        if group_key in grouped:
            raise GoogleOrganicParseError(
                "duplicate_rank",
                "/tasks/0/result/0/items",
                "duplicate rank_group for the same item type and position",
            )
        grouped.add(group_key)


def _decode_json(raw: bytes) -> object:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise GoogleOrganicParseError("utf8_bom", "", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GoogleOrganicParseError("invalid_utf8", "", "body is not strict UTF-8") from exc
    decoder = json.JSONDecoder(
        parse_int=int,
        parse_float=Decimal,
        parse_constant=_reject_constant,
        object_pairs_hook=_object_pairs,
    )
    try:
        value, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise GoogleOrganicParseError("invalid_json", "", "body is not valid JSON") from exc
    if text[end:].strip() != "":
        raise GoogleOrganicParseError(
            "trailing_data", "", "non-whitespace data follows the JSON document"
        )
    return value


def _reject_constant(value: str) -> None:
    raise GoogleOrganicParseError("non_finite_number", "", f"{value} is not a finite number")


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise GoogleOrganicParseError(
                "duplicate_member", f"/{_escape(key)}", "duplicate object member name"
            )
        result[key] = value
    return result


def _collect_unknown(
    obj: Mapping[str, object],
    allowed: frozenset[str],
    path: str,
    diagnostics: list[ParseDiagnostic],
) -> None:
    for key in obj:
        if key not in allowed:
            pointer = f"{path}/{_escape(key)}" if path else f"/{_escape(key)}"
            diagnostics.append(ParseDiagnostic("unknown_extension_field", pointer))


def _object(value: object, path: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise GoogleOrganicParseError("wrong_type", path, "object required")
    return value


def _require_array(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise GoogleOrganicParseError("wrong_type", path, "array required")
    return value


def _require_str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise GoogleOrganicParseError("wrong_type", path, "string required")
    return value


def _require_int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GoogleOrganicParseError("wrong_type", path, "integer required")
    return value


def _require_bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise GoogleOrganicParseError("wrong_type", path, "boolean required")
    return value


def _require_stated_int(obj: Mapping[str, object], key: str, path: str) -> Field[int]:
    if key not in obj:
        raise GoogleOrganicParseError("missing_field", path, f"{key} missing")
    return Field[int].stated(_require_int(obj[key], path))


def _optional_str(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    if key not in obj:
        return Field[str].absent()
    if obj[key] is None:
        return Field[str].json_null()
    return Field[str].stated(_require_str(obj[key], path))


def _optional_int(obj: Mapping[str, object], key: str, path: str) -> Field[int]:
    if key not in obj:
        return Field[int].absent()
    if obj[key] is None:
        return Field[int].json_null()
    return Field[int].stated(_require_int(obj[key], path))


def _optional_decimal(obj: Mapping[str, object], key: str, path: str) -> Field[Decimal]:
    if key not in obj:
        return Field[Decimal].absent()
    if obj[key] is None:
        return Field[Decimal].json_null()
    value = obj[key]
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise GoogleOrganicParseError("wrong_type", path, "decimal required")
    if isinstance(value, int):
        return Field[Decimal].stated(Decimal(value))
    return Field[Decimal].stated(value)


def _optional_url(obj: Mapping[str, object], key: str, path: str) -> Field[str]:
    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_http_url(field.value, path)
    return field


def _optional_result_datetime(
    obj: Mapping[str, object], key: str, path: str
) -> Field[str]:
    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_result_datetime(field.value, path)
    return field


def _require_result_datetime(value: str, path: str) -> None:
    if _RESULT_DATETIME_RE.fullmatch(value) is None:
        raise GoogleOrganicParseError(
            "invalid_timestamp", path, "result datetime is malformed"
        )
    try:
        datetime.strptime(value.removesuffix(" +00:00"), "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise GoogleOrganicParseError(
            "invalid_timestamp", path, "result datetime is not a real UTC datetime"
        ) from exc


def _require_utc_clock_lexical(
    value: str, path: str, code: str, subject: str
) -> None:
    """One strict UTC lexical grammar shared by four semantically distinct fields.

    Shared syntax never implies shared meaning: result retrieval `datetime`, the
    organic item timestamp, the Top Stories child timestamp, and the Video child
    timestamp each keep their own named helper, field, column, and error code.
    """

    if _UTC_CLOCK_RE.fullmatch(value) is None:
        raise GoogleOrganicParseError(code, path, f"{subject} is malformed")
    try:
        datetime.strptime(value.removesuffix(" +00:00"), "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise GoogleOrganicParseError(
            code, path, f"{subject} is not a real UTC datetime"
        ) from exc


def _optional_organic_item_timestamp(
    obj: Mapping[str, object], key: str, path: str
) -> Field[str]:
    """Exact provider-stated organic item/result timestamp testimony.

    Never inherited from result `datetime`, Capture time, Provider Update Time,
    Data Period, `pre_snippet`, or another row.
    """

    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_utc_clock_lexical(
            field.value, path, "invalid_organic_item_timestamp", "organic item timestamp"
        )
    return field


def _optional_top_story_item_timestamp(
    obj: Mapping[str, object], key: str, path: str
) -> Field[str]:
    """Exact provider-stated Top Stories child item timestamp testimony.

    Never inherited from the sibling relative `date` string or any other clock.
    """

    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_utc_clock_lexical(
            field.value,
            path,
            "invalid_top_story_item_timestamp",
            "top stories item timestamp",
        )
    return field


def _optional_video_item_timestamp(
    obj: Mapping[str, object], key: str, path: str
) -> Field[str]:
    """Exact provider-stated Video child item timestamp testimony."""

    field = _optional_str(obj, key, path)
    if field.state is FieldState.STATED:
        assert field.value is not None
        _require_utc_clock_lexical(
            field.value, path, "invalid_video_item_timestamp", "video item timestamp"
        )
    return field


def _require_http_url(value: object, path: str) -> str:
    text = _require_str(value, path)
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or parsed.netloc == "" or " " in text:
        raise GoogleOrganicParseError("invalid_url", path, "absolute http(s) URL required")
    return text


def _escape(part: str) -> str:
    return part.replace("~", "~0").replace("/", "~1")
