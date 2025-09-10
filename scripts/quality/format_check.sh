#!/bin/bash
# 
# Code Formatting Checker (Black)
# Validates and optionally fixes Python code formatting.
# 

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    local fix_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --fix)
                fix_mode=true
                shift
                ;;
            *)
                echo "Usage: $0 [--fix]"
                echo "  --fix    Apply formatting fixes automatically"
                exit 1
                ;;
        esac
    done
    
    print_header "Code Formatting Check (black)"
    
    # Install black if missing
    if ! install_tool_if_missing black; then
        print_status "ERROR" "black installation failed, skipping formatting check"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    
    if [ "$fix_mode" = true ]; then
        echo "Applying black formatting fixes..."
        if black --exclude '(.venv|__pycache__|.pytest_cache)' .; then
            print_status "PASS" "Code formatting applied successfully"
            return 0
        else
            print_status "ERROR" "Failed to apply formatting"
            return 1
        fi
    else
        echo "Checking code formatting..."
        local black_output
        black_output=$(black --check --diff --exclude '(.venv|__pycache__|.pytest_cache)' . 2>&1)
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            print_status "PASS" "All files are properly formatted"
            return 0
        else
            local file_count=$(echo "$black_output" | grep -c "would reformat" || echo "0")
            print_status "WARN" "Some files need formatting ($file_count files)"
            
            echo "Files that need formatting:"
            echo "$black_output" | grep "would reformat" | head -5
            
            echo ""
            echo "To fix formatting: $0 --fix"
            echo "Or run: black --exclude '(.venv|__pycache__|.pytest_cache)' ."
            return 1
        fi
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
