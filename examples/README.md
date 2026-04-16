# Examples

These runnable scripts demonstrate common ways to use `autogen_api_agent`.

## Prerequisites

- Install the project dependencies.
- Configure at least one provider API key in `.env`.
- Run examples from the repository root so the package imports resolve as expected.

## Running an example

```bash
python examples/01_quick_chat.py
```

## Included examples

- `01_quick_chat.py` — single-agent quick chat with the `quick` team.
- `02_productivity_team.py` — full 8-agent `productivity` team coordinated with `SelectorGroupChat`.
- `03_code_review.py` — focused `code_review` team for bugs, security, and design feedback.
- `04_research_team.py` — streaming output from the `research` team.
- `05_session_continuity.py` — manual session history management across multiple turns.
- `06_provider_fallback.py` — provider detection and best-available client selection.

## Quick Start

Make sure you have configured your API keys in `.env` before running examples.
