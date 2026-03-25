import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals, url }) => {
  if (!locals.session || !locals.user) {
    throw redirect(303, '/login');
  }

  const clientId = env.GITHUB_CLIENT_ID;
  if (!clientId) {
    return new Response(JSON.stringify({ error: 'GitHub integration not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const state = crypto.randomUUID();
  const redirectUrl = new URL('https://github.com/login/oauth/authorize');
  redirectUrl.searchParams.set('client_id', clientId);
  redirectUrl.searchParams.set('redirect_uri', `${url.origin}/api/integrations/github/callback`);
  redirectUrl.searchParams.set('scope', 'repo read:user read:org');
  redirectUrl.searchParams.set('state', state);

  throw redirect(302, redirectUrl.toString());
};
