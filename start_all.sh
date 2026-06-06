#!/bin/bash

cd "/c/Users/hante/OneDrive/Desktop/Ilgamrabota/delivery-integration"

echo "🚀 Запуск Dispatcher (порт 5001)..."
python module_a_dispatcher.py &
sleep 2

echo "🚀 Запуск Tracking (порт 5002)..."
python module_b_tracking.py &
sleep 2

echo "🚀 Запуск Notify (порт 5003)..."
python module_c_notify.py &

echo ""
echo "✅ Все сервисы запущены!"
echo "   http://localhost:5001 - Dispatcher"
echo "   http://localhost:5002 - Tracking"
echo "   http://localhost:5003 - Notify"
echo ""
echo "⚠️  Нажмите Ctrl+C для остановки всех сервисов"

wait
