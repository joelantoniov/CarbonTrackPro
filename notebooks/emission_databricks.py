#! /usr/bin/env python
# -*- coding: utf-8 -*-
from src.analytics.databricks_analytics import DatabricksAnalytics
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize analytics engine
analytics = DatabricksAnalytics()

# Load and analyze data
results = analytics.perform_advanced_analytics()

# COMMAND ----------

# Display monthly trends
display(results['monthly_trends'])

# Facility rankings visualization
facility_rankings = results['facility_rankings'].toPandas()

plt.figure(figsize=(12, 6))
sns.barplot(data=facility_rankings.head(10), x='facility_id', y='total_facility_emissions')
plt.title('Top 10 Facilities by Total Emissions')
plt.xticks(rotation=45)
plt.show()

# Anomaly detection results
anomalies = results['anomalies']
print(f"Detected {anomalies.count()} emission anomalies")
display(anomalies.select('facility_id', 'emission_value', 'z_score', 'timestamp').orderBy('z_score', ascending=False))
