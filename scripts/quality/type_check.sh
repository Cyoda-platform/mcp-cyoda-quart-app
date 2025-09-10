#!/bin/bash
# 
# Type Checking (MyPy)
# Validates Python type annotations and detects type-related issues.
# 

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    print_header "Type Checking (mypy)"
    
    # Install mypy if missing
    if ! install_tool_if_missing mypy; then
        print_status "ERROR" "mypy installation failed, skipping type check"
        return 1
    fi
    
    echo "Running mypy type checking..."
    cd "$PROJECT_ROOT"
    
    # Create mypy.ini if it doesn't exist
    if [ ! -f "mypy.ini" ]; then
        echo "📝 Creating mypy.ini configuration..."
        cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
no_strict_optional = True
show_error_codes = True

# Exclude directories
exclude = (?x)(
    ^\.venv/
    | ^__pycache__/
    | ^\.pytest_cache/
    | ^proto/
)

# Per-module options
[mypy-tests.*]
ignore_errors = True

[mypy-proto.*]
ignore_errors = True
EOF
    fi
    
    # Run mypy on specific directories to avoid project name issues
    local mypy_output
    mypy_output=$(mypy common/ service/ cyoda_mcp/ tests/ app.py 2>&1 || true)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_status "PASS" "Type checking passed"
        return 0
    else
        local issue_count=0
        if [ -n "$mypy_output" ]; then
            # Count actual error lines, not just grep matches
            issue_count=$(echo "$mypy_output" | grep "error:" | wc -l 2>/dev/null || echo "0")
            # Remove any whitespace/newlines from count
            issue_count=$(echo "$issue_count" | tr -d ' \n\r')
        fi
        
        if [ "$issue_count" -eq 0 ]; then
            print_status "PASS" "Type checking passed (no errors found)"
            return 0
        else
            print_status "WARN" "Type checking issues found ($issue_count issues)"
            
            echo "First 10 type issues:"
            echo "$mypy_output" | grep "error:" | head -10
            
            if [ "$issue_count" -gt 10 ]; then
                echo "... and $((issue_count - 10)) more issues"
            fi
            
            echo ""
            echo "To see all issues: mypy ."
            return 1
        fi
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
