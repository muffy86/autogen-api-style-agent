import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ locals }) => {
  if (!locals.session || !locals.user) {
    return new Response(JSON.stringify({ error: 'Auth required' }), { status: 401 });
  }

  const { error } = await locals.supabase
    .from('integrations')
    .delete()
    .eq('user_id', locals.user.id)
    .eq('provider', 'github');

  if (error) {
    return new Response(JSON.stringify({ error: 'Failed to disconnect' }), { status: 500 });
  }

  return new Response(JSON.stringify({ success: true }), {
    headers: { 'Content-Type': 'application/json' },
  });
};
