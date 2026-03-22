<script lang="ts">
  let inputValue = $state('');

  const history = [
    { prompt: 'elysium@ai-os ~ $', command: 'neofetch', output: `
  ╔═══════════════════════════════╗
  ║      ELYSIUM AI OS v1.0      ║
  ╠═══════════════════════════════╣
  ║  OS:      Elysium AI OS      ║
  ║  Kernel:  SvelteKit 2.0      ║
  ║  Shell:   Elysium Terminal    ║
  ║  Theme:   Nebula Dark        ║
  ║  CPU:     Neural Engine v3   ║
  ║  Memory:  ∞ (Cloud)          ║
  ║  Uptime:  Always             ║
  ╚═══════════════════════════════╝` },
    { prompt: 'elysium@ai-os ~ $', command: 'ls -la', output: `total 42
drwxr-xr-x  6 elysium  ai-os   192 Mar 22 10:30 .
drwxr-xr-x  3 elysium  ai-os    96 Mar 22 09:00 ..
drwxr-xr-x  4 elysium  ai-os   128 Mar 22 10:15 documents
drwxr-xr-x  2 elysium  ai-os    64 Mar 22 10:20 downloads
drwxr-xr-x  8 elysium  ai-os   256 Mar 22 10:30 knowledge-base
-rw-r--r--  1 elysium  ai-os  1024 Mar 22 10:00 .config` },
    { prompt: 'elysium@ai-os ~ $', command: 'echo "Welcome to Elysium"', output: 'Welcome to Elysium' }
  ];

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      inputValue = '';
    }
  }
</script>

<div class="terminal">
  <div class="terminal-output scrollbar-thin">
    {#each history as entry}
      <div class="line">
        <span class="prompt">{entry.prompt}</span>
        <span class="command"> {entry.command}</span>
      </div>
      <pre class="output">{entry.output}</pre>
    {/each}
    <div class="line current">
      <span class="prompt">elysium@ai-os ~ $</span>
      <input
        class="terminal-input"
        type="text"
        bind:value={inputValue}
        onkeydown={handleKeydown}
        spellcheck="false"
        autocomplete="off"
      />
      <span class="cursor"></span>
    </div>
  </div>
</div>

<style>
  .terminal {
    height: 100%;
    background: #0a0a0f;
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Cascadia Code', monospace;
    font-size: 13px;
    line-height: 1.6;
  }

  .terminal-output {
    height: 100%;
    overflow-y: auto;
    padding: 12px 16px;
  }

  .line {
    display: flex;
    align-items: center;
  }

  .line.current {
    position: relative;
  }

  .prompt {
    color: var(--accent-glow);
    white-space: nowrap;
    flex-shrink: 0;
  }

  .command {
    color: #e4e4e7;
  }

  .output {
    color: var(--text-secondary);
    margin: 0 0 8px 0;
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    white-space: pre;
  }

  .terminal-input {
    flex: 1;
    background: transparent;
    border: none;
    color: #e4e4e7;
    font-family: inherit;
    font-size: inherit;
    outline: none;
    padding: 0;
    margin-left: 4px;
    caret-color: transparent;
  }

  .cursor {
    display: inline-block;
    width: 8px;
    height: 16px;
    background: var(--accent-glow);
    animation: blink 1s step-end infinite;
    margin-left: -2px;
    vertical-align: middle;
  }
</style>
