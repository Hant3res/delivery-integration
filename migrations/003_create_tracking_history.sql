-- Migration 003: Create tracking_history table
CREATE TABLE tracking_history (
    id INT IDENTITY(1,1) PRIMARY KEY,
    task_id NVARCHAR(50) NOT NULL,
    lat FLOAT,
    lng FLOAT,
    status NVARCHAR(50),
    updated_at DATETIME DEFAULT GETUTCDATE()
);
