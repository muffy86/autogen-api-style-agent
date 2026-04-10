from __future__ import annotations

import asyncio

BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs.",
    ":(){:|:&};:",
    "dd if=/dev/zero of=/dev/sd",
    "chmod -R 777 /",
    "> /dev/sda",
    "mv / ",
]


async def run_command(command: str, timeout: int = 30) -> str:
    """Execute a shell command safely with timeout. Returns stdout + stderr."""
    cmd_lower = command.lower().strip()
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            return f"Error: Blocked dangerous command pattern: {pattern}"

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=None,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return f"Error: Command timed out after {timeout}s"

        output_parts = []
        if stdout:
            decoded = stdout.decode("utf-8", errors="replace")
            output_parts.append(decoded)
        if stderr:
            decoded = stderr.decode("utf-8", errors="replace")
            output_parts.append(f"[stderr]\n{decoded}")

        result = "\n".join(output_parts).strip()
        if proc.returncode != 0:
            result = f"[exit code: {proc.returncode}]\n{result}"

        if len(result) > 10000:
            result = result[:10000] + "\n\n... [truncated]"

        return result or "(no output)"
    except Exception as e:
        return f"Error executing command: {e}"
