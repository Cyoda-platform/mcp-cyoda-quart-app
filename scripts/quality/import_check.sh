#!/bin/bash
# 
# Import Sorting Checker (isort)
# Validates and optionally fixes Python import organization.
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
                echo "  --fix    Apply import sorting fixes automatically"
                exit 1
                ;;
        esac
    done
    
    print_header "Import Sorting Check (isort)"
    
    # Install isort if missing
    if ! install_tool_if_missing isort; then
        print_status "ERROR" "isort installation failed, skipping import check"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    
    if [ "$fix_mode" = true ]; then
        echo "Applying import sorting fixes..."
        local fix_output
        fix_output=$(isort --skip .venv --skip __pycache__ --skip .pytest_cache . 2>&1)
        local fix_exit_code=$?

        if [ $fix_exit_code -eq 0 ]; then
            print_status "PASS" "Import sorting applied successfully"
            return 0
        else
            print_status "ERROR" "Failed to apply import sorting"
            echo "Error details: $fix_output"
            return 1
        fi
    else
        echo "Checking import sorting..."
        local isort_output
        isort_output=$(isort --check-only --diff --skip .venv --skip __pycache__ --skip .pytest_cache . 2>&1)
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            print_status "PASS" "All imports are properly sorted"
            return 0
        else
            local file_count=0
            if [ -n "$isort_output" ]; then
                file_count=$(echo "$isort_output" | grep -c "ERROR:" 2>/dev/null || echo "0")
                file_count=$(echo "$file_count" | tr -d ' \n\r')
            fi
            print_status "WARN" "Some imports need sorting ($file_count files)"

            echo "Files with import issues:"
            echo "$isort_output" | grep "ERROR:" | head -5
            
            echo ""
            echo "To fix imports: $0 --fix"
            echo "Or run: isort --skip .venv --skip __pycache__ --skip .pytest_cache ."
            return 1
        fi
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
