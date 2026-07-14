import pandas as pd


filepath = 'open-meteo-9.60N76.52E26m.csv'


with open(filepath, 'r') as file:
    lines = file.readlines()

daily_start = 0
for i, line in enumerate(lines):
    if "time,precipitation_sum" in line:
        daily_start = i
        break


daily_lines = lines[daily_start:]
with open('temp_daily.csv', 'w') as file:
    file.writelines(daily_lines)


df = pd.read_csv('temp_daily.csv')


def assign_outfit(row):
    rain = row['precipitation_sum (mm)']
    temp_max = row['apparent_temperature_max (°C)']
    
    
    if rain > 10.0:
        return 'Rain Gear (Umbrella, Waterproofs)'
    
    
    elif temp_max > 33.0:
        return 'Hot & Humid (Light cotton, Shorts)'
    
    
    else:
        return 'Mild & Breezy (Jeans, T-shirt)'


df['Outfit_Category'] = df.apply(assign_outfit, axis=1)


df.to_csv('model_training_data.csv', index=False)

print("Dataset successfully created! Here is the count of each outfit category:")
print(df['Outfit_Category'].value_counts())