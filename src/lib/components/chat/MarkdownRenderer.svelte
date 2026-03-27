<script lang="ts">
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  import hljs from 'highlight.js';

  interface Props {
    content: string;
  }

  let { content }: Props = $props();

  let containerEl: HTMLDivElement | undefined = $state(undefined);

  function encodeDataCode(text: string): string {
    return btoa(encodeURIComponent(text));
  }

  function addLineNumbers(code: string): string {
    const lines = code.split('\n');
    return lines
      .map((line, i) => {
        const num = i + 1;
        return `<span class="code-line"><span class="line-num">${num}</span><span class="line-content">${line}</span></span>`;
      })
      .join('\n');
  }

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
      const withLineNums = addLineNumbers(highlighted);
      const encoded = encodeDataCode(text);
      return `<div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-lang-badge">${label}</span>
          <div class="code-header-actions">
            <button class="wrap-toggle-btn" data-wrap-toggle="true">Wrap</button>
            <button class="copy-btn" data-code="${encoded}">Copy</button>
          </div>
        </div>
        <pre class="code-pre"><code class="hljs language-${language} code-with-lines">${withLineNums}</code></pre>
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
      ADD_TAGS: ['button'],
      ADD_ATTR: ['data-code', 'data-wrap-toggle'],
    });
  });

  $effect(() => {
    void rendered;
    if (!containerEl) return;

    function handleClick(e: Event) {
      const target = e.target as HTMLElement;

      const copyBtn = target.closest('.copy-btn') as HTMLElement | null;
      if (copyBtn) {
        const encoded = copyBtn.getAttribute('data-code') ?? '';
        let code: string;
        try {
          code = decodeURIComponent(atob(encoded));
        } catch {
          code = '';
        }
        navigator.clipboard.writeText(code);
        copyBtn.textContent = 'Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          copyBtn.textContent = 'Copy';
          copyBtn.classList.remove('copied');
        }, 2000);
        return;
      }

      const wrapBtn = target.closest('[data-wrap-toggle]') as HTMLElement | null;
      if (wrapBtn) {
        const wrapper = wrapBtn.closest('.code-block-wrapper');
        if (wrapper) {
          wrapper.classList.toggle('wrap-lines');
          wrapBtn.textContent = wrapper.classList.contains('wrap-lines') ? 'Unwrap' : 'Wrap';
        }
      }
    }

    containerEl.addEventListener('click', handleClick);
    return () => containerEl?.removeEventListener('click', handleClick);
  });
</script>

<div class="markdown-body" bind:this={containerEl}>
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
    background: rgba(0, 0, 0, 0.4);
  }

  .markdown-body :global(.code-block-header) {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 5px 10px;
    background: rgba(255, 255, 255, 0.04);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  }

  .markdown-body :global(.code-lang-badge) {
    font-size: 10px;
    color: var(--accent-glow);
    font-family: 'SF Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    padding: 2px 6px;
    background: rgba(139, 92, 246, 0.1);
    border-radius: 4px;
  }

  .markdown-body :global(.code-header-actions) {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .markdown-body :global(.copy-btn),
  .markdown-body :global(.wrap-toggle-btn) {
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

  .markdown-body :global(.copy-btn:hover),
  .markdown-body :global(.wrap-toggle-btn:hover) {
    color: var(--text-primary);
    border-color: rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.05);
  }

  .markdown-body :global(.copy-btn.copied) {
    color: #22c55e;
    border-color: rgba(34, 197, 94, 0.3);
  }

  .markdown-body :global(.code-pre) {
    margin: 0;
    padding: 10px 0;
    overflow-x: auto;
  }

  .markdown-body :global(.code-with-lines) {
    display: flex;
    flex-direction: column;
    font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.55;
    background: none;
    padding: 0;
    border: none;
    counter-reset: line;
  }

  .markdown-body :global(.code-line) {
    display: flex;
    min-height: 19px;
  }

  .markdown-body :global(.code-line:hover) {
    background: rgba(255, 255, 255, 0.03);
  }

  .markdown-body :global(.line-num) {
    display: inline-block;
    min-width: 36px;
    padding: 0 10px 0 12px;
    text-align: right;
    color: rgba(255, 255, 255, 0.18);
    font-size: 11px;
    user-select: none;
    flex-shrink: 0;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    margin-right: 12px;
  }

  .markdown-body :global(.line-content) {
    flex: 1;
    padding-right: 12px;
    white-space: pre;
  }

  .markdown-body :global(.code-block-wrapper.wrap-lines .line-content) {
    white-space: pre-wrap;
    word-break: break-all;
  }

  /* Custom syntax theme matching glassmorphism */
  .markdown-body :global(.hljs) {
    color: #c9d1d9;
  }

  .markdown-body :global(.hljs-keyword),
  .markdown-body :global(.hljs-selector-tag),
  .markdown-body :global(.hljs-literal),
  .markdown-body :global(.hljs-section),
  .markdown-body :global(.hljs-link) {
    color: #c792ea;
  }

  .markdown-body :global(.hljs-function .hljs-keyword) {
    color: #82aaff;
  }

  .markdown-body :global(.hljs-string),
  .markdown-body :global(.hljs-meta .hljs-string) {
    color: #c3e88d;
  }

  .markdown-body :global(.hljs-number),
  .markdown-body :global(.hljs-symbol) {
    color: #f78c6c;
  }

  .markdown-body :global(.hljs-attr),
  .markdown-body :global(.hljs-variable),
  .markdown-body :global(.hljs-template-variable),
  .markdown-body :global(.hljs-selector-attr),
  .markdown-body :global(.hljs-selector-pseudo) {
    color: #ffcb6b;
  }

  .markdown-body :global(.hljs-built_in),
  .markdown-body :global(.hljs-title),
  .markdown-body :global(.hljs-name) {
    color: #82aaff;
  }

  .markdown-body :global(.hljs-comment),
  .markdown-body :global(.hljs-quote) {
    color: #676e95;
    font-style: italic;
  }

  .markdown-body :global(.hljs-doctag),
  .markdown-body :global(.hljs-formula) {
    color: #c3e88d;
  }

  .markdown-body :global(.hljs-deletion) {
    color: #ff5370;
  }

  .markdown-body :global(.hljs-addition) {
    color: #c3e88d;
  }

  .markdown-body :global(.hljs-type),
  .markdown-body :global(.hljs-class .hljs-title) {
    color: #ffcb6b;
  }

  .markdown-body :global(.hljs-regexp),
  .markdown-body :global(.hljs-selector-id),
  .markdown-body :global(.hljs-selector-class) {
    color: #89ddff;
  }

  .markdown-body :global(.hljs-meta),
  .markdown-body :global(.hljs-meta-keyword) {
    color: #89ddff;
  }

  .markdown-body :global(.hljs-params) {
    color: #e0e0e0;
  }

  .markdown-body :global(.hljs-tag) {
    color: #f07178;
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
