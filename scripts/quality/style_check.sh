#!/bin/bash
#
# Code Style Checker (Flake8)
# Validates Python code style and detects common issues.
#

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    print_header "Code Style Check (flake8)"
    
    # Install flake8 if missing
    if ! install_tool_if_missing flake8; then
        print_status "ERROR" "flake8 installation failed, skipping style check"
        return 1
    fi
    
    echo "Running flake8 style check..."
    cd "$PROJECT_ROOT"
    
    # Run flake8 with custom configuration
    local flake8_output
    flake8_output=$(flake8 \
        --max-line-length=120 \
        --ignore=E203,W503,E501 \
        --select=E,W,F,N,C \
        --exclude=.venv,__pycache__,.pytest_cache \
        . 2>&1)

    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_status "PASS" "Code style check passed"
        return 0
    else
        if [ -n "$flake8_output" ]; then
            local issue_count=$(echo "$flake8_output" | wc -l)
            issue_count=$(echo "$issue_count" | tr -d ' \n\r')
            print_status "WARN" "Code style issues found ($issue_count issues)"

            # Show first 10 issues
            echo "First 10 issues:"
            echo "$flake8_output" | head -10

            if [ "$issue_count" -gt 10 ]; then
                echo "... and $((issue_count - 10)) more issues"
            fi
        else
            print_status "ERROR" "Flake8 failed to run properly"
        fi

        echo ""
        echo "To see all issues: flake8 --max-line-length=120 --ignore=E203,W503,E501 --exclude=.venv,__pycache__,.pytest_cache ."
        return 1
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
