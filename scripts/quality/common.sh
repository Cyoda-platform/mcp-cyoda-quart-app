#!/bin/bash
#
# Common utilities for code quality scripts
# Shared functions, colors, and tool installation logic.
#

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print section header
print_header() {
    echo -e "${BLUE}🔧 $1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

print_section() {
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install tool if missing
install_tool_if_missing() {
    local tool_name="$1"
    local package_name="${2:-$1}"
    
    if command_exists "$tool_name"; then
        return 0
    fi
    
    echo "📦 Installing $tool_name..."
    if python -m pip install "$package_name" &> /dev/null; then
        echo -e "${GREEN}✅ Successfully installed $tool_name${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Failed to install $tool_name${NC}"
        return 1
    fi
}

# Check if we're in a Python virtual environment
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo -e "${YELLOW}⚠️  Not in a virtual environment${NC}"
        echo "   Consider activating .venv: source .venv/bin/activate"
    else
        echo -e "${GREEN}✅ Using virtual environment: $(basename "$VIRTUAL_ENV")${NC}"
    fi
}

# Get project root directory
get_project_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
    echo "$(cd "$script_dir/../.." && pwd)"
}

# Print success/failure status
print_status() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        "PASS"|"SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "FAIL"|"ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "WARN"|"WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        *)
            echo "$message"
            ;;
    esac
}

# Run command with timeout and capture output
run_with_timeout() {
    local timeout_duration="$1"
    local command="$2"
    shift 2
    
    timeout "$timeout_duration" "$command" "$@"
    return $?
}
