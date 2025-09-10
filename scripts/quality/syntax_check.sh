#!/bin/bash
#
# Python Syntax Checker
# Validates Python syntax across the codebase using py_compile.
#

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    print_header "Python Syntax Check"

    echo "Checking Python syntax using py_compile..."
    cd "$PROJECT_ROOT"

    local error_count=0
    local file_count=0
    local warning_count=0

    # Find all Python files
    while IFS= read -r -d '' file; do
        ((file_count++))

        # Basic syntax check
        local compile_output
        compile_output=$(python -m py_compile "$file" 2>&1)
        local compile_exit=$?

        if [ $compile_exit -ne 0 ]; then
            echo -e "${RED}❌ Syntax error in: $file${NC}"
            echo "   $compile_output"
            ((error_count++))
        else
            # Additional static analysis checks
            local static_issues=""

            # Check for common issues that py_compile might miss
            if grep -n "validation\[valid\]" "$file" >/dev/null 2>&1; then
                static_issues="${static_issues}   ⚠️  Line $(grep -n "validation\[valid\]" "$file" | cut -d: -f1): Possible undefined variable 'valid' - did you mean 'validation[\"valid\"]'?\n"
                ((warning_count++))
            fi

            # Check for method calls with missing arguments
            if grep -n "_discover_from_single_module()" "$file" >/dev/null 2>&1; then
                local line_num=$(grep -n "_discover_from_single_module()" "$file" | cut -d: -f1)
                static_issues="${static_issues}   ❌ Line $line_num: Method '_discover_from_single_module()' called without required arguments - check method signature\n"
                ((warning_count++))
            fi

            # Check for other common method signature issues
            local method_issues=$(python3 -c "
import re
import sys

try:
    with open('$file', 'r') as f:
        content = f.read()
        lines = content.split('\n')

    issues = []

    # Look for method definitions and calls
    for i, line in enumerate(lines, 1):
        # Find method definitions with parameters
        if re.search(r'def\s+(\w+)\s*\([^)]*\w[^)]*\):', line):
            method_match = re.search(r'def\s+(\w+)\s*\(([^)]+)\):', line)
            if method_match:
                method_name = method_match.group(1)
                params = method_match.group(2)
                param_count = len([p.strip() for p in params.split(',') if p.strip() and p.strip() != 'self'])

                # Look for calls to this method with wrong argument count
                for j, call_line in enumerate(lines, 1):
                    if f'{method_name}()' in call_line and 'def ' not in call_line:
                        if param_count > 0:
                            issues.append(f'Line {j}: Method \"{method_name}()\" called without arguments but expects {param_count}')

    for issue in issues:
        print(f'   ❌ {issue}')

except Exception:
    pass
" 2>/dev/null)

            if [ -n "$method_issues" ]; then
                static_issues="${static_issues}$method_issues\n"
                ((warning_count++))
            fi

            # Check for other common issues
            if grep -n "\[.*[a-zA-Z_][a-zA-Z0-9_]*\]" "$file" | grep -v '"\|'"'" >/dev/null 2>&1; then
                local suspicious_lines=$(grep -n "\[.*[a-zA-Z_][a-zA-Z0-9_]*\]" "$file" | grep -v '"\|'"'" | head -3)
                if [ -n "$suspicious_lines" ]; then
                    static_issues="${static_issues}   ⚠️  Possible unquoted dictionary keys found:\n$(echo "$suspicious_lines" | sed 's/^/      /')\n"
                    ((warning_count++))
                fi
            fi

            # Show static analysis warnings
            if [ -n "$static_issues" ]; then
                echo -e "${YELLOW}⚠️  Static analysis warnings in: $file${NC}"
                echo -e "$static_issues"
            fi
        fi
    done < <(find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*" -not -path "./.pytest_cache/*" -print0)

    # Summary
    if [ $error_count -eq 0 ] && [ $warning_count -eq 0 ]; then
        echo -e "${GREEN}✅ All $file_count Python files have valid syntax${NC}"
        return 0
    elif [ $error_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  All $file_count Python files have valid syntax, but found $warning_count static analysis warnings${NC}"
        return 1
    else
        echo -e "${RED}❌ Found $error_count syntax errors and $warning_count warnings in $file_count files${NC}"
        return 1
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
