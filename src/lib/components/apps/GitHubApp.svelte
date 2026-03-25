<script lang="ts">
  import { Github, ExternalLink, Star, GitFork, Circle, AlertCircle, Tag, RefreshCw, LogOut, GitPullRequest, Loader2 } from 'lucide-svelte';
  import { integrationsStore } from '$lib/stores/integrations.svelte';

  interface Repo {
    id: number;
    name: string;
    full_name: string;
    description: string | null;
    html_url: string;
    language: string | null;
    stargazers_count: number;
    forks_count: number;
    open_issues_count: number;
    private: boolean;
    updated_at: string;
    default_branch: string;
  }

  interface Issue {
    id: number;
    number: number;
    title: string;
    state: string;
    html_url: string;
    repository?: string;
    created_at: string;
    updated_at: string;
    labels: Array<{ name: string; color: string }>;
    user?: { login: string; avatar_url: string };
    pull_request?: boolean;
  }

  let activeTab = $state<'repos' | 'issues' | 'prs'>('repos');
  let repos = $state<Repo[]>([]);
  let issues = $state<Issue[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let needsAuth = $state(false);

  let connected = $derived(integrationsStore.isConnected('github'));
  let ghUser = $derived(integrationsStore.getIntegration('github'));

  let filteredIssues = $derived(issues.filter(i => !i.pull_request));
  let filteredPRs = $derived(issues.filter(i => i.pull_request));

  const langColors: Record<string, string> = {
    TypeScript: '#3178c6', JavaScript: '#f1e05a', Python: '#3572A5', Rust: '#dea584',
    Go: '#00ADD8', Java: '#b07219', Ruby: '#701516', Swift: '#F05138',
    'C++': '#f34b7d', C: '#555555', 'C#': '#178600', PHP: '#4F5D95',
    Kotlin: '#A97BFF', Dart: '#00B4AB', Shell: '#89e051', HTML: '#e34c26',
    CSS: '#563d7c', Vue: '#41b883', Svelte: '#ff3e00',
  };

  $effect(() => {
    if (connected && repos.length === 0 && !loading) {
      fetchRepos();
    }
  });

  async function fetchRepos() {
    loading = true;
    error = null;
    try {
      const resp = await fetch('/api/integrations/github/repos');
      const data = await resp.json();
      if (!resp.ok) {
        if (data.needsAuth) { needsAuth = true; return; }
        throw new Error(data.error || 'Failed to fetch repos');
      }
      repos = data.repos;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function fetchIssues() {
    loading = true;
    error = null;
    try {
      const resp = await fetch('/api/integrations/github/issues');
      const data = await resp.json();
      if (!resp.ok) {
        if (data.needsAuth) { needsAuth = true; return; }
        throw new Error(data.error || 'Failed to fetch issues');
      }
      issues = data.issues;
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleTabChange(tab: 'repos' | 'issues' | 'prs') {
    activeTab = tab;
    if ((tab === 'issues' || tab === 'prs') && issues.length === 0) {
      fetchIssues();
    }
  }

  function handleRefresh() {
    if (activeTab === 'repos') fetchRepos();
    else fetchIssues();
  }

  async function handleDisconnect() {
    await integrationsStore.disconnect('github');
    repos = [];
    issues = [];
    needsAuth = false;
  }

  function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 30) return `${days}d ago`;
    return `${Math.floor(days / 30)}mo ago`;
  }
</script>

<div class="github-layout">
  {#if !connected || needsAuth}
    <div class="connect-screen">
      <div class="connect-card">
        <div class="connect-icon">
          <Github size={48} strokeWidth={1.2} />
        </div>
        <h3>Connect GitHub</h3>
        <p>Link your GitHub account to view repos, issues, and pull requests directly in Elysium.</p>
        <a href="/api/integrations/github/connect" class="connect-btn">
          <Github size={18} />
          Connect with GitHub
        </a>
        {#if needsAuth}
          <p class="reconnect-notice">Your GitHub token has expired. Please reconnect.</p>
        {/if}
      </div>
    </div>
  {:else}
    <div class="header">
      <div class="header-left">
        {#if ghUser?.avatar_url}
          <img src={ghUser.avatar_url} alt={ghUser.username} class="avatar" />
        {/if}
        <span class="username">{ghUser?.username || 'GitHub'}</span>
        <span class="connected-badge">Connected</span>
      </div>
      <div class="header-actions">
        <button class="icon-btn" onclick={handleRefresh} aria-label="Refresh" disabled={loading}>
          <RefreshCw size={14} class={loading ? 'spinning' : ''} />
        </button>
        <button class="icon-btn disconnect" onclick={handleDisconnect} aria-label="Disconnect">
          <LogOut size={14} />
        </button>
      </div>
    </div>

    <div class="tabs">
      <button class="tab" class:active={activeTab === 'repos'} onclick={() => handleTabChange('repos')}>
        <Github size={14} />
        Repos
      </button>
      <button class="tab" class:active={activeTab === 'issues'} onclick={() => handleTabChange('issues')}>
        <Circle size={14} />
        Issues
      </button>
      <button class="tab" class:active={activeTab === 'prs'} onclick={() => handleTabChange('prs')}>
        <GitPullRequest size={14} />
        Pull Requests
      </button>
    </div>

    <div class="content scrollbar-thin">
      {#if loading}
        <div class="loading-state">
          <Loader2 size={24} class="spinning" />
          <span>Loading...</span>
        </div>
      {:else if error}
        <div class="error-state">
          <AlertCircle size={20} />
          <span>{error}</span>
          <button class="retry-btn" onclick={handleRefresh}>Retry</button>
        </div>
      {:else if activeTab === 'repos'}
        {#if repos.length === 0}
          <div class="empty-state">No repositories found.</div>
        {:else}
          {#each repos as repo}
            <a href={repo.html_url} target="_blank" rel="noopener noreferrer" class="repo-item">
              <div class="repo-main">
                <div class="repo-name-row">
                  <span class="repo-name">{repo.name}</span>
                  {#if repo.private}
                    <span class="visibility-badge private">Private</span>
                  {:else}
                    <span class="visibility-badge public">Public</span>
                  {/if}
                  <ExternalLink size={12} class="external-icon" />
                </div>
                {#if repo.description}
                  <p class="repo-desc">{repo.description}</p>
                {/if}
                <div class="repo-meta">
                  {#if repo.language}
                    <span class="lang-badge">
                      <span class="lang-dot" style="background: {langColors[repo.language] || '#8b949e'}"></span>
                      {repo.language}
                    </span>
                  {/if}
                  <span class="meta-item">
                    <Star size={12} />
                    {repo.stargazers_count}
                  </span>
                  <span class="meta-item">
                    <GitFork size={12} />
                    {repo.forks_count}
                  </span>
                  <span class="meta-item updated">Updated {timeAgo(repo.updated_at)}</span>
                </div>
              </div>
            </a>
          {/each}
        {/if}
      {:else if activeTab === 'issues'}
        {#if filteredIssues.length === 0}
          <div class="empty-state">No open issues assigned to you.</div>
        {:else}
          {#each filteredIssues as issue}
            <a href={issue.html_url} target="_blank" rel="noopener noreferrer" class="issue-item">
              <div class="issue-icon open">
                <Circle size={14} />
              </div>
              <div class="issue-main">
                <div class="issue-title-row">
                  <span class="issue-title">{issue.title}</span>
                  <ExternalLink size={12} class="external-icon" />
                </div>
                <div class="issue-meta">
                  {#if issue.repository}
                    <span class="issue-repo">{issue.repository}</span>
                  {/if}
                  <span class="issue-number">#{issue.number}</span>
                  <span class="issue-time">{timeAgo(issue.updated_at)}</span>
                </div>
                {#if issue.labels.length > 0}
                  <div class="label-list">
                    {#each issue.labels as label}
                      <span class="label" style="background: #{label.color}20; color: #{label.color}; border-color: #{label.color}40">
                        {label.name}
                      </span>
                    {/each}
                  </div>
                {/if}
              </div>
            </a>
          {/each}
        {/if}
      {:else if activeTab === 'prs'}
        {#if filteredPRs.length === 0}
          <div class="empty-state">No open pull requests found.</div>
        {:else}
          {#each filteredPRs as pr}
            <a href={pr.html_url} target="_blank" rel="noopener noreferrer" class="issue-item">
              <div class="issue-icon pr">
                <GitPullRequest size={14} />
              </div>
              <div class="issue-main">
                <div class="issue-title-row">
                  <span class="issue-title">{pr.title}</span>
                  <ExternalLink size={12} class="external-icon" />
                </div>
                <div class="issue-meta">
                  {#if pr.repository}
                    <span class="issue-repo">{pr.repository}</span>
                  {/if}
                  <span class="issue-number">#{pr.number}</span>
                  <span class="issue-time">{timeAgo(pr.updated_at)}</span>
                </div>
                {#if pr.labels.length > 0}
                  <div class="label-list">
                    {#each pr.labels as label}
                      <span class="label" style="background: #{label.color}20; color: #{label.color}; border-color: #{label.color}40">
                        {label.name}
                      </span>
                    {/each}
                  </div>
                {/if}
              </div>
            </a>
          {/each}
        {/if}
      {/if}
    </div>
  {/if}
</div>

<style>
  .github-layout {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  .connect-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 24px;
  }

  .connect-card {
    text-align: center;
    max-width: 380px;
  }

  .connect-icon {
    color: var(--text-muted);
    margin-bottom: 16px;
  }

  .connect-card h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .connect-card p {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 20px;
  }

  .connect-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 24px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    transition: all var(--transition-fast);
  }

  .connect-btn:hover {
    background: var(--accent-glow);
    box-shadow: var(--shadow-glow);
  }

  .reconnect-notice {
    margin-top: 12px;
    font-size: 12px;
    color: #f59e0b;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1px solid var(--border-subtle);
  }

  .username {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .connected-badge {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 10px;
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    font-weight: 500;
  }

  .header-actions {
    display: flex;
    gap: 4px;
  }

  .icon-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
  }

  .icon-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .icon-btn.disconnect:hover {
    color: #ef4444;
  }

  .icon-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .tabs {
    display: flex;
    gap: 0;
    padding: 0 16px;
    border-bottom: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .tab {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 16px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-size: 13px;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all var(--transition-fast);
    margin-bottom: -1px;
  }

  .tab:hover {
    color: var(--text-secondary);
  }

  .tab.active {
    color: var(--accent-glow);
    border-bottom-color: var(--accent);
  }

  .content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
  }

  .loading-state,
  .error-state,
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 48px 24px;
    color: var(--text-muted);
    font-size: 13px;
  }

  .error-state {
    flex-direction: column;
    color: #ef4444;
  }

  .retry-btn {
    margin-top: 8px;
    padding: 6px 16px;
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    font-size: 12px;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .retry-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .repo-item {
    display: block;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
    text-decoration: none;
    transition: background var(--transition-fast);
  }

  .repo-item:hover {
    background: var(--bg-surface-hover);
  }

  .repo-name-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }

  .repo-name {
    font-size: 14px;
    font-weight: 600;
    color: var(--accent-glow);
  }

  :global(.external-icon) {
    color: var(--text-muted);
    opacity: 0;
    transition: opacity var(--transition-fast);
  }

  .repo-item:hover :global(.external-icon),
  .issue-item:hover :global(.external-icon) {
    opacity: 1;
  }

  .visibility-badge {
    font-size: 10px;
    padding: 1px 6px;
    border-radius: 10px;
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    font-weight: 500;
  }

  .repo-desc {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.4;
    margin-bottom: 8px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .repo-meta {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
  }

  .lang-badge {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--text-secondary);
  }

  .lang-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: var(--text-muted);
  }

  .meta-item.updated {
    margin-left: auto;
  }

  .issue-item {
    display: flex;
    gap: 10px;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-subtle);
    text-decoration: none;
    transition: background var(--transition-fast);
    align-items: flex-start;
  }

  .issue-item:hover {
    background: var(--bg-surface-hover);
  }

  .issue-icon {
    flex-shrink: 0;
    margin-top: 2px;
  }

  .issue-icon.open {
    color: #10b981;
  }

  .issue-icon.pr {
    color: var(--accent-glow);
  }

  .issue-main {
    min-width: 0;
    flex: 1;
  }

  .issue-title-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }

  .issue-title {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .issue-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }

  .issue-repo {
    color: var(--text-secondary);
    font-weight: 500;
  }

  .label-list {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .label {
    font-size: 10px;
    padding: 1px 6px;
    border-radius: 10px;
    border: 1px solid;
    font-weight: 500;
  }

  :global(.spinning) {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
