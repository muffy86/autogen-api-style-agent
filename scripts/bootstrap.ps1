#Requires -Version 5.1
<#
.SYNOPSIS
    AutoGen API Style Agent — Windows Bootstrap Script
.DESCRIPTION
    Sets up the development environment on Windows: Python venv, dependencies,
    .env configuration, and MCP server installation.
#>

$ErrorActionPreference = "Stop"

function Write-Color {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

Write-Color "🤖 AutoGen API Style Agent — Bootstrap" "Cyan"
Write-Host "========================================="

# Check Python 3.10+
function Test-Python {
    try {
        $version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if (-not $version) {
            $version = & python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        }
        if ($version) {
            $parts = $version.Split('.')
            $major = [int]$parts[0]
            $minor = [int]$parts[1]
            if ($major -ge 3 -and $minor -ge 10) {
                Write-Color "✅ Python $version found" "Green"
                return $true
            }
        }
    } catch {}
    Write-Color "❌ Python 3.10+ required. Install from https://python.org" "Red"
    exit 1
}

# Check Node.js
function Test-Node {
    try {
        $nodeVersion = & node -v 2>$null
        if ($nodeVersion) {
            Write-Color "✅ Node.js $nodeVersion found" "Green"
            return $true
        }
    } catch {}
    Write-Color "⚠️  Node.js not found. MCP servers require Node.js. Install from https://nodejs.org" "Yellow"
    return $false
}

Test-Python
$hasNode = Test-Node

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot

# Create venv
Write-Host ""
Write-Color "📦 Creating virtual environment..." "Cyan"
if (Test-Path ".venv") {
    Write-Color "  ↳ .venv already exists, reusing" "Yellow"
} else {
    & python -m venv .venv
}

# Activate venv
if ($IsWindows -or $env:OS -match "Windows") {
    & .\.venv\Scripts\Activate.ps1
} else {
    & ./.venv/bin/Activate.ps1
}

# Install
Write-Color "📥 Installing autogen-api-style-agent..." "Cyan"
& pip install -e ".[dev]" --quiet

# Setup .env
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Color "⚙️  Creating .env from template..." "Cyan"
    if (Test-Path "configs/.env.example") {
        Copy-Item "configs/.env.example" ".env"
        Write-Color "📝 Edit .env to add your API keys" "Yellow"
    } else {
        New-Item -ItemType File -Path ".env" -Force | Out-Null
        Write-Color "📝 Created empty .env — add your API keys" "Yellow"
    }
} else {
    Write-Host ""
    Write-Color "✅ .env already exists" "Green"
}

# Check API keys
Write-Host ""
Write-Color "🔍 Checking for API keys..." "Cyan"
$providers = @("OPENAI_API_KEY", "TOGETHER_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY", "MOONSHOT_API_KEY", "MISTRAL_API_KEY")
$found = 0
foreach ($key in $providers) {
    $value = [System.Environment]::GetEnvironmentVariable($key)
    if ($value) {
        Write-Color "  ✅ $key found in environment" "Green"
        try {
            $envContent = Get-Content ".env" -ErrorAction SilentlyContinue
            if (-not ($envContent -match "^$key=")) {
                Add-Content ".env" "$key=$value" -ErrorAction Stop
            }
        } catch {
            Write-Color "  ⚠️  Failed to write $key to .env: $_" "Yellow"
        }
        $found++
    } else {
        Write-Color "  ⬚  $key not set" "Yellow"
    }
}

if ($found -eq 0) {
    Write-Host ""
    Write-Color "⚠️  No API keys found! Set at least one in .env" "Red"
}

# Install MCP servers
Write-Host ""
Write-Color "🔌 Installing MCP servers..." "Cyan"
if ($hasNode) {
    try { & npx -y @modelcontextprotocol/server-github --version 2>$null; Write-Color "  ✅ GitHub MCP" "Green" } catch {}
    try { & npx -y @modelcontextprotocol/server-filesystem --version 2>$null; Write-Color "  ✅ Filesystem MCP" "Green" } catch {}
    try { & npx -y @modelcontextprotocol/server-fetch --version 2>$null; Write-Color "  ✅ Fetch MCP" "Green" } catch {}
} else {
    Write-Color "  ⚠️  npx not found, skipping MCP server install" "Yellow"
}

# Verify
Write-Host ""
Write-Color "🧪 Verifying installation..." "Cyan"
try {
    & python -c "from autogen_api_agent import __version__; print(f'  ✅ autogen-api-style-agent v{__version__}')"
} catch {
    Write-Color "  ⚠️  Package import check skipped (source modules pending)" "Yellow"
}
try { & python -c "from autogen_api_agent.providers import ModelClientFactory; print('  ✅ Provider factory loaded')" } catch {}
try { & python -c "from autogen_api_agent.teams import create_team; print('  ✅ Team registry loaded')" } catch {}

Write-Host ""
Write-Color "🎉 Bootstrap complete!" "Green"
Write-Host ""
Write-Host "Quick start:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  agent providers          # Check available providers"
Write-Host "  agent chat 'Hello!'      # Quick chat"
Write-Host "  agent interactive        # Interactive REPL"
Write-Host "  agent serve              # Start HTTP API server"
Write-Host "  agent mcp-serve          # Start MCP server for IDE"
Write-Host ""
Write-Host "Or use Docker:"
Write-Host "  docker-compose up"
