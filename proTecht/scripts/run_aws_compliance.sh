#!/bin/bash
# AWS Compliance Execution Script for proTecht
# This script runs the complete AWS compliance workflow

set -euo pipefail

# Configuration
PROFILE="tanmay_modi"
REGION="us-east-1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS credentials are configured
check_aws_credentials() {
    log_info "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity --profile "$PROFILE" >/dev/null 2>&1; then
        log_error "AWS credentials not configured for profile: $PROFILE"
        log_error "Please run: aws configure --profile $PROFILE"
        exit 1
    fi
    
    log_success "AWS credentials verified for profile: $PROFILE"
}

# Check if Python virtual environment exists
check_python_env() {
    log_info "Checking Python environment..."
    
    if [ ! -d "$PROJECT_DIR/.venv" ]; then
        log_error "Python virtual environment not found"
        log_error "Please run: cd $PROJECT_DIR && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    
    log_success "Python virtual environment found"
}

# Check if proTecht services are running
check_services() {
    log_info "Checking proTecht services..."
    
    # Check API server
    if ! curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        log_warning "proTecht API server not running on port 8000"
        log_info "Starting API server in background..."
        cd "$PROJECT_DIR"
        source .venv/bin/activate
        nohup python src/api_server.py > /tmp/protecht_api.log 2>&1 &
        sleep 5
    else
        log_success "proTecht API server is running"
    fi
    
    # Check frontend
    if ! curl -s http://localhost:5173 >/dev/null 2>&1; then
        log_warning "proTecht frontend not running on port 5173"
        log_info "Starting frontend in background..."
        cd "$PROJECT_DIR/Frontend"
        nohup npm run dev > /tmp/protecht_frontend.log 2>&1 &
        sleep 5
    else
        log_success "proTecht frontend is running"
    fi
}

# Run AWS compliance deployment
run_deployment() {
    log_info "Starting AWS compliance deployment..."
    
    cd "$PROJECT_DIR"
    source .venv/bin/activate
    
    # Run the deployment script
    python scripts/deploy_aws_compliance.py \
        --profile "$PROFILE" \
        --region "$REGION"
    
    if [ $? -eq 0 ]; then
        log_success "AWS compliance deployment completed successfully!"
    else
        log_error "AWS compliance deployment failed!"
        exit 1
    fi
}

# Show deployment summary
show_summary() {
    log_info "Deployment Summary:"
    echo "  - AWS Profile: $PROFILE"
    echo "  - AWS Region: $REGION"
    echo "  - API Server: http://localhost:8000"
    echo "  - Frontend: http://localhost:5173"
    echo "  - Logs: /tmp/aws_compliance_*.log"
    echo ""
    log_info "Next steps:"
    echo "  1. Open http://localhost:5173 to view compliance dashboard"
    echo "  2. Check /tmp/aws_compliance_deployment_report_*.json for detailed results"
    echo "  3. Monitor AWS services for compliance improvements"
}

# Main execution
main() {
    log_info "🚀 Starting proTecht AWS Compliance Deployment"
    echo "=================================================="
    
    # Pre-flight checks
    check_aws_credentials
    check_python_env
    check_services
    
    # Run deployment
    run_deployment
    
    # Show summary
    show_summary
    
    log_success "🎉 All done! Your AWS environment is now compliant with FedRAMP AC controls."
}

# Handle script arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Usage: $0 [help|deploy|analyze|implement|verify]"
        echo ""
        echo "Commands:"
        echo "  help      - Show this help message"
        echo "  deploy    - Run complete deployment (default)"
        echo "  analyze   - Run AWS analysis only"
        echo "  implement - Run AWS implementation only"
        echo "  verify    - Run compliance verification only"
        echo ""
        echo "Environment variables:"
        echo "  AWS_PROFILE - AWS profile to use (default: tanmay_modi)"
        echo "  AWS_REGION  - AWS region to use (default: us-east-1)"
        exit 0
        ;;
    "analyze")
        log_info "Running AWS analysis only..."
        cd "$PROJECT_DIR"
        source .venv/bin/activate
        python scripts/aws_background_agent.py --profile "$PROFILE" --region "$REGION"
        ;;
    "implement")
        log_info "Running AWS implementation only..."
        cd "$PROJECT_DIR"
        source .venv/bin/activate
        python scripts/implement_aws_recommendations.py --profile "$PROFILE" --region "$REGION"
        ;;
    "verify")
        log_info "Running compliance verification only..."
        cd "$PROJECT_DIR"
        source .venv/bin/activate
        python scripts/aws_background_agent.py --profile "$PROFILE" --region "$REGION"
        ;;
    "deploy"|"")
        main
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
