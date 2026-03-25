"""Pre-configured agent teams."""
from __future__ import annotations

from .code_review import create_code_review_team
from .productivity import create_productivity_team
from .quick import create_quick_agent
from .research import create_research_team

_TEAM_MAP = {
    "productivity": create_productivity_team,
    "code_review": create_code_review_team,
    "research": create_research_team,
    "quick": create_quick_agent,
}


def create_team(
    team_name: str = "productivity",
    factory=None,
    provider: str | None = None,
    model: str | None = None,
    config=None,
):
    """Dispatch to the appropriate team creation function by name."""
    creator = _TEAM_MAP.get(team_name)
    if creator is None:
        raise ValueError(
            f"Unknown team: {team_name!r}. Available: {list(_TEAM_MAP)}"
        )
    kwargs: dict = {"factory": factory}
    if provider is not None:
        kwargs["provider"] = provider
    if model is not None:
        kwargs["model"] = model
    if config is not None:
        kwargs["config"] = config
    return creator(**kwargs)


__all__ = [
    "create_code_review_team",
    "create_productivity_team",
    "create_quick_agent",
    "create_research_team",
    "create_team",
]
