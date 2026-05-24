#!/bin/bash

# Stock Replenishment System - Docker Startup Script

set -e

echo "================================================"
echo "Stock Replenishment System - Docker Deployment"
echo "================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it and add your API keys:"
    echo "   - GROQ_API_KEY"
    echo "   - OPENROUTER_API_KEY"
    echo ""
    read -p "Press Enter after updating .env file to continue..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Error: Docker Compose is not available"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Docker Compose found: $($COMPOSE_CMD version --short 2>/dev/null || echo 'installed')"
echo ""

# Parse command line arguments
COMMAND=${1:-up}

case $COMMAND in
    up)
        echo "🚀 Building and starting services..."
        $COMPOSE_CMD up --build -d
        echo ""
        echo "✅ Services started successfully!"
        echo ""
        echo "📊 Service Status:"
        $COMPOSE_CMD ps
        echo ""
        echo "🌐 Access the application:"
        echo "   Frontend: http://localhost"
        echo "   Backend API: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📝 View logs with: $COMPOSE_CMD logs -f"
        echo "🛑 Stop services with: $COMPOSE_CMD stop"
        ;;
    
    down)
        echo "🛑 Stopping and removing services..."
        $COMPOSE_CMD down
        echo "✅ Services stopped and removed"
        ;;
    
    logs)
        echo "📝 Showing logs (Ctrl+C to exit)..."
        $COMPOSE_CMD logs -f
        ;;
    
    restart)
        echo "🔄 Restarting services..."
        $COMPOSE_CMD restart
        echo "✅ Services restarted"
        ;;
    
    status)
        echo "📊 Service Status:"
        $COMPOSE_CMD ps
        ;;
    
    build)
        echo "🔨 Building images..."
        $COMPOSE_CMD build
        echo "✅ Build complete"
        ;;
    
    *)
        echo "Usage: $0 {up|down|logs|restart|status|build}"
        echo ""
        echo "Commands:"
        echo "  up       - Build and start services (default)"
        echo "  down     - Stop and remove services"
        echo "  logs     - View service logs"
        echo "  restart  - Restart services"
        echo "  status   - Show service status"
        echo "  build    - Build Docker images"
        exit 1
        ;;
esac
