import pandas as pd

filepath = 'open-meteo-9.60N76.52E26m.csv'

# Read the file to find where the daily summary starts
with open(filepath, 'r') as file:
    lines = file.readlines()

daily_start_line = 0
for i, line in enumerate(lines):
    if "time,precipitation_sum" in line:
        daily_start_line = i
        break

# Extract the daily rows and save them to a clean file
daily_data = lines[daily_start_line:]
with open('clean_daily_weather.csv', 'w') as clean_file:
    clean_file.writelines(daily_data)

# Load the clean data into pandas to verify the columns
df = pd.read_csv('clean_daily_weather.csv')

print("--- Cleaned Dataset Columns ---")
print(df.columns.tolist())
print("\n--- First 3 Rows of Data ---")
print(df.head(3))