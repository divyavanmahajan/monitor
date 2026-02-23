# Grafana Setup Guide for Home Automation

This guide explains how to set up Grafana to visualize your home automation data from SQLite.

## 1. Install Grafana and SQLite Plugin

1. Ensure Grafana is running (default `http://localhost:3000`).
2. Login (default: `admin` / `admin`).
3. Go to **Connections** > **Data Sources**.
4. Search for **SQLite** and install/add it.

## 2. Configure Data Sources

Add three separate SQLite data sources (or one per project) pointing to your `.db` files:

- **Path to DB**: `/Users/divya/Documents/projects/homeautomation/monitor/data/temp.db`
- **Path to DB**: `/Users/divya/Documents/projects/homeautomation/monitor/data/energy.db`
- **Path to DB**: `/Users/divya/Documents/projects/homeautomation/monitor/data/weatherdata.db`

## 3. Create Dashboards

### Temperature (Evohome)
Create a **Time series** panel using the `temp.db` source:

```sql
SELECT
  strftime('%Y-%m-%dT%H:%M:%SZ', timestamp) AS time,
  "_5262675_Livingroom" AS Livingroom,
  "_5262676_Hall_upstairs" AS "Hall Upstairs",
  "_5262677_Nana" AS Nana,
  "_5262678_Kitchen" AS Kitchen,
  "_5262680_Dining" AS Dining,
  "_5262681_Alicia" AS Alicia,
  "_5262682_Divya" AS Divya,
  "_5262683_Jessy" AS Jessy,
  "_5262684_Boys" AS Boys,
  "_5262685_Laundry_room" AS "Laundry Room"
FROM readings
WHERE timestamp >= '${__from:date:iso}' 
  AND timestamp <= '${__to:date:iso}'
ORDER BY timestamp ASC
```

### Energy Meter (P1)
Create a **Time series** panel using the `energy.db` source:

```sql
SELECT
  strftime('%Y-%m-%dT%H:%M:%SZ', timestamp) AS time,
  active_power_w AS "Power (W)",
  active_power_l1_w AS "Phase 1 (W)",
  active_power_l2_w AS "Phase 2 (W)",
  active_power_l3_w AS "Phase 3 (W)"
FROM readings
WHERE timestamp >= '${__from:date:iso}' 
  AND timestamp <= '${__to:date:iso}'
ORDER BY timestamp ASC
```

```sql
SELECT
  strftime('%Y-%m-%dT%H:%M:%SZ', timestamp) AS time,
  total_gas_m3 AS "Gas (m3)",
  total_power_import_kwh AS "Power (kWh)"
FROM readings
WHERE timestamp >= '${__from:date:iso}' 
  AND timestamp <= '${__to:date:iso}'
ORDER BY timestamp ASC
```

```sql
SELECT
  strftime('%Y-%m-%dT%H:%M:%SZ', timestamp) AS time,
  total_power_export_kwh AS "Power Export (kwh)"
FROM readings
WHERE timestamp >= '${__from:date:iso}' 
  AND timestamp <= '${__to:date:iso}'
ORDER BY timestamp ASC
```

***
```sql
CREATE TABLE readings ("wifi_ssid" REAL, "wifi_strength" REAL, "smr_version" REAL, "meter_model" REAL, "unique_id" REAL, "active_tariff" REAL, "total_power_import_kwh" REAL, "total_power_import_t1_kwh" REAL, "total_power_import_t2_kwh" REAL, "total_power_export_kwh" REAL, "total_power_export_t1_kwh" REAL, "total_power_export_t2_kwh" REAL, "active_power_w" REAL, "active_power_l1_w" REAL, "active_power_l2_w" REAL, "active_power_l3_w" REAL, "active_voltage_l1_v" REAL, "active_voltage_l2_v" REAL, "active_voltage_l3_v" REAL, "active_current_a" REAL, "active_current_l1_a" REAL, "active_current_l2_a" REAL, "active_current_l3_a" REAL, "voltage_sag_l1_count" REAL, "voltage_sag_l2_count" REAL, "voltage_sag_l3_count" REAL, "voltage_swell_l1_count" REAL, "voltage_swell_l2_count" REAL, "voltage_swell_l3_count" REAL, "any_power_fail_count" REAL, "long_power_fail_count" REAL, "total_gas_m3" REAL, "gas_timestamp" REAL, "gas_unique_id" REAL, "timestamp" TEXT);
```

### Weather (OpenWeatherMap)
Create a **Time series** panel using the `weatherdata.db` source:

```sql
SELECT
  strftime('%Y-%m-%dT%H:%M:%SZ', timestamp) AS time,
  temp_c AS "Temperature (°C)",
  feels_like_c AS "Feels Like (°C)",
  pressure AS "Pressure",
  humidity AS "Humidity (%)"
FROM readings
WHERE timestamp >= '${__from:date:iso}' 
  AND timestamp <= '${__to:date:iso}'
ORDER BY timestamp ASC
```

```sql
CREATE TABLE readings ("lat" REAL, "lon" REAL, "timezone" TEXT, "timezone_offset" TEXT, "dt" REAL, "sunrise" REAL, "sunset" REAL, "temp_k" REAL, "temp_c" REAL, "feels_like_k" REAL, "feels_like_c" REAL, "dew_point_k" REAL, "dew_point_c" REAL, "pressure" REAL, "humidity" REAL, "uvi" REAL, "clouds" REAL, "visibility" REAL, "wind_speed" REAL, "wind_deg" REAL, "weather_id" REAL, "weather_main" TEXT, "weather_description" TEXT, "weather_icon" TEXT, "timestamp" TEXT);
```

## 4. Troubleshooting
If columns are missing or names are incorrect, ensure the polling scripts have been updated and the databases have been cleanly re-imported from their respective CSV files.
