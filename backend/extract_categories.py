"""Extract unique airline names and airport codes from training data."""
import pandas as pd
import os

data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# Read just the Airline column from one file
csv_path = os.path.join(data_dir, 'Combined_Flights_2022.csv')
print(f"Reading from: {csv_path}")

df = pd.read_csv(csv_path, usecols=['Airline', 'Origin', 'Dest'], nrows=500000)

airlines = sorted(df['Airline'].unique())
origins = sorted(df['Origin'].unique())
dests = sorted(df['Dest'].unique())
airports = sorted(set(origins) | set(dests))

print(f"\n=== UNIQUE AIRLINES ({len(airlines)}) ===")
for a in airlines:
    print(f"  '{a}'")

print(f"\n=== UNIQUE AIRPORTS ({len(airports)}) ===")
for a in airports:
    print(f"  '{a}'")
