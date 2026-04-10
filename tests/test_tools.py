from __future__ import annotations

import asyncio
import builtins
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from autogen_api_agent.tools.code_analysis import analyze_python_file, check_syntax
from autogen_api_agent.tools.file_ops import (
    find_in_files,
    list_directory,
    read_file,
    search_files,
    write_file,
)
from autogen_api_agent.tools.github_tools import (
    create_issue,
    get_pr_diff,
    get_repo_info,
    list_issues,
)
from autogen_api_agent.tools.shell_exec import run_command
from autogen_api_agent.tools.web_search import _strip_html, fetch_url, web_search


class _FakeResponse:
    def __init__(self, text: str, content_type: str = "text/html", status_code: int = 200):
        self.text = text
        self.headers = {"content-type": content_type}
        self.status_code = status_code
        self.request = httpx.Request("GET", "https://example.com")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "boom",
                request=self.request,
                response=httpx.Response(self.status_code, request=self.request),
            )


class _FakeAsyncClient:
    def __init__(self, response: _FakeResponse):
        self.response = response
        self.requests: list[tuple[str, dict | None]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str, headers: dict | None = None):
        self.requests.append((url, headers))
        return self.response


class _FakeIssues(list):
    def __init__(self, items):
        super().__init__(items)
        self.totalCount = len(items)


def _install_fake_github_module(repo) -> ModuleType:
    module = ModuleType("github")

    class FakeGithub:
        def __init__(self, token: str | None = None):
            self.token = token

        def get_repo(self, full_name: str):
            assert full_name == "capy/repo"
            return repo

    module.Github = FakeGithub
    return module


@pytest.mark.asyncio
async def test_read_file_reads_existing_file_content(tmp_path: Path) -> None:
    target = tmp_path / "example.txt"
    target.write_text("hello world", encoding="utf-8")

    assert await read_file(str(target)) == "hello world"


@pytest.mark.asyncio
async def test_read_file_returns_error_for_missing_file(tmp_path: Path) -> None:
    result = await read_file(str(tmp_path / "missing.txt"))

    assert result == f"Error: File not found: {tmp_path / 'missing.txt'}"


@pytest.mark.asyncio
async def test_write_file_creates_file_and_parent_directories(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir" / "file.txt"

    result = await write_file(str(target), "content")

    assert target.read_text(encoding="utf-8") == "content"
    assert result == f"Successfully wrote 7 chars to {target}"


@pytest.mark.asyncio
async def test_list_directory_lists_files_with_metadata(tmp_path: Path) -> None:
    (tmp_path / "subdir").mkdir()
    file_path = tmp_path / "file.txt"
    file_path.write_text("abc", encoding="utf-8")

    result = await list_directory(str(tmp_path))

    assert "📁 subdir" in result
    assert "📄 file.txt (3B)" in result


@pytest.mark.asyncio
async def test_search_files_finds_matching_patterns(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('a')", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.py").write_text("print('b')", encoding="utf-8")

    result = await search_files("*.py", str(tmp_path))

    assert "a.py" in result
    assert "nested/b.py" in result


@pytest.mark.asyncio
async def test_find_in_files_finds_regex_matches_in_file_content(tmp_path: Path) -> None:
    (tmp_path / "one.py").write_text("def my_func():\n    return 1\n", encoding="utf-8")
    (tmp_path / "two.py").write_text("print('nothing')\n", encoding="utf-8")

    result = await find_in_files(r"my_func", str(tmp_path), "*.py")

    assert "one.py:1: def my_func():" in result


@pytest.mark.asyncio
async def test_run_command_echo_returns_output() -> None:
    result = await run_command("echo hello")

    assert result == "hello"


@pytest.mark.asyncio
async def test_run_command_blocked_pattern_returns_error() -> None:
    result = await run_command("rm -rf /")

    assert result == "Error: Blocked dangerous command pattern: rm -rf /"


@pytest.mark.asyncio
async def test_run_command_handles_timeout() -> None:
    proc = MagicMock()

    async def delayed_communicate():
        await asyncio.sleep(0.01)
        return (b"", b"")

    proc.communicate = delayed_communicate

    with patch(
        "autogen_api_agent.tools.shell_exec.asyncio.create_subprocess_shell",
        AsyncMock(return_value=proc),
    ):
        result = await run_command("sleep 10", timeout=0)

    proc.kill.assert_called_once()
    assert result == "Error: Command timed out after 0s"


@pytest.mark.asyncio
async def test_web_search_returns_formatted_results() -> None:
    fake_module = ModuleType("duckduckgo_search")

    class FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query: str, max_results: int = 5):
            assert query == "capybara"
            assert max_results == 2
            return [
                {"title": "Result One", "href": "https://one.example", "body": "First body"},
                {"title": "Result Two", "href": "https://two.example", "body": "Second body"},
            ]

    fake_module.DDGS = FakeDDGS

    with patch.dict(sys.modules, {"duckduckgo_search": fake_module}):
        result = await web_search("capybara", max_results=2)

    assert "1. **Result One**" in result
    assert "URL: https://one.example" in result
    assert "2. **Result Two**" in result


