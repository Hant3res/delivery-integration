#!/bin/bash

cd "/c/Users/hante/OneDrive/Desktop/Ilgamrabota/delivery-integration"

echo "Starting all services..."

# Start dispatcher
python module_a_dispatcher.py &
sleep 2

# Start tracking
python module_b_tracking.py &
sleep 2

# Start notify
python module_c_notify.py &
sleep 2

echo "All services started. Running orchestrator..."

# Run orchestrator
python orchestrator.py

echo "System test completed. Check orchestrator.log for details."
