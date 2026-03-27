import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { createSupabaseServerClient } from '$lib/supabase/server';

export const GET: RequestHandler = async ({ url, cookies }) => {
  const code = url.searchParams.get('code');
  if (code) {
    const supabase = createSupabaseServerClient(cookies);
    await supabase.auth.exchangeCodeForSession(code);
  }
  throw redirect(303, '/');
};
