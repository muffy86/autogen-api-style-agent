import { createSupabaseServerClient } from '$lib/supabase/server';
import { redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
  const supabase = createSupabaseServerClient(event.cookies);
  event.locals.supabase = supabase;

  const { data: { session } } = await supabase.auth.getSession();
  event.locals.session = session;
  event.locals.user = session?.user ?? null;

  const isAuthRoute = event.url.pathname.startsWith('/login') ||
                      event.url.pathname.startsWith('/auth');

  if (!session && !isAuthRoute) {
    throw redirect(303, '/login');
  }

  return resolve(event);
};
