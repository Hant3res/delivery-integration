#!/bin/bash

echo "Запуск модуля Dispatcher (порт 5001)..."
cd module_a_dispatcher
python app.py &
cd ..

echo "Запуск модуля Tracking (порт 5002)..."
cd module_b_tracking
python app.py &
cd ..

echo "Запуск модуля Notify (порт 5003)..."
cd module_c_notify
python app.py &
cd ..

echo "Все модули запущены!"
echo "Dispatcher: http://localhost:5001"
echo "Tracking: http://localhost:5002"
echo "Notify: http://localhost:5003"

wait
