from __future__ import annotations

from .errors import ReadError
from .fixtures import GRANTS
from .models import CallerGrant


def authorize(caller_class: str, scope_id: str, request_type: str) -> CallerGrant:
    grant = GRANTS.get(caller_class)
    if grant is None:
        raise ReadError("blocked_authentication")
    if request_type not in grant.request_types:
        raise ReadError("blocked_authorization")
    if scope_id not in grant.scopes:
        raise ReadError("blocked_scope")
    return grant
