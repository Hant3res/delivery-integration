#!/bin/bash

cd "/c/Users/hante/OneDrive/Desktop/Ilgamrabota/delivery-integration"

echo "Stopping all modules..."
taskkill //F //IM python.exe 2>/dev/null
sleep 2

echo "Resetting database..."
if [ -f delivery.db ]; then
    python -c "
import sqlite3
try:
    conn = sqlite3.connect('delivery.db')
    conn.execute('UPDATE couriers SET available = 1')
    conn.commit()
    print('✓ Couriers reset to available')
except Exception as e:
    print(f'Error: {e}')
    conn = sqlite3.connect('delivery.db')
    conn.execute('UPDATE couriers SET available = 1')
    conn.commit()
    print('✓ Couriers reset')
conn.close()
"
else
    echo "No database found, will be created on startup"
fi

echo ""
echo "Starting modules..."
python module_a_dispatcher.py &
sleep 2
python module_b_tracking.py &
sleep 2
python module_c_notify.py &
sleep 3

echo ""
echo "✅ All modules started!"
echo "   http://localhost:5001 - Dispatcher"
echo "   http://localhost:5002 - Tracking"
echo "   http://localhost:5003 - Notify"
echo ""

echo "Checking couriers status:"
curl -s http://localhost:5001/couriers | head -5

echo ""
echo "Now run: python run_tests.py"
