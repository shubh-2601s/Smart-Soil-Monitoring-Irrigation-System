-- Smart Soil Monitoring System Database Setup
-- Run this script to set up the MySQL database

-- Create the database
CREATE DATABASE IF NOT EXISTS soil_db;
USE soil_db;

-- Create the main soil_data table
CREATE TABLE IF NOT EXISTS soil_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nitrogen INT NOT NULL,
    phosphorus INT NOT NULL,
    potassium INT NOT NULL,
    ph FLOAT NOT NULL,
    ec INT NOT NULL,
    humidity FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    relay VARCHAR(10) DEFAULT 'OFF',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_relay (relay)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create a user for the application (optional)
-- Replace 'your_password' with a secure password
-- CREATE USER 'soil_user'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON soil_db.* TO 'soil_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Insert sample data for testing (optional)
INSERT INTO soil_data (nitrogen, phosphorus, potassium, ph, ec, humidity, temperature, relay) VALUES
(25, 30, 150, 6.8, 800, 45.5, 24.2, 'OFF'),
(22, 28, 145, 6.9, 820, 42.3, 23.8, 'OFF'),
(28, 32, 155, 7.1, 780, 48.7, 25.1, 'ON');

-- Show table structure
DESCRIBE soil_data;

-- Show sample data
SELECT * FROM soil_data ORDER BY timestamp DESC LIMIT 5;