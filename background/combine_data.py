"""
Combine our national metrics and the CU data into a single table.
"""

# needs updating...

import os
import pandas as pd

path = 'C:/Users/djoll/OneDrive/Documents/work/CU_trust/'
national_path = path + 'national_data_formatted/'
os.chdir(path)

cu = pd.read_csv('CU_data.csv')

combined = cu.copy()

national_files = [os.path.join(national_path, f) for f in os.listdir(national_path)]
# we've now added population...

for f in national_files:
    print(f'doing {f}')
    metric = pd.read_csv(f)
    combined = combined.merge(metric,
                              on='la',
                              how='outer')


combined.sort_values(by=['region', 'la'])\
        .to_csv('combined_data.csv', index=None)


