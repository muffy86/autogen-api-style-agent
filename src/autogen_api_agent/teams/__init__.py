"""Pre-configured agent teams."""

from .code_review import create_code_review_team
from .productivity import create_productivity_team
from .quick import create_quick_agent
from .research import create_research_team

__all__ = [
    "create_code_review_team",
    "create_productivity_team",
    "create_quick_agent",
    "create_research_team",
]
