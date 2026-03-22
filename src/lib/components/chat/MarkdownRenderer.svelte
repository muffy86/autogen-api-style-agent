<script lang="ts">
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  import hljs from 'highlight.js';

  interface Props {
    content: string;
  }

  let { content }: Props = $props();

  let rendered = $derived.by(() => {
    const renderer = new marked.Renderer();

    renderer.code = ({ text, lang }: { text: string; lang?: string }) => {
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext';
      const label = lang || 'code';
      let highlighted: string;
      try {
        highlighted = hljs.highlight(text, { language }).value;
      } catch {
        highlighted = hljs.highlightAuto(text).value;
      }
      const escaped = text.replace(/`/g, '\\`').replace(/\$/g, '\\$');
      return `<div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-lang">${label}</span>
          <button class="copy-btn" onclick="(() => { navigator.clipboard.writeText(\`${escaped}\`); const el = event.target; el.textContent = 'Copied!'; setTimeout(() => el.textContent = 'Copy', 1500); })()">Copy</button>
        </div>
        <pre><code class="hljs language-${language}">${highlighted}</code></pre>
      </div>`;
    };

    renderer.codespan = ({ text }: { text: string }) => {
      return `<code class="inline-code">${text}</code>`;
    };

    marked.setOptions({
      renderer,
      gfm: true,
      breaks: true,
    });

    const rawHtml = marked.parse(content) as string;
    return DOMPurify.sanitize(rawHtml, {
      ADD_ATTR: ['onclick'],
      ADD_TAGS: ['button'],
    });
  });
</script>

<div class="markdown-body">
  {@html rendered}
</div>

<style>
  .markdown-body {
    font-size: 13px;
    line-height: 1.65;
    color: var(--text-primary);
    word-break: break-word;
  }

  .markdown-body :global(p) {
    margin: 0 0 8px;
  }

  .markdown-body :global(p:last-child) {
    margin-bottom: 0;
  }

  .markdown-body :global(strong) {
    font-weight: 600;
    color: var(--text-primary);
  }

  .markdown-body :global(em) {
    font-style: italic;
  }

  .markdown-body :global(a) {
    color: var(--accent-glow);
    text-decoration: none;
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    transition: border-color var(--transition-fast);
  }

  .markdown-body :global(a:hover) {
    border-color: var(--accent-glow);
  }

  .markdown-body :global(ul),
  .markdown-body :global(ol) {
    margin: 4px 0 8px;
    padding-left: 20px;
  }

  .markdown-body :global(li) {
    margin-bottom: 2px;
  }

  .markdown-body :global(li::marker) {
    color: var(--text-muted);
  }

  .markdown-body :global(blockquote) {
    margin: 8px 0;
    padding: 4px 12px;
    border-left: 3px solid var(--accent);
    background: rgba(139, 92, 246, 0.06);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    color: var(--text-secondary);
  }

  .markdown-body :global(hr) {
    border: none;
    height: 1px;
    background: var(--border-subtle);
    margin: 12px 0;
  }

  .markdown-body :global(h1),
  .markdown-body :global(h2),
  .markdown-body :global(h3),
  .markdown-body :global(h4) {
    font-weight: 600;
    color: var(--text-primary);
    margin: 12px 0 6px;
    line-height: 1.3;
  }

  .markdown-body :global(h1) { font-size: 18px; }
  .markdown-body :global(h2) { font-size: 16px; }
  .markdown-body :global(h3) { font-size: 14px; }
  .markdown-body :global(h4) { font-size: 13px; }

  .markdown-body :global(.inline-code) {
    background: rgba(255, 255, 255, 0.08);
    padding: 1px 5px;
    border-radius: 4px;
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #e2b3ff;
    border: 1px solid rgba(255, 255, 255, 0.06);
  }

  .markdown-body :global(.code-block-wrapper) {
    margin: 8px 0;
    border-radius: var(--radius-sm);
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(0, 0, 0, 0.35);
  }

  .markdown-body :global(.code-block-header) {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: rgba(255, 255, 255, 0.04);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  .markdown-body :global(.code-lang) {
    font-size: 11px;
    color: var(--text-muted);
    font-family: 'SF Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .markdown-body :global(.copy-btn) {
    font-size: 11px;
    color: var(--text-muted);
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-family: inherit;
    transition: all var(--transition-fast);
  }

  .markdown-body :global(.copy-btn:hover) {
    color: var(--text-primary);
    border-color: rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.05);
  }

  .markdown-body :global(pre) {
    margin: 0;
    padding: 12px;
    overflow-x: auto;
  }

  .markdown-body :global(pre code) {
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
    background: none;
    padding: 0;
    border: none;
  }

  .markdown-body :global(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 12px;
  }

  .markdown-body :global(th),
  .markdown-body :global(td) {
    padding: 6px 10px;
    border: 1px solid var(--border-subtle);
    text-align: left;
  }

  .markdown-body :global(th) {
    background: rgba(255, 255, 255, 0.04);
    font-weight: 600;
    color: var(--text-primary);
  }

  .markdown-body :global(td) {
    color: var(--text-secondary);
  }

  .markdown-body :global(img) {
    max-width: 100%;
    border-radius: var(--radius-sm);
  }
</style>
