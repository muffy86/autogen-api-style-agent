from __future__ import annotations

import os


async def get_repo_info(owner: str, repo: str) -> str:
    """Get GitHub repository information."""
    try:
        from github import Github

        token = os.environ.get("GITHUB_TOKEN", "")
        g = Github(token) if token else Github()
        r = g.get_repo(f"{owner}/{repo}")

        info = [
            f"**{r.full_name}**",
            f"Description: {r.description or 'N/A'}",
            f"Stars: {r.stargazers_count} | Forks: {r.forks_count}",
            f"Language: {r.language or 'N/A'}",
            f"Default branch: {r.default_branch}",
            f"Open issues: {r.open_issues_count}",
            f"Created: {r.created_at}",
            f"Updated: {r.updated_at}",
            f"URL: {r.html_url}",
        ]
        if r.topics:
            info.append(f"Topics: {', '.join(r.topics)}")
        return "\n".join(info)
    except ImportError:
        return "Error: PyGithub package not installed"
    except Exception as e:
        return f"Error getting repo info: {e}"


async def list_issues(owner: str, repo: str, state: str = "open") -> str:
    """List GitHub issues for a repository."""
    try:
        from github import Github

        token = os.environ.get("GITHUB_TOKEN", "")
        g = Github(token) if token else Github()
        r = g.get_repo(f"{owner}/{repo}")
        issues = r.get_issues(state=state, sort="updated", direction="desc")

        lines = []
        for i, issue in enumerate(issues):
            if i >= 20:
                lines.append(f"\n... showing first 20 of {issues.totalCount} issues")
                break
            labels = ", ".join(lb.name for lb in issue.labels) if issue.labels else ""
            label_str = f" [{labels}]" if labels else ""
            lines.append(f"#{issue.number} {issue.title}{label_str}")
            lines.append(f"  State: {issue.state} | Author: {issue.user.login}")
            lines.append(f"  Updated: {issue.updated_at}")
            lines.append("")

        if not lines:
            return f"No {state} issues found in {owner}/{repo}"
        return "\n".join(lines)
    except ImportError:
        return "Error: PyGithub package not installed"
    except Exception as e:
        return f"Error listing issues: {e}"


async def create_issue(owner: str, repo: str, title: str, body: str) -> str:
    """Create a new GitHub issue."""
    try:
        from github import Github

        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return "Error: GITHUB_TOKEN environment variable required to create issues"
        g = Github(token)
        r = g.get_repo(f"{owner}/{repo}")
        issue = r.create_issue(title=title, body=body)
        return f"Created issue #{issue.number}: {issue.html_url}"
    except ImportError:
        return "Error: PyGithub package not installed"
    except Exception as e:
        return f"Error creating issue: {e}"


async def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Get the diff for a pull request."""
    try:
        from github import Github

        token = os.environ.get("GITHUB_TOKEN", "")
        g = Github(token) if token else Github()
        r = g.get_repo(f"{owner}/{repo}")
        pr = r.get_pull(pr_number)

        info = [
            f"**PR #{pr.number}: {pr.title}**",
            f"Author: {pr.user.login} | State: {pr.state}",
            f"Base: {pr.base.ref} <- Head: {pr.head.ref}",
            f"Changed files: {pr.changed_files} | +{pr.additions} -{pr.deletions}",
            "",
        ]

        files = pr.get_files()
        for f in files:
            info.append(f"--- {f.filename} (+{f.additions} -{f.deletions})")
            if f.patch:
                patch = f.patch
                if len(patch) > 2000:
                    patch = patch[:2000] + "\n... [truncated]"
                info.append(patch)
            info.append("")

        result = "\n".join(info)
        if len(result) > 10000:
            result = result[:10000] + "\n\n... [truncated]"
        return result
    except ImportError:
        return "Error: PyGithub package not installed"
    except Exception as e:
        return f"Error getting PR diff: {e}"
