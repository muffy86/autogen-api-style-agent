<script lang="ts">
  import { Upload, Trash2, Search, FileText, Database, X } from 'lucide-svelte';

  interface UploadedFile {
    id: string;
    name: string;
    size: number;
    type: string;
    uploadedAt: string;
    chunkCount: number;
  }

  interface SearchResult {
    content: string;
    fileName: string;
    score: number;
  }

  let files = $state<UploadedFile[]>([]);
  let selectedFile = $state<(UploadedFile & { content?: string }) | null>(null);
  let searchQuery = $state('');
  let searchResults = $state<SearchResult[]>([]);
  let isSearching = $state(false);
  let isUploading = $state(false);
  let uploadProgress = $state(0);
  let dragOver = $state(false);
  let errorMsg = $state('');

  const ALLOWED_EXTENSIONS = ['.txt', '.md', '.json', '.csv', '.js', '.ts', '.py', '.html', '.css', '.xml', '.yaml', '.yml', '.toml', '.sh', '.sql', '.svelte'];

  async function loadFiles() {
    try {
      const res = await fetch('/api/files');
      const data = await res.json();
      files = data.files ?? [];
    } catch {}
  }

  async function uploadFile(file: globalThis.File) {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      errorMsg = `Unsupported file type: ${ext}`;
      setTimeout(() => (errorMsg = ''), 3000);
      return;
    }

    isUploading = true;
    uploadProgress = 0;
    errorMsg = '';

    const interval = setInterval(() => {
      uploadProgress = Math.min(uploadProgress + 15, 90);
    }, 100);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('/api/files', { method: 'POST', body: formData });
      const data = await res.json();

      if (!res.ok) {
        errorMsg = data.error || 'Upload failed';
        setTimeout(() => (errorMsg = ''), 3000);
        return;
      }

      uploadProgress = 100;
      await loadFiles();
    } catch (e: any) {
      errorMsg = e.message || 'Upload failed';
      setTimeout(() => (errorMsg = ''), 3000);
    } finally {
      clearInterval(interval);
      setTimeout(() => {
        isUploading = false;
        uploadProgress = 0;
      }, 500);
    }
  }

  async function deleteFile(id: string) {
    try {
      await fetch(`/api/files/${id}`, { method: 'DELETE' });
      if (selectedFile?.id === id) selectedFile = null;
      await loadFiles();
    } catch {}
  }

  async function selectFile(file: UploadedFile) {
    try {
      const res = await fetch(`/api/files/${file.id}`);
      const data = await res.json();
      selectedFile = { ...file, content: data.content };
    } catch {
      selectedFile = file;
    }
  }

  async function handleSearch() {
    if (!searchQuery.trim()) {
      searchResults = [];
      return;
    }
    isSearching = true;
    try {
      const res = await fetch(`/api/files/search?q=${encodeURIComponent(searchQuery)}`);
      if (res.ok) {
        const data = await res.json();
        searchResults = data.results ?? [];
      } else {
        searchResults = [];
      }
    } catch {
      searchResults = [];
    }
    isSearching = false;
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

  $effect(() => {
    loadFiles();
  });
</script>

<div class="knowledge-layout">
  <div class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">Documents</span>
      <span class="file-count">{files.length}</span>
    </div>
    <div class="file-list scrollbar-thin">
      {#if files.length === 0}
        <div class="empty-sidebar">
          <FileText size={20} />
          <span>No documents yet</span>
        </div>
      {:else}
        {#each files as file}
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <!-- svelte-ignore a11y_click_events_have_key_events -->
          <div
            class="file-item"
            class:active={selectedFile?.id === file.id}
            onclick={() => selectFile(file)}
          >
            <div class="file-item-icon">
              <FileText size={14} />
            </div>
            <div class="file-item-info">
              <span class="file-item-name">{file.name}</span>
              <span class="file-item-meta">{formatSize(file.size)} &middot; {file.chunkCount} chunks</span>
            </div>
            <button
              class="file-delete-btn"
              onclick={(e) => { e.stopPropagation(); deleteFile(file.id); }}
              aria-label="Delete file"
            >
              <Trash2 size={12} />
            </button>
          </div>
        {/each}
      {/if}
    </div>
  </div>

  <div class="main">
    <div class="toolbar">
      <div class="search-box">
        <Search size={14} />
        <input
          type="text"
          placeholder="Search knowledge base..."
          bind:value={searchQuery}
          onkeydown={(e) => { if (e.key === 'Enter') handleSearch(); }}
        />
        {#if searchQuery}
          <button class="clear-search" onclick={() => { searchQuery = ''; searchResults = []; }}>
            <X size={12} />
          </button>
        {/if}
      </div>
      <label class="upload-btn">
        <Upload size={14} />
        <span>Upload</span>
        <input type="file" accept={ALLOWED_EXTENSIONS.join(',')} multiple onchange={handleFileInput} hidden />
      </label>
    </div>

    {#if errorMsg}
      <div class="error-bar">{errorMsg}</div>
    {/if}

    {#if isUploading}
      <div class="upload-progress">
        <div class="progress-bar" style="width: {uploadProgress}%"></div>
        <span class="progress-text">Uploading... {uploadProgress}%</span>
      </div>
    {/if}

    <div class="content-area scrollbar-thin">
      {#if searchResults.length > 0}
        <div class="search-results">
          <h4 class="results-title">Search Results for "{searchQuery}"</h4>
          {#each searchResults as result, i}
            <div class="result-card">
              <div class="result-header">
                <span class="result-file">{result.fileName}</span>
                <span class="result-score">{(result.score * 100).toFixed(1)}% match</span>
              </div>
              <p class="result-content">{result.content}</p>
            </div>
          {/each}
        </div>
      {:else if selectedFile}
        <div class="file-preview">
          <div class="preview-header">
            <FileText size={18} />
            <div class="preview-meta">
              <h4 class="preview-name">{selectedFile.name}</h4>
              <span class="preview-info">{formatSize(selectedFile.size)} &middot; {selectedFile.chunkCount} chunks &middot; {formatDate(selectedFile.uploadedAt)}</span>
            </div>
          </div>
          {#if selectedFile.content}
            <pre class="preview-content scrollbar-thin">{selectedFile.content}</pre>
          {:else}
            <p class="preview-loading">Loading content...</p>
          {/if}
        </div>
      {:else}
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
          class="drop-zone"
          class:drag-over={dragOver}
          ondrop={handleDrop}
          ondragover={handleDragOver}
          ondragleave={handleDragLeave}
        >
          <div class="drop-icon">
            <Database size={40} strokeWidth={1} />
          </div>
          <h3 class="drop-title">Drop files here to build your knowledge base</h3>
          <p class="drop-desc">Upload text files and the AI will index them for smart retrieval. Supports: {ALLOWED_EXTENSIONS.slice(0, 6).join(', ')}, and more.</p>
          <label class="drop-browse">
            <span>Browse Files</span>
            <input type="file" accept={ALLOWED_EXTENSIONS.join(',')} multiple onchange={handleFileInput} hidden />
          </label>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .knowledge-layout {
    display: flex;
    height: 100%;
  }

  .sidebar {
    width: 240px;
    border-right: 1px solid var(--border-subtle);
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
  }

  .sidebar-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .sidebar-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
  }

  .file-count {
    font-size: 11px;
    color: var(--text-muted);
    background: var(--bg-surface-hover);
    padding: 1px 7px;
    border-radius: 10px;
  }

  .file-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px;
  }

  .empty-sidebar {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 32px 16px;
    color: var(--text-muted);
    font-size: 12px;
  }

  .file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 10px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition-fast);
    text-align: left;
  }

  .file-item:hover {
    background: var(--bg-surface-hover);
  }

  .file-item.active {
    background: var(--accent-subtle);
  }

  .file-item-icon {
    color: var(--accent-glow);
    flex-shrink: 0;
  }

  .file-item-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 1px;
  }

  .file-item-name {
    font-size: 12px;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-item-meta {
    font-size: 10px;
    color: var(--text-muted);
  }

  .file-delete-btn {
    opacity: 0;
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all var(--transition-fast);
    flex-shrink: 0;
  }

  .file-item:hover .file-delete-btn {
    opacity: 1;
  }

  .file-delete-btn:hover {
    color: #f43f5e;
    background: rgba(244, 63, 94, 0.1);
  }

  .main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-bottom: 1px solid var(--border-subtle);
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

  .clear-search {
    border: none;
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    padding: 2px;
    display: flex;
  }

  .upload-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 14px;
    height: 32px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--accent);
    background: var(--accent-subtle);
    color: var(--accent-glow);
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    transition: all var(--transition-fast);
    white-space: nowrap;
  }

  .upload-btn:hover {
    background: rgba(139, 92, 246, 0.25);
  }

  .error-bar {
    padding: 8px 16px;
    background: rgba(244, 63, 94, 0.1);
    border-bottom: 1px solid rgba(244, 63, 94, 0.2);
    color: #f43f5e;
    font-size: 12px;
  }

  .upload-progress {
    position: relative;
    height: 24px;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border-subtle);
    overflow: hidden;
  }

  .progress-bar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background: linear-gradient(90deg, var(--accent-subtle), rgba(139, 92, 246, 0.3));
    transition: width 0.2s ease;
  }

  .progress-text {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 16px;
    font-size: 11px;
    color: var(--text-secondary);
  }

  .content-area {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .drop-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    border: 2px dashed var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 40px;
    text-align: center;
    transition: all var(--transition-smooth);
  }

  .drop-zone.drag-over {
    border-color: var(--accent);
    background: var(--accent-subtle);
  }

  .drop-icon {
    color: var(--text-muted);
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .drag-over .drop-icon {
    color: var(--accent-glow);
    opacity: 1;
  }

  .drop-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .drop-desc {
    font-size: 13px;
    color: var(--text-muted);
    max-width: 400px;
    margin-bottom: 20px;
    line-height: 1.5;
  }

  .drop-browse {
    display: inline-flex;
    padding: 8px 20px;
    border-radius: var(--radius-sm);
    background: var(--accent);
    color: white;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .drop-browse:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
  }

  .search-results {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .results-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .result-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 12px;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .result-file {
    font-size: 12px;
    font-weight: 600;
    color: var(--accent-glow);
  }

  .result-score {
    font-size: 11px;
    color: var(--text-muted);
    background: var(--bg-surface-hover);
    padding: 2px 8px;
    border-radius: 10px;
  }

  .result-content {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .file-preview {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .preview-header {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--accent-glow);
  }

  .preview-meta {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .preview-name {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
  }

  .preview-info {
    font-size: 12px;
    color: var(--text-muted);
  }

  .preview-content {
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.6;
    color: var(--text-secondary);
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 16px;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-y: auto;
    max-height: 500px;
    margin: 0;
  }

  .preview-loading {
    font-size: 13px;
    color: var(--text-muted);
  }
</style>
