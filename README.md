# Delivery Integration System

## Last Mile Delivery Management Platform

[![CI/CD](https://github.com/Hant3res/delivery-integration/actions/workflows/ci.yml/badge.svg)](https://github.com/Hant3res/delivery-integration/actions)

## Overview

This project implements a complete **Last Mile Delivery Integration System** with microservices architecture. The system manages the entire delivery lifecycle from courier assignment to final delivery confirmation.

## Architecture

┌─────────────────────────────────────────────────────────────────┐
│ Client Browser │
│ http://localhost │
└─────────────────────────────┬───────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ Nginx (Port 80) │
│ Frontend UI │
└─────────────────────────────┬───────────────────────────────────┘
│
┌─────────────────────┼─────────────────────┐
│ │ │
▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Dispatcher │ │ Tracking │ │ Notify │
│ (Port 5001) │ │ (Port 5002) │ │ (Port 5003) │
│ Module A │ │ Module B │ │ Module C │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
│ │ │
└────────────────────┼────────────────────┘
│
▼
┌─────────────────┐
│ SQLite DB │
│ delivery.db │
└─────────────────┘

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Flask |
| Database | SQLite, SQLAlchemy |
| Frontend | HTML5, Bootstrap 5, JavaScript |
| Container | Docker, Docker Compose |
| Testing | unittest, pytest |
| Logging | Structured JSON logging |
| Resilience | Retry pattern, Circuit Breaker |

## Modules

### Module A: Dispatcher (Port 5001)
- `POST /assign` - Assign courier to delivery
- `GET /couriers` - List all couriers
- `GET /deliveries` - List all deliveries
- `GET /status/<task_id>` - Get delivery status

### Module B: Tracking (Port 5002)
- `POST /track/update` - Update courier location
- `GET /track/<task_id>` - Get tracking information
- `POST /track/complete` - Complete delivery

### Module C: Notify (Port 5003)
- `POST /notify` - Send notification
- `GET /notifications` - List all notifications
- `GET /notify/order/<order_id>` - Get notifications by order

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/Hant3res/delivery-integration.git
cd delivery-integration

# Install dependencies
pip install -r requirements.txt

# Start modules (3 terminal windows)
python module_a_dispatcher.py    # Terminal 1
python module_b_tracking.py      # Terminal 2
python module_c_notify.py        # Terminal 3

# Open frontend (Terminal 4)
cd frontend && python -m http.server 8080

# Access application
open http://localhost:8080
# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
API Examples
Create Delivery
curl -X POST http://localhost:5001/assign \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-001","address":"Moscow, Red Square","recipient_phone":"+79001234567"}'
Response:


{
  "task_id": "a1b2c3d4",
  "courier_name": "Ivan",
  "status": "assigned"
}
Update Tracking

curl -X POST http://localhost:5002/track/update \
  -H "Content-Type: application/json" \
  -d '{"task_id":"a1b2c3d4","lat":55.7558,"lng":37.6173}'
Complete Delivery
curl -X POST http://localhost:5002/track/complete \
  -H "Content-Type: application/json" \
  -d '{"task_id":"a1b2c3d4","proof":"DELIVERY_CODE"}'
Send Notification
curl -X POST http://localhost:5003/notify \
  -H "Content-Type: application/json" \
  -d '{"recipient":"+79001234567","message":"Order delivered!","order_id":"ORD-001"}'
Testing
# Run all tests
python run_tests.py

# Run specific test suites
python -m unittest discover tests/unit -v
python -m unittest discover tests/integration -v
python -m unittest discover tests/e2e -v
Performance Optimization
Endpoint	Before	After	Improvement
GET /couriers	~50ms	~5ms	90% faster
In-memory caching with TTL (10 seconds)

Cache invalidation on data changes

Parallel request handling

Error Handling
Retry pattern - 3 attempts with exponential backoff

Circuit Breaker - Opens after 3 failures, recovers in 30s

Structured logging - JSON format with timestamps

Validation - Phone number, order ID, address

Project Structure
delivery-integration/
├── module_a_dispatcher.py    # Dispatcher service
├── module_b_tracking.py      # Tracking service
├── module_c_notify.py        # Notify service
├── database/
│   └── models.py             # SQLAlchemy models
├── frontend/
│   └── index.html            # Web UI
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── docker-compose.yml        # Docker orchestration
├── requirements.txt          # Python dependencies
└── .github/workflows/        # CI/CD pipeline
CI/CD Pipeline
GitHub Actions automatically:

Runs unit, integration, and E2E tests

Checks code syntax with flake8

Builds Docker images

Validates API responses

Monitoring
Logs: Structured JSON in logs/ directory

Performance: Timing metrics in console

Health: Endpoint status monitoring

Contributors
Hant3res - Lead Developer

License
This project is for educational purposes.

Links
GitHub Repository

Documentation

---

## 3. OpenAPI/Swagger документация

```bash
cat > openapi.yaml << 'EOF'
openapi: 3.0.0
info:
  title: Delivery Integration API
  description: |
    Last Mile Delivery Management System API
    
    ## Overview
    This API provides endpoints for managing delivery operations:
    - **Dispatcher** - Courier assignment and delivery management
    - **Tracking** - Real-time courier tracking
    - **Notify** - Notification service
    
    ## Authentication
    No authentication required for development.
    
    ## Error Handling
    - 400: Bad Request - Invalid input
    - 404: Not Found - Resource doesn't exist
    - 500: Internal Server Error
  version: 2.0.0
  contact:
    name: Hant3res
    email: rauhwelt4@gmail.com

servers:
  - url: http://localhost:5001
    description: Dispatcher Service
  - url: http://localhost:5002
    description: Tracking Service
  - url: http://localhost:5003
    description: Notify Service

tags:
  - name: Dispatcher
    description: Courier and delivery management
  - name: Tracking
    description: Real-time delivery tracking
  - name: Notify
    description: Notification management

paths:
  # Dispatcher endpoints
  /assign:
    post:
      tags: [Dispatcher]
      summary: Assign courier to delivery
      operationId: assignDelivery
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AssignRequest'
            example:
              order_id: "ORD-001"
              address: "Moscow, Red Square, 1"
              recipient_phone: "+79001234567"
      responses:
        '200':
          description: Delivery assigned successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AssignResponse'
              example:
                task_id: "a1b2c3d4"
                courier_name: "Ivan"
                status: "assigned"
        '400':
          description: Missing required fields
        '503':
          description: No available couriers

  /couriers:
    get:
      tags: [Dispatcher]
      summary: Get all couriers
      operationId: listCouriers
      responses:
        '200':
          description: List of couriers
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Courier'
              example:
                - id: "courier_1"
                  name: "Ivan"
                  available: true
                  location: "Moscow"

  /deliveries:
    get:
      tags: [Dispatcher]
      summary: Get all deliveries
      operationId: listDeliveries
      responses:
        '200':
          description: List of deliveries
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Delivery'

  /status/{task_id}:
    get:
      tags: [Dispatcher]
      summary: Get delivery status
      operationId: getDeliveryStatus
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
          description: Unique task identifier
      responses:
        '200':
          description: Delivery status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DeliveryStatus'

  # Tracking endpoints
  /track/update:
    post:
      tags: [Tracking]
      summary: Update courier location
      operationId: updateLocation
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LocationUpdate'
            example:
              task_id: "a1b2c3d4"
              lat: 55.7558
              lng: 37.6173
      responses:
        '200':
          description: Location updated
          content:
            application/json:
              example:
                message: "Location updated"

  /track/{task_id}:
    get:
      tags: [Tracking]
      summary: Get tracking information
      operationId: getTracking
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Tracking information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TrackingInfo'

  /track/complete:
    post:
      tags: [Tracking]
      summary: Complete delivery
      operationId: completeDelivery
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CompleteRequest'
            example:
              task_id: "a1b2c3d4"
              proof: "DELIVERY_CODE_123"
      responses:
        '200':
          description: Delivery completed
          content:
            application/json:
              example:
                message: "Delivery completed"
                status: "delivered"

  # Notify endpoints
  /notify:
    post:
      tags: [Notify]
      summary: Send notification
      operationId: sendNotification
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/NotificationRequest'
            example:
              recipient: "+79001234567"
              type: "sms"
              message: "Your order has been delivered!"
              order_id: "ORD-001"
      responses:
        '200':
          description: Notification sent
          content:
            application/json:
              example:
                message: "Notification sent"
                notification_id: 1

  /notifications:
    get:
      tags: [Notify]
      summary: Get all notifications
      operationId: listNotifications
      responses:
        '200':
          description: List of notifications
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Notification'

components:
  schemas:
    AssignRequest:
      type: object
      required:
        - order_id
        - address
        - recipient_phone
      properties:
        order_id:
          type: string
          description: Unique order identifier
          example: "ORD-001"
        address:
          type: string
          description: Delivery address
          example: "Moscow, Red Square, 1"
        recipient_phone:
          type: string
          description: Recipient phone number
          pattern: '^\+?[0-9]{10,15}$'
          example: "+79001234567"

    AssignResponse:
      type: object
      properties:
        task_id:
          type: string
          description: Unique task identifier
        courier_name:
          type: string
        status:
          type: string
          enum: [assigned, pending]

    Courier:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        available:
          type: boolean
        location:
          type: string

    Delivery:
      type: object
      properties:
        task_id:
          type: string
        order_id:
          type: string
        status:
          type: string
        courier_name:
          type: string

    DeliveryStatus:
      type: object
      properties:
        task_id:
          type: string
        order_id:
          type: string
        status:
          type: string
          enum: [assigned, in_transit, delivered, failed]
        courier_name:
          type: string

    LocationUpdate:
      type: object
      required:
        - task_id
        - lat
        - lng
      properties:
        task_id:
          type: string
        lat:
          type: number
          format: float
          description: Latitude
        lng:
          type: number
          format: float
          description: Longitude

    TrackingInfo:
      type: object
      properties:
        task_id:
          type: string
        status:
          type: string
        last_location:
          type: object
          properties:
            lat:
              type: number
            lng:
              type: number

    CompleteRequest:
      type: object
      required:
        - task_id
        - proof
      properties:
        task_id:
          type: string
        proof:
          type: string
          description: Delivery confirmation code

    NotificationRequest:
      type: object
      required:
        - recipient
        - message
      properties:
        recipient:
          type: string
        type:
          type: string
          enum: [sms, email, push]
          default: sms
        message:
          type: string
        order_id:
          type: string

    Notification:
      type: object
      properties:
        id:
          type: integer
        recipient:
          type: string
        type:
          type: string
        message:
          type: string
        status:
          type: string
