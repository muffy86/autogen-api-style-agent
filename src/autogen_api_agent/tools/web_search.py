from __future__ import annotations

import re

import httpx


async def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo and return results."""
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for: {query}"

        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r.get('title', 'No title')}**")
            lines.append(f"   URL: {r.get('href', 'N/A')}")
            lines.append(f"   {r.get('body', 'No description')}")
            lines.append("")

        return "\n".join(lines)
    except ImportError:
        return "Error: duckduckgo-search package not installed"
    except Exception as e:
        return f"Error performing web search: {e}"


async def fetch_url(url: str) -> str:
    """Fetch a web page and return its text content (truncated to ~4000 chars)."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=15.0
        ) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; AutogenAgent/1.0; "
                        "+https://github.com/muffy86/autogen-api-style-agent)"
                    )
                },
            )
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")

            text = (
                _strip_html(resp.text) if "text/html" in content_type else resp.text
            )

            if len(text) > 4000:
                text = text[:4000] + "\n\n... [truncated]"
            return text
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}: {e}"
    except Exception as e:
        return f"Error fetching URL: {e}"


def _strip_html(html: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#\d+;", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
