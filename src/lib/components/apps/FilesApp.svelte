<script lang="ts">
  import { Search, LayoutGrid, List, FileText, File, Upload, Trash2, ChevronRight, X } from 'lucide-svelte';

  interface UploadedFile {
    id: string;
    name: string;
    size: number;
    type: string;
    uploadedAt: string;
    chunkCount: number;
  }

  let viewMode = $state<'grid' | 'list'>('grid');
  let searchQuery = $state('');
  let files = $state<UploadedFile[]>([]);
  let selectedFile = $state<(UploadedFile & { content?: string }) | null>(null);
  let isUploading = $state(false);
  let dragOver = $state(false);
  let previewOpen = $state(false);

  const ALLOWED_EXTENSIONS = ['.txt', '.md', '.json', '.csv', '.js', '.ts', '.py', '.html', '.css', '.xml', '.yaml', '.yml', '.toml', '.sh', '.sql', '.svelte'];

  async function loadFiles() {
    try {
      const res = await fetch('/api/files');
      const data = await res.json();
      files = data.files ?? [];
    } catch {}
  }

  async function uploadFile(file: globalThis.File) {
    isUploading = true;
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/files', { method: 'POST', body: formData });
      if (res.ok) await loadFiles();
    } catch {}
    isUploading = false;
  }

  async function deleteFile(id: string, e?: MouseEvent) {
    if (e) e.stopPropagation();
    try {
      await fetch(`/api/files/${id}`, { method: 'DELETE' });
      if (selectedFile?.id === id) {
        selectedFile = null;
        previewOpen = false;
      }
      await loadFiles();
    } catch {}
  }

  async function previewFile(file: UploadedFile) {
    try {
      const res = await fetch(`/api/files/${file.id}`);
      const data = await res.json();
      selectedFile = { ...file, content: data.content };
      previewOpen = true;
    } catch {
      selectedFile = file;
      previewOpen = true;
    }
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;
    const droppedFiles = e.dataTransfer?.files;
    if (droppedFiles) {
      for (const file of droppedFiles) {
        uploadFile(file);
      }
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragOver = true;
  }

  function handleDragLeave() {
    dragOver = false;
  }

  function handleFileInput(e: Event) {
    const input = e.target as HTMLInputElement;
    if (input.files) {
      for (const file of input.files) {
        uploadFile(file);
      }
      input.value = '';
    }
  }

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function getFileIcon(name: string) {
    const ext = name.split('.').pop()?.toLowerCase();
    if (['md', 'txt', 'csv'].includes(ext ?? '')) return FileText;
    return File;
  }

  let filteredFiles = $derived(
    searchQuery
      ? files.filter(f => f.name.toLowerCase().includes(searchQuery.toLowerCase()))
      : files
  );

  $effect(() => {
    loadFiles();
  });
</script>

<div class="files-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Files</span>
    </div>
    <div class="sidebar-info">
      <div class="stat-row">
        <span class="stat-label">Total Files</span>
        <span class="stat-value">{files.length}</span>
      </div>
      <div class="stat-row">
        <span class="stat-label">Total Size</span>
        <span class="stat-value">{formatSize(files.reduce((sum, f) => sum + f.size, 0))}</span>
      </div>
    </div>
    <div class="sidebar-upload">
      <label
        class="upload-zone"
        class:drag-over={dragOver}
        ondrop={handleDrop}
        ondragover={handleDragOver}
        ondragleave={handleDragLeave}
      >
        <Upload size={18} />
        <span>{isUploading ? 'Uploading...' : 'Drop or Browse'}</span>
        <input type="file" accept={ALLOWED_EXTENSIONS.join(',')} multiple onchange={handleFileInput} hidden />
      </label>
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
      <span class="current">Uploads</span>
      <span class="file-total">{filteredFiles.length} files</span>
    </div>

    {#if previewOpen && selectedFile}
      <div class="preview-panel">
        <div class="preview-bar">
          <span class="preview-filename">{selectedFile.name}</span>
          <button class="preview-close" onclick={() => (previewOpen = false)}>
            <X size={14} />
          </button>
        </div>
        <pre class="preview-content scrollbar-thin">{selectedFile.content ?? 'Loading...'}</pre>
      </div>
    {:else}
      <div class="file-area scrollbar-thin" class:grid-view={viewMode === 'grid'} class:list-view={viewMode === 'list'}>
        {#if filteredFiles.length === 0}
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <div
            class="empty-state"
            class:drag-over={dragOver}
            ondrop={handleDrop}
            ondragover={handleDragOver}
            ondragleave={handleDragLeave}
          >
            <Upload size={32} strokeWidth={1} />
            <p>{files.length === 0 ? 'No files uploaded yet. Drop files here or use the upload button.' : 'No files match your search.'}</p>
          </div>
        {:else}
          {#each filteredFiles as file}
            {@const IconComp = getFileIcon(file.name)}
            {#if viewMode === 'grid'}
              <!-- svelte-ignore a11y_no_static_element_interactions -->
              <!-- svelte-ignore a11y_click_events_have_key_events -->
              <div class="file-card" onclick={() => previewFile(file)}>
                <div class="file-icon">
                  <IconComp size={24} strokeWidth={1.5} />
                </div>
                <span class="file-name">{file.name}</span>
                <span class="file-size">{formatSize(file.size)}</span>
                <div class="file-actions">
                  <button class="action-btn" onclick={(e) => { e.stopPropagation(); deleteFile(file.id); }} aria-label="Delete">
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            {:else}
              <!-- svelte-ignore a11y_no_static_element_interactions -->
              <!-- svelte-ignore a11y_click_events_have_key_events -->
              <div class="file-row" onclick={() => previewFile(file)}>
                <div class="file-row-icon">
                  <IconComp size={16} strokeWidth={1.5} />
                </div>
                <span class="file-row-name">{file.name}</span>
                <span class="file-row-size">{formatSize(file.size)}</span>
                <span class="file-row-date">{formatDate(file.uploadedAt)}</span>
                <button class="action-btn" onclick={(e) => { e.stopPropagation(); deleteFile(file.id); }} aria-label="Delete">
                  <Trash2 size={12} />
                </button>
              </div>
            {/if}
          {/each}
        {/if}
      </div>
    {/if}
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
    display: flex;
    flex-direction: column;
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

  .sidebar-info {
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
  }

  .stat-label {
    color: var(--text-muted);
  }

  .stat-value {
    color: var(--text-primary);
    font-weight: 500;
  }

  .sidebar-upload {
    padding: 8px 12px;
    margin-top: auto;
    border-top: 1px solid var(--border-subtle);
  }

  .upload-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 16px;
    border: 2px dashed var(--border-subtle);
    border-radius: var(--radius-sm);
    cursor: pointer;
    color: var(--text-muted);
    font-size: 12px;
    transition: all var(--transition-fast);
    text-align: center;
  }

  .upload-zone:hover,
  .upload-zone.drag-over {
    border-color: var(--accent);
    color: var(--accent-glow);
    background: var(--accent-subtle);
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

  .file-total {
    margin-left: auto;
    font-size: 11px;
    color: var(--text-muted);
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

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    height: 100%;
    color: var(--text-muted);
    text-align: center;
    font-size: 13px;
    border: 2px dashed transparent;
    border-radius: var(--radius-lg);
    padding: 40px;
    transition: all var(--transition-fast);
    grid-column: 1 / -1;
  }

  .empty-state.drag-over {
    border-color: var(--accent);
    background: var(--accent-subtle);
  }

  .file-card {
    position: relative;
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
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: 100%;
  }

  .file-size {
    font-size: 10px;
    color: var(--text-muted);
  }

  .file-actions {
    position: absolute;
    top: 4px;
    right: 4px;
    opacity: 0;
    transition: opacity var(--transition-fast);
  }

  .file-card:hover .file-actions {
    opacity: 1;
  }

  .action-btn {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: rgba(0, 0, 0, 0.5);
    color: var(--text-muted);
    cursor: pointer;
    border-radius: 4px;
    transition: all var(--transition-fast);
  }

  .action-btn:hover {
    color: #f43f5e;
    background: rgba(244, 63, 94, 0.15);
  }

  .file-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px 12px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast);
    text-align: left;
  }

  .file-row:hover {
    background: var(--bg-surface-hover);
  }

  .file-row-icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-glow);
    flex-shrink: 0;
  }

  .file-row-name {
    flex: 1;
    font-size: 13px;
    color: var(--text-primary);
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

  .file-row .action-btn {
    opacity: 0;
    flex-shrink: 0;
  }

  .file-row:hover .action-btn {
    opacity: 1;
  }

  .preview-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .preview-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    border-bottom: 1px solid var(--border-subtle);
    background: var(--bg-surface);
  }

  .preview-filename {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
  }

  .preview-close {
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    transition: all var(--transition-fast);
  }

  .preview-close:hover {
    background: var(--bg-surface-hover);
    color: var(--text-primary);
  }

  .preview-content {
    flex: 1;
    margin: 0;
    padding: 16px;
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
    overflow-y: auto;
  }
</style>
