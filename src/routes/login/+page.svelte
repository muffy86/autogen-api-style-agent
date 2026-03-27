<script lang="ts">
  import { createSupabaseBrowserClient } from '$lib/supabase/client';
  import { Sparkles } from 'lucide-svelte';

  const supabase = createSupabaseBrowserClient();
  let email = $state('');
  let loading = $state(false);
  let message = $state('');

  async function signInWithGitHub() {
    loading = true;
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'github',
      options: { redirectTo: `${window.location.origin}/auth/callback` }
    });
    if (error) message = error.message;
    loading = false;
  }

  async function signInWithGoogle() {
    loading = true;
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` }
    });
    if (error) message = error.message;
    loading = false;
  }

  async function signInWithEmail() {
    if (!email.trim()) return;
    loading = true;
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback` }
    });
    if (error) {
      message = error.message;
    } else {
      message = 'Check your email for a login link!';
    }
    loading = false;
  }
</script>

<div class="login-page">
  <div class="login-card glass">
    <div class="login-logo">
      <Sparkles size={32} strokeWidth={1.5} />
    </div>
    <h1 class="login-title">Elysium AI OS</h1>
    <p class="login-subtitle">Sign in to your AI workspace</p>

    <div class="oauth-buttons">
      <button class="oauth-btn github" onclick={signInWithGitHub} disabled={loading}>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
        Continue with GitHub
      </button>
      <button class="oauth-btn google" onclick={signInWithGoogle} disabled={loading}>
        <svg viewBox="0 0 24 24" width="18" height="18"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
        Continue with Google
      </button>
    </div>

    <div class="divider">
      <span>or</span>
    </div>

    <form onsubmit={(e) => { e.preventDefault(); signInWithEmail(); }}>
      <input
        class="email-input"
        type="email"
        placeholder="Enter your email"
        bind:value={email}
        disabled={loading}
      />
      <button class="email-btn" type="submit" disabled={loading || !email.trim()}>
        {loading ? 'Sending...' : 'Send Magic Link'}
      </button>
    </form>

    {#if message}
      <p class="message">{message}</p>
    {/if}
  </div>
</div>

<style>
  .login-page {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    background: var(--bg-base);
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 20%, rgba(59, 130, 246, 0.06) 0%, transparent 50%),
      radial-gradient(ellipse at 50% 80%, rgba(168, 85, 247, 0.05) 0%, transparent 50%);
  }

  .login-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    max-width: 400px;
    padding: 40px 32px;
    border-radius: var(--radius-xl);
    animation: windowIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .login-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 16px;
    background: var(--accent-subtle);
    color: var(--accent-glow);
    margin-bottom: 20px;
  }

  .login-title {
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-glow), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 6px;
  }

  .login-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 28px;
  }

  .oauth-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }

  .oauth-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    padding: 11px 16px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 14px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .oauth-btn:hover:not(:disabled) {
    background: var(--bg-surface-hover);
    border-color: var(--border-subtle);
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.1);
  }

  .oauth-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .divider {
    display: flex;
    align-items: center;
    width: 100%;
    margin: 20px 0;
    gap: 12px;
  }

  .divider::before,
  .divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border-subtle);
  }

  .divider span {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }

  .email-input {
    width: 100%;
    padding: 11px 14px;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    background: var(--bg-surface);
    color: var(--text-primary);
    font-size: 14px;
    font-family: inherit;
    outline: none;
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  }

  .email-input::placeholder {
    color: var(--text-muted);
  }

  .email-input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-subtle);
  }

  .email-input:disabled {
    opacity: 0.5;
  }

  .email-btn {
    width: 100%;
    padding: 11px 16px;
    border: none;
    border-radius: var(--radius-md);
    background: var(--accent);
    color: white;
    font-size: 14px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .email-btn:hover:not(:disabled) {
    background: var(--accent-glow);
    box-shadow: var(--shadow-glow);
  }

  .email-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .message {
    margin-top: 16px;
    font-size: 13px;
    color: var(--accent-glow);
    text-align: center;
  }
</style>
