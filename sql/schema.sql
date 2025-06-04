-- CarbonTrack Pro Database Schema

-- Raw emissions data table
CREATE TABLE emissions_raw (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    timestamp DATETIME2,
    facility_id NVARCHAR(50),
    sensor_id NVARCHAR(50),
    emission_type NVARCHAR(20),
    emission_value FLOAT,
    unit NVARCHAR(20),
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    processed_timestamp DATETIME2,
    emission_severity NVARCHAR(10),
    year INT,
    month INT,
    day INT,
    hour INT
);

-- Aggregated emissions data
CREATE TABLE emissions_aggregated (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    window_start DATETIME2,
    window_end DATETIME2,
    facility_id NVARCHAR(50),
    emission_type NVARCHAR(20),
    avg_emission FLOAT,
    max_emission FLOAT,
    min_emission FLOAT,
    reading_count INT,
    avg_temperature FLOAT,
    avg_humidity FLOAT
);

-- Compliance reports
CREATE TABLE compliance_reports (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    report_date DATE,
    facility_id NVARCHAR(50),
    total_emissions FLOAT,
    compliance_status NVARCHAR(20),
    threshold_exceeded_count INT,
    created_timestamp DATETIME2 DEFAULT GETDATE()
);

-- Alerts table
CREATE TABLE alerts (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    alert_timestamp DATETIME2,
    facility_id NVARCHAR(50),
    alert_type NVARCHAR(30),
    message NVARCHAR(500),
    severity NVARCHAR(20),
    acknowledged BIT DEFAULT 0,
    acknowledged_by NVARCHAR(100),
    acknowledged_timestamp DATETIME2
);
