#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo -e "${BLUE}🤖 AutoGen API Style Agent — Bootstrap${NC}"
echo "========================================="

check_python() {
    if command -v python3 &>/dev/null; then
        version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            echo -e "${GREEN}✅ Python $version found${NC}"
            return 0
        fi
    fi
    echo -e "${RED}❌ Python 3.10+ required. Install from https://python.org${NC}"
    exit 1
}

check_node() {
    if command -v node &>/dev/null; then
        echo -e "${GREEN}✅ Node.js $(node -v) found${NC}"
    else
        echo -e "${YELLOW}⚠️  Node.js not found. MCP servers require Node.js. Install from https://nodejs.org${NC}"
    fi
}

check_python
check_node

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "\n${BLUE}📦 Creating virtual environment...${NC}"
if [ -d .venv ]; then
    echo -e "${YELLOW}  ↳ .venv already exists, reusing${NC}"
else
    python3 -m venv .venv
fi
source .venv/bin/activate

echo -e "${BLUE}📥 Installing autogen-api-style-agent...${NC}"
pip install -e ".[dev]" --quiet

if [ ! -f .env ]; then
    echo -e "\n${BLUE}⚙️  Creating .env from template...${NC}"
    if [ -f configs/.env.example ]; then
        cp configs/.env.example .env
        echo -e "${YELLOW}📝 Edit .env to add your API keys${NC}"
    else
        touch .env
        echo -e "${YELLOW}📝 Created empty .env — add your API keys${NC}"
    fi
else
    echo -e "\n${GREEN}✅ .env already exists${NC}"
fi

echo -e "\n${BLUE}🔍 Checking for API keys...${NC}"
providers=("OPENAI_API_KEY" "TOGETHER_API_KEY" "OPENROUTER_API_KEY" "GOOGLE_API_KEY" "MOONSHOT_API_KEY" "MISTRAL_API_KEY")
found=0
for key in "${providers[@]}"; do
    if [ -n "${!key:-}" ]; then
        echo -e "  ${GREEN}✅ $key found in environment${NC}"
        if ! grep -q "^$key=" .env 2>/dev/null; then
            echo "$key=${!key}" >> .env || echo -e "  ${YELLOW}⚠️  Failed to write $key to .env${NC}" >&2
        fi
        found=$((found + 1))
    else
        echo -e "  ${YELLOW}⬚  $key not set${NC}"
    fi
done

if [ "$found" -eq 0 ]; then
    echo -e "\n${RED}⚠️  No API keys found! Set at least one in .env${NC}"
fi

echo -e "\n${BLUE}🔌 Installing MCP servers...${NC}"
if command -v npx &>/dev/null; then
    npx -y @modelcontextprotocol/server-github --version 2>/dev/null && echo -e "  ${GREEN}✅ GitHub MCP${NC}" || true
    npx -y @modelcontextprotocol/server-filesystem --version 2>/dev/null && echo -e "  ${GREEN}✅ Filesystem MCP${NC}" || true
    npx -y @modelcontextprotocol/server-fetch --version 2>/dev/null && echo -e "  ${GREEN}✅ Fetch MCP${NC}" || true
else
    echo -e "  ${YELLOW}⚠️  npx not found, skipping MCP server install${NC}"
fi

echo -e "\n${BLUE}🧪 Verifying installation...${NC}"
python3 -c "from autogen_api_agent import __version__; print(f'  ✅ autogen-api-style-agent v{__version__}')" 2>/dev/null || echo -e "  ${YELLOW}⚠️  Package import check skipped (source modules pending)${NC}"
python3 -c "from autogen_api_agent.providers import ModelClientFactory; print('  ✅ Provider factory loaded')" 2>/dev/null || true
python3 -c "from autogen_api_agent.teams import create_team; print('  ✅ Team registry loaded')" 2>/dev/null || true

echo -e "\n${GREEN}🎉 Bootstrap complete!${NC}"
echo ""
echo "Quick start:"
echo "  source .venv/bin/activate"
echo "  agent providers          # Check available providers"
echo "  agent chat 'Hello!'      # Quick chat"
echo "  agent interactive        # Interactive REPL"
echo "  agent serve              # Start HTTP API server"
echo "  agent mcp-serve          # Start MCP server for IDE"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
