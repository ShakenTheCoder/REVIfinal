#!/bin/bash

echo "🚀 REVI Setup Script"
echo "===================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🏗️  Building Docker images..."
echo "⚠️  First build will download AI models (~1GB). This may take 5-10 minutes."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if [ "$(docker ps -q -f name=revi-postgres)" ]; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL failed to start"
fi

if [ "$(docker ps -q -f name=revi-backend)" ]; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
fi

if [ "$(docker ps -q -f name=revi-frontend)" ]; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 REVI is ready!"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
