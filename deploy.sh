#!/bin/bash

# MCP Weather Server Deployment Script

set -e

echo "🚀 Starting MCP Weather Server deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (plugin or standalone)
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Determine which Docker Compose command to use
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenWeatherMap API key"
    echo "   You can get a free API key from: https://openweathermap.org/api"
    read -p "Press enter to continue after updating .env file..."
fi

# Create logs directory
mkdir -p logs

# Build and start the container
echo "🏗️  Building Docker image..."
$DOCKER_COMPOSE build

echo "🌟 Starting MCP Weather Server..."
$DOCKER_COMPOSE up -d

# Wait for health check
echo "⏳ Waiting for server to be healthy..."
sleep 10

# Check if server is running
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo "✅ MCP Weather Server is running!"
    echo "🌐 Server is accessible at: http://localhost:8124"
    echo "📊 Health check: http://localhost:8124/health"
    echo "📋 Server info: Use get_server_info tool"
    echo ""
    echo "Available MCP tools:"
    echo "  - get_weather(city)"
    echo "  - get_forecast(city, days)"
    echo "  - get_weather_alerts(city)"
    echo "  - compare_cities_weather(city1, city2)"
    echo "  - get_current_time()"
    echo "  - echo_message(message)"
    echo "  - add_numbers(a, b)"
    echo ""
    echo "🔧 To view logs: $DOCKER_COMPOSE logs -f"
    echo "🛑 To stop: $DOCKER_COMPOSE down"
else
    echo "❌ Failed to start MCP Weather Server"
    echo "📋 Check logs: $DOCKER_COMPOSE logs"
    exit 1
fi