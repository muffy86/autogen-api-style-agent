import { Octokit } from '@octokit/rest';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals, url }) => {
  if (!locals.session || !locals.user) {
    return new Response(JSON.stringify({ error: 'Auth required' }), { status: 401 });
  }

  const { data: integration } = await locals.supabase
    .from('integrations')
    .select('access_token')
    .eq('user_id', locals.user.id)
    .eq('provider', 'github')
    .single();

  if (!integration) {
    return new Response(JSON.stringify({ error: 'GitHub not connected', needsAuth: true }), { status: 403 });
  }

  try {
    const octokit = new Octokit({ auth: integration.access_token });
    const repo = url.searchParams.get('repo');
    const state = url.searchParams.get('state') || 'open';

    if (repo) {
      const [owner, repoName] = repo.split('/');
      const { data: issues } = await octokit.issues.listForRepo({
        owner, repo: repoName, state: state as 'open' | 'closed' | 'all',
        per_page: 20, sort: 'updated',
      });
      const cleaned = issues.map(i => ({
        id: i.id, number: i.number, title: i.title, state: i.state,
        html_url: i.html_url, created_at: i.created_at, updated_at: i.updated_at,
        labels: i.labels.map((l: any) => ({ name: l.name, color: l.color })),
        user: { login: i.user?.login, avatar_url: i.user?.avatar_url },
        pull_request: !!i.pull_request,
      }));
      return new Response(JSON.stringify({ issues: cleaned }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { data: issues } = await octokit.issues.listForAuthenticatedUser({
      filter: 'assigned', state: state as 'open' | 'closed' | 'all', per_page: 20, sort: 'updated',
    });
    const cleaned = issues.map(i => ({
      id: i.id, number: i.number, title: i.title, state: i.state,
      html_url: i.html_url, repository: i.repository?.full_name,
      created_at: i.created_at, updated_at: i.updated_at,
      labels: i.labels?.map((l: any) => ({ name: l.name, color: l.color })) || [],
    }));
    return new Response(JSON.stringify({ issues: cleaned }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: 'Failed to fetch issues' }), { status: 500 });
  }
};
