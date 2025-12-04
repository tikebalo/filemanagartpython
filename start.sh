#!/bin/bash

echo "🚀 Starting FileManager Pro..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo ""
fi

# Check if Docker is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    echo "Please install Docker and docker-compose first"
    exit 1
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 5

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T backend python init_db.py

echo ""
echo "✅ FileManager Pro is running!"
echo ""
echo "📱 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "🔑 Default credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "⚠️  Please change the password after first login!"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f    # View logs"
echo "   docker-compose down       # Stop services"
echo "   docker-compose restart    # Restart services"
echo ""
