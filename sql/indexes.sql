-- Performance indexes for CarbonTrack Pro

-- Indexes for performance
CREATE INDEX IX_emissions_raw_facility_timestamp ON emissions_raw(facility_id, processed_timestamp);
CREATE INDEX IX_emissions_raw_severity ON emissions_raw(emission_severity);
CREATE INDEX IX_emissions_raw_emission_value ON emissions_raw(emission_value);
CREATE INDEX IX_emissions_raw_timestamp ON emissions_raw(processed_timestamp);

CREATE INDEX IX_emissions_aggregated_window ON emissions_aggregated(window_start, facility_id);
CREATE INDEX IX_emissions_aggregated_facility ON emissions_aggregated(facility_id, emission_type);

CREATE INDEX IX_compliance_reports_date ON compliance_reports(report_date, facility_id);
CREATE INDEX IX_compliance_reports_status ON compliance_reports(compliance_status);

CREATE INDEX IX_alerts_timestamp ON alerts(alert_timestamp, acknowledged);
CREATE INDEX IX_alerts_facility ON alerts(facility_id, alert_type);
CREATE INDEX IX_alerts_severity ON alerts(severity, acknowledged);
