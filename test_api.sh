#!/bin/bash

echo "=== 1. Тест Dispatcher - назначить доставку ==="
curl -X POST http://localhost:5001/assign \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-123","address":"Москва, Красная пл., 1","recipient_phone":"+79001234567"}' \
  -w "\n\n"

echo "=== 2. Тест Tracking - обновить локацию ==="
curl -X POST http://localhost:5002/track/update \
  -H "Content-Type: application/json" \
  -d '{"task_id":"demo_123","lat":55.7558,"lng":37.6173}' \
  -w "\n\n"

echo "=== 3. Тест Tracking - получить статус ==="
curl http://localhost:5002/track/demo_123 -w "\n\n"

echo "=== 4. Тест Notify - отправить уведомление ==="
curl -X POST http://localhost:5003/notify \
  -H "Content-Type: application/json" \
  -d '{"recipient":"+79001234567","type":"sms","message":"Ваш заказ в пути!","order_id":"ORD-123"}' \
  -w "\n\n"

echo "=== 5. Тест Notify - список уведомлений ==="
curl http://localhost:5003/notifications -w "\n\n"

echo "=== 6. Тест Tracking - завершить доставку ==="
curl -X POST http://localhost:5002/track/complete \
  -H "Content-Type: application/json" \
  -d '{"task_id":"demo_123","proof":"code_123456"}' \
  -w "\n\n"

echo "=== 7. Тест Tracking - финальный статус ==="
curl http://localhost:5002/track/demo_123 -w "\n\n"

echo "=== 8. Тест Dispatcher - список курьеров ==="
curl http://localhost:5001/couriers -w "\n"
