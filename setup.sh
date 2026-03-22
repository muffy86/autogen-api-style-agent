#!/usr/bin/env bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

header() { echo -e "\n${CYAN}=== $1 ===${NC}\n"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

# Detect platform
IS_TERMUX=false
if [ -d "/data/data/com.termux" ]; then
    IS_TERMUX=true
fi

header "NanoClaw Bot Setup"
echo "Platform: $([ "$IS_TERMUX" = true ] && echo 'Termux (Android)' || echo 'Linux')"

# Step 1: Install system dependencies
header "Step 1: System Dependencies"
if [ "$IS_TERMUX" = true ]; then
    pkg update -y
    pkg install -y python tmux git
else
    if command -v apt-get &>/dev/null; then
        if command -v sudo &>/dev/null; then
            sudo apt-get update -y
            sudo apt-get install -y python3 python3-pip python3-venv tmux git
        else
            warn "sudo not available. Please install manually: python3 python3-pip python3-venv tmux git"
        fi
    elif command -v dnf &>/dev/null; then
        if command -v sudo &>/dev/null; then
            sudo dnf install -y python3 python3-pip tmux git
        else
            warn "sudo not available. Please install manually: python3 python3-pip tmux git"
        fi
    elif command -v pacman &>/dev/null; then
        if command -v sudo &>/dev/null; then
            sudo pacman -Sy --noconfirm python python-pip tmux git
        else
            warn "sudo not available. Please install manually: python python-pip tmux git"
        fi
    else
        warn "Unknown package manager. Ensure python3, pip, tmux, and git are installed."
    fi
fi
success "System dependencies installed"

# Step 2: Clone or update repo
header "Step 2: Project Setup"
INSTALL_DIR="${NANOCLAW_DIR:-$HOME/nanoclaw-bot}"
if [ -d "$INSTALL_DIR" ]; then
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/muffy86/autogen-api-style-agent.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
success "Project ready at $INSTALL_DIR"

# Step 3: Python virtual environment
header "Step 3: Python Environment"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
success "Python environment configured"

# Step 4: Interactive configuration
header "Step 4: Configuration"
ENV_FILE="$INSTALL_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo "Existing .env found. Overwrite? (y/N)"
    read -r overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        success "Keeping existing configuration"
    else
        configure_env=true
    fi
else
    configure_env=true
fi

if [ "${configure_env:-false}" = true ]; then
    echo ""
    echo "You need two things from Telegram:"
    echo "  1. Bot Token — get from @BotFather (https://t.me/BotFather)"
    echo "  2. Your Chat ID — get from @userinfobot (https://t.me/userinfobot)"
    echo ""

    read -rp "Enter Telegram Bot Token: " BOT_TOKEN
    if [ -z "$BOT_TOKEN" ]; then
        error "Bot token is required"
    fi

    read -rp "Enter your Telegram Chat ID: " CHAT_ID
    if [ -z "$CHAT_ID" ]; then
        error "Chat ID is required"
    fi

    # Validate chat ID is numeric
    if ! [[ "$CHAT_ID" =~ ^[0-9]+$ ]]; then
        error "Chat ID must be a number"
    fi

    cat > "$ENV_FILE" << EOF
# NanoClaw Bot Configuration
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
TELEGRAM_OWNER_CHAT_ID=$CHAT_ID

# AI API Keys (set via /configure command in Telegram)
# OPENAI_API_KEY=
# MISTRAL_API_KEY=
# ANTHROPIC_API_KEY=
EOF
    chmod 600 "$ENV_FILE"
    success "Configuration saved to .env (permissions: 600)"
fi

# Step 5: Create launcher script
header "Step 5: Launcher"
LAUNCHER="$INSTALL_DIR/start.sh"
cat > "$LAUNCHER" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv
source .venv/bin/activate

# Kill existing bot session if any
tmux kill-session -t nanoclaw_bot 2>/dev/null || true

# Start bot in tmux
tmux new-session -d -s nanoclaw_bot "cd $SCRIPT_DIR && source .venv/bin/activate && python -m nanoclaw_bot"

echo "🤖 NanoClaw Bot started in tmux session 'nanoclaw_bot'"
echo "   Attach: tmux attach -t nanoclaw_bot"
echo "   Stop:   tmux kill-session -t nanoclaw_bot"
EOF
chmod +x "$LAUNCHER"
success "Launcher created at $LAUNCHER"

# Step 6: Offer to start
header "Setup Complete!"
echo ""
echo "To start the bot:"
echo "  cd $INSTALL_DIR && bash start.sh"
echo ""
echo "Or run directly:"
echo "  cd $INSTALL_DIR && source .venv/bin/activate && python -m nanoclaw_bot"
echo ""
read -rp "Start the bot now? (Y/n): " START_NOW
if [ "$START_NOW" != "n" ] && [ "$START_NOW" != "N" ]; then
    bash "$LAUNCHER"
fi
