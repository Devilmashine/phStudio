#!/bin/bash

# Security Audit Script
# Скрипт для проведения security audit

set -e

echo "🔒 Starting Security Audit for Photo Studio CRM..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "ℹ️  $message${NC}"
            ;;
    esac
}

# Check if required tools are installed
check_dependencies() {
    print_status "INFO" "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v bandit &> /dev/null; then
        missing_deps+=("bandit")
    fi
    
    if ! command -v safety &> /dev/null; then
        missing_deps+=("safety")
    fi
    
    if ! command -v semgrep &> /dev/null; then
        missing_deps+=("semgrep")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_status "ERROR" "Missing dependencies: ${missing_deps[*]}"
        print_status "INFO" "Install missing dependencies and run again"
        exit 1
    fi
    
    print_status "SUCCESS" "All dependencies are installed"
}

# Backend Security Checks
backend_security_check() {
    print_status "INFO" "Running backend security checks..."
    
    cd backend
    
    # Bandit - Python security linter
    print_status "INFO" "Running Bandit security scan..."
    if bandit -r app/ -f json -o bandit-report.json; then
        print_status "SUCCESS" "Bandit scan completed"
    else
        print_status "WARNING" "Bandit found potential security issues"
    fi
    
    # Safety - Check for known security vulnerabilities
    print_status "INFO" "Running Safety check..."
    if safety check --json --output safety-report.json; then
        print_status "SUCCESS" "Safety check passed"
    else
        print_status "WARNING" "Safety found vulnerable packages"
    fi
    
    # Semgrep - Static analysis
    print_status "INFO" "Running Semgrep analysis..."
    if semgrep --config=auto app/ --json --output=semgrep-report.json; then
        print_status "SUCCESS" "Semgrep analysis completed"
    else
        print_status "WARNING" "Semgrep found potential issues"
    fi
    
    # Check for hardcoded secrets
    print_status "INFO" "Checking for hardcoded secrets..."
    if grep -r -i "password\|secret\|key\|token" app/ --exclude-dir=__pycache__ | grep -v "password_hash\|secret_key" | grep -v "test"; then
        print_status "WARNING" "Potential hardcoded secrets found"
    else
        print_status "SUCCESS" "No hardcoded secrets detected"
    fi
    
    cd ..
}

# Frontend Security Checks
frontend_security_check() {
    print_status "INFO" "Running frontend security checks..."
    
    cd frontend
    
    # npm audit
    print_status "INFO" "Running npm audit..."
    if npm audit --audit-level=moderate; then
        print_status "SUCCESS" "npm audit passed"
    else
        print_status "WARNING" "npm audit found vulnerabilities"
    fi
    
    # Check for hardcoded secrets in frontend
    print_status "INFO" "Checking for hardcoded secrets in frontend..."
    if grep -r -i "api_key\|secret\|password" src/ --exclude-dir=node_modules | grep -v "process.env"; then
        print_status "WARNING" "Potential hardcoded secrets found in frontend"
    else
        print_status "SUCCESS" "No hardcoded secrets detected in frontend"
    fi
    
    cd ..
}

# Docker Security Checks
docker_security_check() {
    print_status "INFO" "Running Docker security checks..."
    
    # Check Dockerfile security best practices
    print_status "INFO" "Checking Dockerfile security..."
    
    # Check if running as root
    if grep -r "USER root" backend/Dockerfile* frontend/Dockerfile*; then
        print_status "WARNING" "Dockerfiles may be running as root"
    else
        print_status "SUCCESS" "Dockerfiles use non-root users"
    fi
    
    # Check for latest base images
    if grep -r "FROM.*:latest" backend/Dockerfile* frontend/Dockerfile*; then
        print_status "WARNING" "Using 'latest' tag in Dockerfiles"
    else
        print_status "SUCCESS" "Dockerfiles use specific versions"
    fi
}

# Configuration Security Checks
config_security_check() {
    print_status "INFO" "Running configuration security checks..."
    
    # Check for default passwords
    if grep -r "password.*=.*password\|secret.*=.*secret" . --exclude-dir=node_modules --exclude-dir=.git; then
        print_status "WARNING" "Default passwords detected in configuration"
    else
        print_status "SUCCESS" "No default passwords found"
    fi
    
    # Check for exposed ports
    if grep -r "EXPOSE.*80\|EXPOSE.*443\|EXPOSE.*22" backend/Dockerfile* frontend/Dockerfile*; then
        print_status "INFO" "Standard ports exposed (review if necessary)"
    fi
    
    # Check for debug mode in production
    if grep -r "DEBUG.*=.*True\|debug.*=.*true" . --exclude-dir=node_modules --exclude-dir=.git; then
        print_status "WARNING" "Debug mode may be enabled"
    else
        print_status "SUCCESS" "Debug mode not detected"
    fi
}

# Generate Security Report
generate_report() {
    print_status "INFO" "Generating security report..."
    
    local report_file="security-audit-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$report_file" << EOF
# Security Audit Report

**Date:** $(date)
**Project:** Photo Studio CRM
**Auditor:** Automated Security Script

## Summary

This report contains the results of the automated security audit.

## Backend Security

### Bandit Results
\`\`\`json
$(cat backend/bandit-report.json 2>/dev/null || echo "No report generated")
\`\`\`

### Safety Results
\`\`\`json
$(cat backend/safety-report.json 2>/dev/null || echo "No report generated")
\`\`\`

### Semgrep Results
\`\`\`json
$(cat backend/semgrep-report.json 2>/dev/null || echo "No report generated")
\`\`\`

## Frontend Security

### npm audit Results
\`\`\`
$(npm audit --audit-level=moderate 2>/dev/null || echo "No audit results")
\`\`\`

## Recommendations

1. Review all warnings and errors above
2. Update vulnerable dependencies
3. Implement security headers
4. Enable HTTPS in production
5. Regular security audits

## Next Steps

- [ ] Fix critical vulnerabilities
- [ ] Update dependencies
- [ ] Implement security monitoring
- [ ] Schedule regular audits

EOF

    print_status "SUCCESS" "Security report generated: $report_file"
}

# Main execution
main() {
    print_status "INFO" "Starting comprehensive security audit..."
    
    check_dependencies
    backend_security_check
    frontend_security_check
    docker_security_check
    config_security_check
    generate_report
    
    print_status "SUCCESS" "Security audit completed!"
    print_status "INFO" "Review the generated report for detailed findings"
}

# Run main function
main "$@"
