-- Migration 002: Create deliveries table
CREATE TABLE deliveries (
    id INT IDENTITY(1,1) PRIMARY KEY,
    task_id NVARCHAR(50) NOT NULL UNIQUE,
    order_id NVARCHAR(50) NOT NULL,
    address NVARCHAR(500) NOT NULL,
    recipient_phone NVARCHAR(20) NOT NULL,
    courier_id INT FOREIGN KEY REFERENCES couriers(id),
    status NVARCHAR(50) DEFAULT 'assigned',
    proof NTEXT,
    created_at DATETIME DEFAULT GETUTCDATE(),
    completed_at DATETIME
);
