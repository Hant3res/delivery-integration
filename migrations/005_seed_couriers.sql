-- Migration 005: Seed initial couriers
INSERT INTO couriers (courier_id, name, available, location) VALUES
('courier_1', 'Ivan', 1, 'Moscow, Tverskaya'),
('courier_2', 'Petr', 1, 'Moscow, Arbat'),
('courier_3', 'Sidor', 1, 'Moscow, Kutuzovsky');
