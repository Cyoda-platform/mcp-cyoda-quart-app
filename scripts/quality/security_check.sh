#!/bin/bash
# 
# Security Checker (Bandit)
# Scans Python code for common security vulnerabilities.
# 

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    local detailed=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --detailed)
                detailed=true
                shift
                ;;
            *)
                echo "Usage: $0 [--detailed]"
                echo "  --detailed    Show detailed security report"
                exit 1
                ;;
        esac
    done
    
    print_header "Security Check (bandit)"
    
    # Install bandit if missing
    if ! install_tool_if_missing bandit; then
        print_status "ERROR" "bandit installation failed, skipping security check"
        return 1
    fi
    
    echo "Running bandit security scan..."
    cd "$PROJECT_ROOT"
    
    # Run bandit with JSON output for parsing
    local bandit_output
    local bandit_stderr
    bandit_output=$(bandit -r . -f json --skip B101,B601 --exclude .venv,__pycache__,.pytest_cache -q 2>&1)
    local exit_code=$?
    
    if [ -n "$bandit_output" ]; then
        # Check if output is valid JSON
        if echo "$bandit_output" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
            # Parse JSON output to count issues
            local issue_count
            issue_count=$(echo "$bandit_output" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(len(data.get('results', [])))
except:
    print('0')
" 2>/dev/null || echo "0")

            if [ "$issue_count" -eq 0 ]; then
                print_status "PASS" "No security issues found"
                return 0
            else
                print_status "WARN" "Security issues found ($issue_count issues)"

                if [ "$detailed" = true ]; then
                    echo ""
                    echo "Security Issues:"
                    echo "$bandit_output" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for i, result in enumerate(data.get('results', [])[:10], 1):
        print(f'{i}. {result.get(\"filename\", \"unknown\")}:{result.get(\"line_number\", \"?\")}')
        print(f'   {result.get(\"issue_text\", \"No description\")}')
        print(f'   Severity: {result.get(\"issue_severity\", \"unknown\")}')
        print()
except Exception as e:
    print(f'Error parsing bandit output: {e}')
" 2>/dev/null
                else
                    echo "Run with --detailed for more information"
                fi

                echo ""
                echo "For full report: bandit -r . --exclude .venv"
                return 1
            fi
        else
            # Output is not valid JSON, treat as error
            print_status "ERROR" "Bandit produced invalid output"
            echo "Raw output: $bandit_output"
            return 1
        fi
    else
        print_status "PASS" "No security issues found"
        return 0
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
