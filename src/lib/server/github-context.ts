import { Octokit } from '@octokit/rest';

export async function getGitHubContext(accessToken: string): Promise<string> {
  try {
    const octokit = new Octokit({ auth: accessToken });

    const [{ data: user }, { data: repos }, { data: issues }] = await Promise.all([
      octokit.users.getAuthenticated(),
      octokit.repos.listForAuthenticatedUser({ sort: 'updated', per_page: 10 }),
      octokit.issues.listForAuthenticatedUser({ filter: 'assigned', state: 'open', per_page: 10 }),
    ]);

    const repoList = repos.map(r =>
      `- ${r.full_name} (${r.language || 'unknown'}, ★${r.stargazers_count}, ${r.private ? 'private' : 'public'}) — ${r.description || 'No description'}`
    ).join('\n');

    const issueList = issues.map(i =>
      `- [${i.repository?.full_name}#${i.number}] ${i.title} (${i.state})`
    ).join('\n');

    return `\n\n[GitHub Context for ${user.login}]\nRecent repos:\n${repoList}\n\nOpen issues assigned to you:\n${issueList}\n`;
  } catch {
    return '';
  }
}
