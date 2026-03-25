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
    return new Response(JSON.stringify({ error: 'GitHub not connected', needsAuth: true }), {
      status: 403,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const octokit = new Octokit({ auth: integration.access_token });
    const page = parseInt(url.searchParams.get('page') || '1');
    const perPage = Math.min(parseInt(url.searchParams.get('per_page') || '20'), 50);

    const { data: repos } = await octokit.repos.listForAuthenticatedUser({
      sort: 'updated',
      per_page: perPage,
      page,
    });

    const cleaned = repos.map(r => ({
      id: r.id,
      name: r.name,
      full_name: r.full_name,
      description: r.description,
      html_url: r.html_url,
      language: r.language,
      stargazers_count: r.stargazers_count,
      forks_count: r.forks_count,
      open_issues_count: r.open_issues_count,
      private: r.private,
      updated_at: r.updated_at,
      default_branch: r.default_branch,
    }));

    return new Response(JSON.stringify({ repos: cleaned }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err: any) {
    if (err.status === 401) {
      await locals.supabase.from('integrations').delete()
        .eq('user_id', locals.user.id).eq('provider', 'github');
      return new Response(JSON.stringify({ error: 'GitHub token expired. Please reconnect.', needsAuth: true }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    return new Response(JSON.stringify({ error: 'Failed to fetch repos' }), { status: 500 });
  }
};