@pytest.mark.asyncio
async def test_web_search_handles_import_error_gracefully() -> None:
    original_import = builtins.__import__

    def raising_import(name, *args, **kwargs):
        if name == "duckduckgo_search":
            raise ImportError
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=raising_import):
        result = await web_search("capybara")

    assert result == "Error: duckduckgo-search package not installed"


@pytest.mark.asyncio
async def test_fetch_url_returns_page_content() -> None:
    response = _FakeResponse("<html><body>Hello <b>world</b></body></html>")
    fake_client = _FakeAsyncClient(response)

    with patch("autogen_api_agent.tools.web_search.httpx.AsyncClient", return_value=fake_client):
        result = await fetch_url("https://example.com")

    assert result == "Hello world"


def test_strip_html_removes_tags_and_collapses_whitespace() -> None:
    html = "<html><body><script>bad()</script><p>Hello&nbsp;&amp;\n world</p></body></html>"

    assert _strip_html(html) == "Hello & world"


@pytest.mark.asyncio
async def test_analyze_python_file_extracts_imports_classes_functions_and_complexity(
    tmp_path: Path,
) -> None:
    source = (
        "import os\n"
        "from pathlib import Path\n\n"
        "class Demo(Base):\n"
        "    def method(self):\n"
        "        return 1\n\n"
        "async def worker(a, b):\n"
        "    if a and b:\n"
        "        for item in range(2):\n"
        "            print(item)\n"
    )
    target = tmp_path / "sample.py"
    target.write_text(source, encoding="utf-8")

    result = await analyze_python_file(str(target))

    assert "**Imports (2):**" in result
    assert "  - os" in result
    assert "  - pathlib.Path" in result
    assert "class Demo(Base) [line 4, 1 methods: method]" in result
    assert "async def worker(a, b) [line 8, complexity: 4]" in result


@pytest.mark.asyncio
async def test_check_syntax_returns_ok_for_valid_python() -> None:
    result = await check_syntax("x = 1\nprint(x)\n")

    assert result == "Syntax OK: No errors found."


@pytest.mark.asyncio
async def test_check_syntax_reports_errors_for_invalid_python() -> None:
    result = await check_syntax("def broken(:\n    pass\n")

    assert "Syntax Error at line 1" in result
    assert "invalid syntax" in result.lower()


@pytest.mark.asyncio
async def test_check_syntax_returns_unsupported_for_non_python() -> None:
    result = await check_syntax("const x = 1;", language="javascript")

    assert "Only Python is available" in result


@pytest.mark.asyncio
async def test_get_repo_info_returns_formatted_info() -> None:
    repo = SimpleNamespace(
        full_name="capy/repo",
        description="Example repo",
        stargazers_count=10,
        forks_count=2,
        language="Python",
        default_branch="main",
        open_issues_count=3,
        created_at="2024-01-01",
        updated_at="2024-01-02",
        html_url="https://github.com/capy/repo",
        topics=["agents", "tests"],
    )
    fake_module = _install_fake_github_module(repo)

    with patch.dict(sys.modules, {"github": fake_module}):
        result = await get_repo_info("capy", "repo")

    assert "**capy/repo**" in result
    assert "Stars: 10 | Forks: 2" in result
    assert "Topics: agents, tests" in result


@pytest.mark.asyncio
async def test_list_issues_returns_formatted_issues() -> None:
    issue = SimpleNamespace(
        number=12,
        title="Bug report",
        labels=[SimpleNamespace(name="bug")],
        state="open",
        user=SimpleNamespace(login="capy"),
        updated_at="2024-01-03",
    )
    repo = SimpleNamespace(get_issues=lambda **kwargs: _FakeIssues([issue]))
    fake_module = _install_fake_github_module(repo)

    with patch.dict(sys.modules, {"github": fake_module}):
        result = await list_issues("capy", "repo")

    assert "#12 Bug report [bug]" in result
    assert "State: open | Author: capy" in result


@pytest.mark.asyncio
async def test_create_issue_requires_github_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    result = await create_issue("capy", "repo", "Title", "Body")

    assert result == "Error: GITHUB_TOKEN environment variable required to create issues"


@pytest.mark.asyncio
async def test_get_pr_diff_returns_formatted_diff() -> None:
    changed_file = SimpleNamespace(
        filename="app.py",
        additions=5,
        deletions=1,
        patch="@@ -1 +1 @@\n-print('old')\n+print('new')",
    )
    pull_request = SimpleNamespace(
        number=7,
        title="Improve logging",
        user=SimpleNamespace(login="capy"),
        state="open",
        base=SimpleNamespace(ref="main"),
        head=SimpleNamespace(ref="feature"),
        changed_files=1,
        additions=5,
        deletions=1,
        get_files=lambda: [changed_file],
    )
    repo = SimpleNamespace(get_pull=lambda pr_number: pull_request)
    fake_module = _install_fake_github_module(repo)

    with patch.dict(sys.modules, {"github": fake_module}):
        result = await get_pr_diff("capy", "repo", 7)

    assert "**PR #7: Improve logging**" in result
    assert "Changed files: 1 | +5 -1" in result
    assert "--- app.py (+5 -1)" in result
