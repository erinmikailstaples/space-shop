import pandas as pd

# Load the data
file_path = 'data/jupiter_moons.tsv'
moons_data = pd.read_csv(file_path, sep='\t')

# Display the first few rows
print(moons_data.head())
