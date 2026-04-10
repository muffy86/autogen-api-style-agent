from __future__ import annotations

import fnmatch
import re
from pathlib import Path


async def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Error: File not found: {path}"
    if not p.is_file():
        return f"Error: Not a file: {path}"
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        if len(content) > 100_000:
            return content[:100_000] + f"\n\n... [truncated, total {len(content)} chars]"
        return content
    except Exception as e:
        return f"Error reading file: {e}"


async def write_file(path: str, content: str) -> str:
    """Write content to a file, creating directories if needed."""
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


async def list_directory(path: str = ".") -> str:
    """List files and directories at the given path."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: Directory not found: {path}"
        if not p.is_dir():
            return f"Error: Not a directory: {path}"

        entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        lines = []
        for entry in entries[:200]:
            prefix = "📁 " if entry.is_dir() else "📄 "
            size = ""
            if entry.is_file():
                sz = entry.stat().st_size
                if sz < 1024:
                    size = f" ({sz}B)"
                elif sz < 1024 * 1024:
                    size = f" ({sz / 1024:.1f}KB)"
                else:
                    size = f" ({sz / 1024 / 1024:.1f}MB)"
            lines.append(f"{prefix}{entry.name}{size}")

        total = len(list(p.iterdir()))
        result = "\n".join(lines)
        if total > 200:
            result += f"\n\n... and {total - 200} more entries"
        return result
    except Exception as e:
        return f"Error listing directory: {e}"


async def search_files(pattern: str, directory: str = ".") -> str:
    """Search for files matching a glob pattern."""
    try:
        p = Path(directory).expanduser().resolve()
        if not p.exists():
            return f"Error: Directory not found: {directory}"

        matches = sorted(p.rglob(pattern))[:100]
        if not matches:
            return f"No files matching '{pattern}' found in {directory}"
        lines = [str(m.relative_to(p)) for m in matches]
        result = "\n".join(lines)
        if len(matches) == 100:
            result += "\n\n... (showing first 100 matches)"
        return result
    except Exception as e:
        return f"Error searching files: {e}"


async def find_in_files(query: str, directory: str = ".", file_pattern: str = "*.py") -> str:
    """Search for a string/regex pattern within files."""
    try:
        p = Path(directory).expanduser().resolve()
        if not p.exists():
            return f"Error: Directory not found: {directory}"

        pattern = re.compile(query, re.IGNORECASE)
        results: list[str] = []
        file_count = 0

        for filepath in p.rglob("*"):
            if not filepath.is_file():
                continue
            if not fnmatch.fnmatch(filepath.name, file_pattern):
                continue
            file_count += 1
            try:
                text = filepath.read_text(encoding="utf-8", errors="replace")
                for i, line in enumerate(text.splitlines(), 1):
                    if pattern.search(line):
                        rel = filepath.relative_to(p)
                        results.append(f"{rel}:{i}: {line.strip()}")
                        if len(results) >= 100:
                            break
            except Exception:
                continue
            if len(results) >= 100:
                break

        if not results:
            return f"No matches for '{query}' in {file_count} files"
        output = "\n".join(results)
        if len(results) == 100:
            output += "\n\n... (showing first 100 matches)"
        return output
    except Exception as e:
        return f"Error searching in files: {e}"
