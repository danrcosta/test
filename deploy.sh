#!/bin/bash

#############################################################################
# Telegram + Hermes + Claude Code Integration - Deployment Script
#############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="telegram-hermes-integration"
DOCKER_IMAGE="$PROJECT_NAME:latest"
CONTAINER_NAME="telegram-hermes-webhook"
WEBHOOK_PORT=8000

# Functions
log_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    log_success "All requirements met"
}

check_env_file() {
    log_info "Checking .env file..."

    if [ ! -f .env ]; then
        log_warning ".env file not found"
        log_info "Creating .env from .env.example..."

        if [ -f .env.example ]; then
            cp .env.example .env
            log_success ".env file created from template"
            log_warning "Please edit .env with your actual values!"
            read -p "Press enter to continue..."
        else
            log_error ".env.example not found"
            exit 1
        fi
    else
        log_success ".env file found"
    fi
}

build_docker_image() {
    log_info "Building Docker image..."

    docker build -t $DOCKER_IMAGE \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .

    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

start_containers() {
    log_info "Starting containers..."

    docker-compose up -d

    if [ $? -eq 0 ]; then
        log_success "Containers started successfully"
    else
        log_error "Failed to start containers"
        exit 1
    fi
}

wait_for_webhook() {
    log_info "Waiting for webhook server to be ready..."

    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$WEBHOOK_PORT/health > /dev/null 2>&1; then
            log_success "Webhook server is healthy"
            return 0
        fi

        echo -ne "${BLUE}Attempt $attempt/$max_attempts...${NC}\r"
        sleep 1
        ((attempt++))
    done

    log_error "Webhook server did not become healthy in time"
    return 1
}

configure_webhook() {
    log_info "Configuring Telegram webhook..."

    if [ -z "$WEBHOOK_URL" ]; then
        log_warning "WEBHOOK_URL not set in .env"
        log_info "For local testing, use ngrok:"
        echo -e "${YELLOW}  ngrok http 8000${NC}"
        echo -e "${YELLOW}  Then set WEBHOOK_URL in .env${NC}"
        return 0
    fi

    log_info "Setting webhook to: $WEBHOOK_URL/webhook/telegram"

    curl -X POST "http://localhost:$WEBHOOK_PORT/set-webhook?webhook_url=$WEBHOOK_URL/webhook/telegram"

    if [ $? -eq 0 ]; then
        log_success "Webhook configured successfully"
    else
        log_warning "Webhook configuration returned an error (may be expected if running locally)"
    fi
}

show_status() {
    log_info "Container Status:"
    docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}"

    log_info "Logs:"
    docker logs --tail 10 $CONTAINER_NAME 2>/dev/null || log_warning "Could not retrieve logs"
}

show_info() {
    echo ""
    log_info "═══════════════════════════════════════════════════════"
    log_success "Deployment completed successfully! 🚀"
    log_info "═══════════════════════════════════════════════════════"
    echo ""

    echo -e "${GREEN}📍 Webhook URL: http://localhost:$WEBHOOK_PORT${NC}"
    echo -e "${GREEN}🏥 Health Check: http://localhost:$WEBHOOK_PORT/health${NC}"
    echo -e "${GREEN}📝 Logs: docker logs -f $CONTAINER_NAME${NC}"
    echo ""

    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Configure .env with your Telegram bot token"
    echo "2. For local testing, use ngrok: ngrok http $WEBHOOK_PORT"
    echo "3. Update WEBHOOK_URL in .env with ngrok URL"
    echo "4. Send test message to @Danrcbh_bot on Telegram"
    echo "5. Monitor logs: docker logs -f $CONTAINER_NAME"
    echo ""
}

main() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Telegram + Hermes Integration Deployment           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_requirements
    check_env_file

    log_info "Building and deploying application..."
    echo ""

    build_docker_image
    start_containers

    if wait_for_webhook; then
        configure_webhook
        show_status
        show_info
    else
        log_error "Deployment failed - webhook server unhealthy"
        docker-compose logs
        exit 1
    fi
}

# Handle cleanup on exit
cleanup() {
    log_info "Cleaning up..."
}

trap cleanup EXIT

# Run main
main
