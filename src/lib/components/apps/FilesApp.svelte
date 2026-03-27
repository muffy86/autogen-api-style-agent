<script lang="ts">
  import { Search, LayoutGrid, List, FileText, Image, File, FolderOpen, ChevronRight } from 'lucide-svelte';

  let viewMode = $state<'grid' | 'list'>('grid');
  let selectedFolder = $state('Documents');
  let searchQuery = $state('');

  const folders = [
    { name: 'Documents', count: 12 },
    { name: 'Downloads', count: 8 },
    { name: 'Knowledge Base', count: 24 },
    { name: 'Uploads', count: 5 }
  ];

  const files = [
    { name: 'Project Proposal.pdf', type: 'pdf', size: '2.4 MB', modified: 'Mar 15, 2026' },
    { name: 'Architecture Notes.md', type: 'md', size: '18 KB', modified: 'Mar 14, 2026' },
    { name: 'Meeting Summary.txt', type: 'txt', size: '4.2 KB', modified: 'Mar 13, 2026' },
    { name: 'System Diagram.png', type: 'img', size: '1.1 MB', modified: 'Mar 12, 2026' },
    { name: 'API Reference.pdf', type: 'pdf', size: '856 KB', modified: 'Mar 11, 2026' },
    { name: 'Training Data.csv', type: 'txt', size: '12.3 MB', modified: 'Mar 10, 2026' },
    { name: 'Dashboard Mock.png', type: 'img', size: '2.8 MB', modified: 'Mar 9, 2026' },
    { name: 'Release Notes.md', type: 'md', size: '7.1 KB', modified: 'Mar 8, 2026' }
  ];

  const iconMap = {
    pdf: FileText,
    md: File,
    txt: File,
    img: Image
  };
</script>

<div class="files-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Folders</span>
    </div>
    <div class="folder-list">
      {#each folders as folder}
        <button
          class="folder-item"
          class:active={selectedFolder === folder.name}
          onclick={() => (selectedFolder = folder.name)}
        >
          <FolderOpen size={14} />
          <span>{folder.name}</span>
          <span class="folder-count">{folder.count}</span>
        </button>
      {/each}
    </div>
  </div>
  <div class="main">
    <div class="dev-banner">
      <span>📁 File management is under development — showing sample data</span>
    </div>
    <div class="toolbar">
      <div class="search-box">
        <Search size={14} />
        <input type="text" placeholder="Search files..." bind:value={searchQuery} />
      </div>
      <div class="toolbar-actions">
        <button
          class="view-btn"
          class:active={viewMode === 'grid'}
          onclick={() => (viewMode = 'grid')}
          aria-label="Grid view"
        >
          <LayoutGrid size={14} />
        </button>
        <button
          class="view-btn"
          class:active={viewMode === 'list'}
          onclick={() => (viewMode = 'list')}
          aria-label="List view"
        >
          <List size={14} />
        </button>
      </div>
    </div>
    <div class="breadcrumb">
      <span>Home</span>
      <ChevronRight size={12} />
      <span class="current">{selectedFolder}</span>
    </div>
    <div class="file-area scrollbar-thin" class:grid-view={viewMode === 'grid'} class:list-view={viewMode === 'list'}>
      {#each files as file}
        {@const IconComp = iconMap[file.type as keyof typeof iconMap] ?? File}
        {#if viewMode === 'grid'}
          <button class="file-card">
            <div class="file-icon">
              <IconComp size={24} strokeWidth={1.5} />
            </div>
            <span class="file-name">{file.name}</span>
            <span class="file-size">{file.size}</span>
          </button>
        {:else}
          <button class="file-row">
            <div class="file-row-icon">
              <IconComp size={16} strokeWidth={1.5} />
            </div>
            <span class="file-row-name">{file.name}</span>
            <span class="file-row-size">{file.size}</span>
            <span class="file-row-date">{file.modified}</span>
          </button>
        {/if}
      {/each}
    </div>
  </div>
</div>

<style>
  .files-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: 200px;
    border-right: 1px solid var(--border-subtle);
    flex-shrink: 0;
  }

  .sidebar-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
  }

  .sidebar-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .folder-list {
    padding: 4px;
  }

  .folder-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 13px;
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    text-align: left;
  }

  .folder-item:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .folder-item.active {
    background: var(--accent-subtle);
    color: var(--accent-glow);
  }

  .folder-count {
    margin-left: auto;
    font-size: 11px;
    color: var(--text-muted);
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .dev-banner {
    padding: 6px 16px;
    background: rgba(245, 158, 11, 0.1);
    border-bottom: 1px solid rgba(245, 158, 11, 0.2);
    font-size: 11px;
    color: #f59e0b;
    text-align: center;
  }

  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    border-bottom: 1px solid var(--border-subtle);
    gap: 12px;
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 10px;
    height: 32px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-subtle);
    background: var(--bg-surface);
    color: var(--text-muted);
    flex: 1;
    max-width: 300px;
  }

  .search-box input {
    flex: 1;
    border: none;
    background: transparent;
    color: var(--text-primary);
    font-size: 12px;
    outline: none;
  }

  .search-box input::placeholder {
    color: var(--text-muted);
  }

  .toolbar-actions {
    display: flex;
    gap: 2px;
  }

  .view-btn {
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

  .view-btn:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .view-btn.active {
    background: var(--accent-subtle);
    color: var(--accent-glow);
  }

  .breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    font-size: 12px;
    color: var(--text-muted);
  }

  .breadcrumb .current {
    color: var(--text-primary);
  }

  .file-area {
    flex: 1;
    overflow-y: auto;
    padding: 12px 16px;
  }

  .file-area.grid-view {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 8px;
    align-content: start;
  }

  .file-area.list-view {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .file-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 16px 8px;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    background: transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    text-align: center;
  }

  .file-card:hover {
    background: var(--bg-surface-hover);
    border-color: var(--border-subtle);
  }

  .file-icon {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-glow);
    background: var(--accent-subtle);
    border-radius: var(--radius-sm);
  }

  .file-name {
    font-size: 11px;
    color: var(--text-primary);
    word-break: break-all;
    line-height: 1.3;
  }

  .file-size {
    font-size: 10px;
    color: var(--text-muted);
  }

  .file-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    border: none;
    background: transparent;
    cursor: pointer;
    transition: background var(--transition-fast);
    width: 100%;
    text-align: left;
  }

  .file-row:hover {
    background: var(--bg-surface-hover);
  }

  .file-row-icon {
    color: var(--accent-glow);
    flex-shrink: 0;
  }

  .file-row-name {
    font-size: 13px;
    color: var(--text-primary);
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-row-size {
    font-size: 12px;
    color: var(--text-muted);
    width: 80px;
    text-align: right;
    flex-shrink: 0;
  }

  .file-row-date {
    font-size: 12px;
    color: var(--text-muted);
    width: 100px;
    text-align: right;
    flex-shrink: 0;
  }
</style>
