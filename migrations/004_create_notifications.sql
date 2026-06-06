-- Migration 004: Create notifications table
CREATE TABLE notifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    recipient NVARCHAR(50) NOT NULL,
    type NVARCHAR(20) DEFAULT 'sms',
    message NTEXT,
    order_id NVARCHAR(50),
    status NVARCHAR(20) DEFAULT 'queued',
    sent_at DATETIME,
    created_at DATETIME DEFAULT GETUTCDATE()
);
