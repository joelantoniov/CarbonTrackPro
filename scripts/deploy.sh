#!/bin/bash

set -e

ENVIRONMENT=${1:-production}

echo "Deploying CarbonTrack Pro to $ENVIRONMENT..."

validate_environment() {
    echo "🔍 Validating environment..."
    
    if [ ! -f ".env" ]; then
        echo ".env file not found!"
        exit 1
    fi
    
    source .env
    
    required_vars=(
        "KAFKA_BOOTSTRAP_SERVERS"
        "AZURE_SQL_SERVER"
        "AZURE_SQL_DATABASE"
        "DATABRICKS_HOST"
        "DATABRICKS_TOKEN"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "Required environment variable $var not set!"
            exit 1
        fi
    done
    
    echo "Environment validation passed!"
}

run_tests() {
    echo "Running tests..."
    
    python -m pytest tests/ -v
    
    echo "All tests passed!"
}

build_images() {
    echo "Building Docker images..."
    
    docker-compose build --no-cache
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker tag carbon-track-pro:latest carbon-track-pro:$(git rev-parse --short HEAD)
        docker tag carbon-track-pro:latest carbon-track-pro:production
    fi
    
    echo "Images built successfully!"
}

deploy_services() {
    echo "Deploying services..."
    
    docker-compose down
    docker-compose up -d
    
    echo "Waiting for services to be ready..."
    sleep 30
    
    health_check
    
    echo "Services deployed successfully!"
}

health_check() {
    echo "Performing health checks..."
    
    services=(
        "http://localhost:8080/health:Airflow"
        "http://localhost:8081:Spark"
    )
    
    for service in "${services[@]}"; do
        url=$(echo $service | cut -d: -f1-2)
        name=$(echo $service | cut -d: -f3)
        
        if curl -f -s "$url" > /dev/null; then
            echo "$name is healthy"
        else
            echo "$name is not responding"
            exit 1
        fi
    done
}

main() {
    echo "CarbonTrack Pro Deployment"
    echo "============================"
    
    validate_environment
    run_tests
    build_images
    deploy_services
    
    echo ""
    echo "Deployment Complete!"
    echo "======================"
    echo "Environment: $ENVIRONMENT"
    echo "Timestamp: $(date)"
    echo "Commit: $(git rev-parse --short HEAD)"
    echo ""
    echo "Access URLs:"
    echo "- Airflow UI: http://localhost:8080"
    echo "- Spark UI: http://localhost:8081"
    echo ""
}

main "$@"
