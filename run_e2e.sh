#!/bin/bash

cd "/c/Users/hante/OneDrive/Desktop/Ilgamrabota/delivery-integration"

echo "=========================================="
echo "Running End-to-End Delivery Scenario"
echo "=========================================="

# Check if services are running
echo "Checking services..."

if curl -s http://localhost:5001/couriers > /dev/null; then
    echo "✓ Dispatcher (5001) is running"
else
    echo "✗ Dispatcher is not running"
    exit 1
fi

if curl -s http://localhost:5002/track/demo_123 > /dev/null 2>&1; then
    echo "✓ Tracking (5002) is running"
else
    echo "✗ Tracking is not running"
fi

if curl -s http://localhost:5003/notifications > /dev/null 2>&1; then
    echo "✓ Notify (5003) is running"
else
    echo "✗ Notify is not running"
fi

echo ""
echo "Running E2E scenario..."
python e2e_scenario.py

echo ""
echo "E2E scenario completed!"
