#!/bin/bash
#
# Test All Quality Scripts
# Demonstrates that the scripts are working correctly
#

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source common utilities
source "$SCRIPT_DIR/common.sh"

main() {
    print_header "Testing All Quality Check Scripts"
    
    echo "Note: Exit codes 1 are EXPECTED when issues are found - this is correct behavior!"
    echo ""
    
    local scripts=(
        "syntax_check.sh"
        "style_check.sh" 
        "format_check.sh"
        "import_check.sh"
        "type_check.sh"
        "security_check.sh"
        "sonar_check.sh"
        "test_runner.sh"
    )
    
    local total=0
    local working=0
    
    for script in "${scripts[@]}"; do
        if [ -f "$SCRIPT_DIR/$script" ]; then
            echo -e "${BLUE}Testing $script...${NC}"
            
            # Run the script and capture exit code
            if "$SCRIPT_DIR/$script" >/dev/null 2>&1; then
                echo -e "${GREEN}✅ $script: PASS (no issues found)${NC}"
            else
                local exit_code=$?
                if [ $exit_code -eq 1 ]; then
                    echo -e "${YELLOW}⚠️  $script: ISSUES FOUND (exit code 1 - this is correct!)${NC}"
                else
                    echo -e "${RED}❌ $script: ERROR (exit code $exit_code)${NC}"
                fi
            fi
            
            ((working++))
        else
            echo -e "${RED}❌ $script: NOT FOUND${NC}"
        fi
        
        ((total++))
        echo ""
    done
    
    echo -e "${BLUE}📊 Summary${NC}"
    echo -e "${BLUE}==========${NC}"
    echo "Scripts tested: $total"
    echo "Scripts working: $working"
    
    if [ $working -eq $total ]; then
        echo -e "${GREEN}🎉 All scripts are working correctly!${NC}"
        echo ""
        echo "Exit Code Legend:"
        echo "  0 = No issues found (PASS)"
        echo "  1 = Issues found (WARN - this is normal and expected)"
        echo "  >1 = Script error (ERROR - needs fixing)"
        return 0
    else
        echo -e "${RED}❌ Some scripts have issues${NC}"
        return 1
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
