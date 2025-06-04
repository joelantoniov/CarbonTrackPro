#!/bin/bash

set -e

echo "Setting up CarbonTrack Pro Infrastructure..."

check_dependencies() {
    echo "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        echo "Docker not found. Please install Docker."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 not found. Please install Python 3.9+."
        exit 1
    fi
    
    echo "All dependencies found!"
}

setup_environment() {
    echo "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "Created .env file. Please configure with your settings."
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "Environment setup complete!"
}

setup_kafka() {
    echo "Setting up Kafka..."
    
    docker-compose up -d zookeeper kafka
    
    sleep 30
    
    docker-compose exec kafka kafka-topics.sh \
        --create \
        --topic emissions_topic \
        --bootstrap-server localhost:9092 \
        --partitions 3 \
        --replication-factor 1
    
    echo "✅ Kafka setup complete!"
}

setup_database() {
    echo "Setting up database schema..."
    
    if [ -n "$AZURE_SQL_SERVER" ]; then
        echo "Azure SQL Database detected. Please run sql/schema.sql manually."
    else
        echo "No database configuration found. Please configure Azure SQL."
    fi
    
    echo "Database setup instructions provided!"
}

main() {
    echo "CarbonTrack Pro Infrastructure Setup"
    echo "======================================"
    
    check_dependencies
    setup_environment
    setup_kafka
    setup_database
    
    echo ""
    echo "Setup Complete!"
    echo "=================="
    echo "Next steps:"
    echo "1. Configure .env file with your Azure credentials"
    echo "2. Run database schema: sql/schema.sql"
    echo "3. Start services: make start"
    echo "4. Run pipeline: make run-pipeline"
    echo ""
    echo "Access URLs:"
    echo "- Airflow UI: http://localhost:8080"
    echo "- Spark UI: http://localhost:8081"
    echo ""
}

main "$@"
