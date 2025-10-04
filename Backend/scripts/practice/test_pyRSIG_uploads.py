import pyrsig
import pandas as pd
import os

# Settings
tempokey = "tempo.l2.no2.vertical_column_troposphere"
locname = "nyc"
bbox = (-74.8, 40.32, -71.43, 41.4)
bdate = "2024-12-18"

#output_dir = "test_plots"
#os.makedirs(output_dir, exist_ok=True)

# Initialize API
api = pyrsig.RsigApi(bdate=bdate, bbox=bbox, workdir=locname, gridfit=True)
api_key = "anonymous"  # public access
api.tempo_kw["api_key"] = api_key

# ---- TEMPO NO2 Data ----
# Get descriptions
descdf = api.descriptions()
print("TEMPO descriptions:\n", descdf.head(10))

# Extract data as a DataFrame
tempo_df = api.to_dataframe(tempokey, unit_keys=False, parse_dates=True, backend="xdr")
print("TEMPO NO2 DataFrame:\n", tempo_df.head(10))

# Make hourly averages
tempo_hourly = tempo_df.groupby(pd.Grouper(key="time", freq="1h")).mean(numeric_only=True)
print("TEMPO hourly average:\n", tempo_hourly.head(10))

# ---- AirNow NO2 Data ----
airnowkey = "airnow.no2"
airnow_df = api.to_dataframe(airnowkey, unit_keys=False, parse_dates=True)
print("AirNow NO2 DataFrame:\n", airnow_df.head(10))

# Aggregate AirNow NO2 by hour (numeric column only)
airnowno2_hourly = airnow_df.groupby(pd.Grouper(key="time", freq="1h"))["no2"].median()
print(airnowno2_hourly.head(10))
#repeat for tempo 
tempo_no2_hourly = tempo_df.groupby(pd.Grouper(key="time", freq="1h"))["no2_vertical_column_troposphere"].mean()
print(tempo_no2_hourly.head(10))





# Save to CSV (optional)
#tempo_hourly.to_csv(os.path.join(output_dir, "tempo_no2_hourly.csv"))
#airnow_hourly.to_csv(os.path.join(output_dir, "airnow_no2_hourly.csv"))
 