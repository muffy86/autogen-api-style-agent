from __future__ import annotations

import ast
from pathlib import Path


async def analyze_python_file(path: str) -> str:
    """Analyze a Python file: functions, classes, complexity, imports."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return f"Error: File not found: {path}"
        if p.suffix != ".py":
            return f"Error: Not a Python file: {path}"

        source = p.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=path)

        imports: list[str] = []
        classes: list[str] = []
        functions: list[str] = []
        total_lines = len(source.splitlines())

        _set_parents(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
            elif isinstance(node, ast.ClassDef):
                methods = [
                    n.name
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(ast.dump(base))
                base_str = f"({', '.join(bases)})" if bases else ""
                classes.append(
                    f"class {node.name}{base_str} "
                    f"[line {node.lineno}, {len(methods)} methods: "
                    f"{', '.join(methods)}]"
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parent = getattr(node, "_parent", None)
                if isinstance(parent, ast.ClassDef):
                    continue
                prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
                args = [a.arg for a in node.args.args]
                complexity = _calc_complexity(node)
                functions.append(
                    f"{prefix}def {node.name}({', '.join(args)}) "
                    f"[line {node.lineno}, complexity: {complexity}]"
                )

        sections = [f"**File: {path}** ({total_lines} lines)\n"]

        if imports:
            sections.append(f"**Imports ({len(imports)}):**")
            for imp in imports[:30]:
                sections.append(f"  - {imp}")
            if len(imports) > 30:
                sections.append(f"  ... and {len(imports) - 30} more")

        if classes:
            sections.append(f"\n**Classes ({len(classes)}):**")
            for cls in classes:
                sections.append(f"  - {cls}")

        if functions:
            sections.append(f"\n**Functions ({len(functions)}):**")
            for fn in functions:
                sections.append(f"  - {fn}")

        return "\n".join(sections)
    except SyntaxError as e:
        return f"Syntax error in {path}: {e}"
    except Exception as e:
        return f"Error analyzing file: {e}"


async def check_syntax(code: str, language: str = "python") -> str:
    """Check code syntax for errors."""
    if language != "python":
        return (
            f"Syntax checking for '{language}' is not yet supported. "
            "Only Python is available."
        )

    try:
        ast.parse(code)
        return "Syntax OK: No errors found."
    except SyntaxError as e:
        return (
            f"Syntax Error at line {e.lineno}, col {e.offset}:\n"
            f"  {e.msg}\n"
            f"  {e.text.rstrip() if e.text else ''}"
        )


def _calc_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of a function node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(
            child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)
        ):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif isinstance(child, ast.Assert):
            complexity += 1
    return complexity


def _set_parents(tree: ast.AST) -> None:
    """Set _parent attribute on all child nodes."""
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._parent = node  # type: ignore[attr-defined]
