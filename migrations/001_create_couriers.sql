-- Migration 001: Create couriers table
CREATE TABLE couriers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    courier_id NVARCHAR(50) NOT NULL UNIQUE,
    name NVARCHAR(100) NOT NULL,
    available BIT DEFAULT 1,
    location NVARCHAR(200),
    created_at DATETIME DEFAULT GETUTCDATE()
);
