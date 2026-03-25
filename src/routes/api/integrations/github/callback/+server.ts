import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals }) => {
  if (!locals.session || !locals.user) {
    throw redirect(303, '/login');
  }

  const code = url.searchParams.get('code');
  if (!code) {
    throw redirect(303, '/?error=github_no_code');
  }

  const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code,
    }),
  });

  const tokenData = await tokenResponse.json();
  if (tokenData.error || !tokenData.access_token) {
    console.error('GitHub OAuth error:', tokenData);
    throw redirect(303, '/?error=github_auth_failed');
  }

  const userResponse = await fetch('https://api.github.com/user', {
    headers: { Authorization: `Bearer ${tokenData.access_token}` },
  });
  const githubUser = await userResponse.json();

  const { error } = await locals.supabase
    .from('integrations')
    .upsert({
      user_id: locals.user.id,
      provider: 'github',
      access_token: tokenData.access_token,
      scope: tokenData.scope,
      username: githubUser.login,
      avatar_url: githubUser.avatar_url,
      metadata: {
        github_id: githubUser.id,
        name: githubUser.name,
        html_url: githubUser.html_url,
      },
    }, { onConflict: 'user_id,provider' });

  if (error) {
    console.error('Failed to store GitHub integration:', error);
    throw redirect(303, '/?error=github_store_failed');
  }

  throw redirect(303, '/?github=connected');
};
