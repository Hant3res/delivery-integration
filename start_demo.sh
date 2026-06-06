#!/bin/bash

echo "=========================================="
echo "Starting Delivery Integration Demo"
echo "=========================================="

cd "/c/Users/hante/OneDrive/Desktop/Ilgamrabota/delivery-integration"

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null

# Build and start
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 10

# Check services
echo ""
echo "=========================================="
echo "Service Status"
echo "=========================================="
docker-compose ps

echo ""
echo "=========================================="
echo "Testing Endpoints"
echo "=========================================="

# Test Dispatcher
echo -n "Dispatcher (5001): "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/couriers
echo ""

# Test Tracking
echo -n "Tracking (5002): "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/track/demo_123
echo ""

# Test Notify
echo -n "Notify (5003): "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5003/notifications
echo ""

# Test Frontend
echo -n "Frontend (80): "
curl -s -o /dev/null -w "%{http_code}" http://localhost
echo ""

echo ""
echo "=========================================="
echo "Demo Environment Ready!"
echo "=========================================="
echo ""
echo "Access the system:"
echo "  - Frontend UI:    http://localhost"
echo "  - Dispatcher API: http://localhost:5001"
echo "  - Tracking API:   http://localhost:5002"
echo "  - Notify API:     http://localhost:5003"
echo ""
echo "Run tests: python run_tests.py"
echo "Stop demo: docker-compose down"
echo "=========================================="
