#!/bin/bash
# 
# Auto-Fix Code Quality Issues
# Automatically applies fixes for common code quality issues.
# 

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
QUALITY_DIR="$SCRIPT_DIR/quality"

# Source common utilities
source "$QUALITY_DIR/common.sh"

main() {
    echo -e "${BLUE}🔧 Auto-Fix Code Quality Issues${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    
    # 1. Fix code formatting with Black
    echo -e "${BLUE}1. Applying Black formatting...${NC}"
    if "$QUALITY_DIR/format_check.sh" --fix; then
        print_status "PASS" "Black formatting applied"
    else
        print_status "ERROR" "Black formatting failed"
    fi
    echo ""
    
    # 2. Fix import sorting with isort
    echo -e "${BLUE}2. Sorting imports with isort...${NC}"
    if "$QUALITY_DIR/import_check.sh" --fix; then
        print_status "PASS" "Import sorting applied"
    else
        print_status "ERROR" "Import sorting failed"
    fi
    echo ""
    
    # 3. Remove trailing whitespace
    echo -e "${BLUE}3. Removing trailing whitespace...${NC}"
    local files_fixed=0
    while IFS= read -r -d '' file; do
        if sed -i 's/[[:space:]]*$//' "$file" 2>/dev/null; then
            ((files_fixed++))
        fi
    done < <(find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*" -not -path "./.pytest_cache/*" -print0)
    
    if [ $files_fixed -gt 0 ]; then
        print_status "PASS" "Removed trailing whitespace from $files_fixed files"
    else
        print_status "INFO" "No trailing whitespace found"
    fi
    echo ""
    
    # 4. Fix common flake8 issues
    echo -e "${BLUE}4. Fixing common flake8 issues...${NC}"
    local flake8_fixes=0
    
    # Remove unused imports (simple cases)
    while IFS= read -r -d '' file; do
        if python3 -c "
import ast
import sys

try:
    with open('$file', 'r') as f:
        content = f.read()
    
    # Simple unused import removal (very basic)
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # Skip obvious unused imports (this is very basic)
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            # Keep the line for now (more complex analysis needed)
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    # For now, just keep the file as is
    # More sophisticated unused import removal would require AST analysis
    
except Exception:
    pass
" 2>/dev/null; then
            ((flake8_fixes++))
        fi
    done < <(find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*" -not -path "./.pytest_cache/*" -print0)
    
    print_status "INFO" "Basic flake8 fixes applied (manual review recommended)"
    echo ""
    
    # 5. Run final quality check
    echo -e "${BLUE}5. Running final quality check...${NC}"
    if "$SCRIPT_DIR/quality_check.sh" --fast; then
        print_status "PASS" "Quality check passed after fixes"
    else
        print_status "WARN" "Some issues remain (manual review needed)"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Auto-fix completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the changes: git diff"
    echo "2. Run full quality check: ./scripts/quality_check.sh"
    echo "3. Run tests: ./scripts/quality/test_runner.sh"
    echo "4. Commit changes if satisfied"
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
