"""
Important: the CU data is at the 
"counties and unitary authority" level, not the LA level.
"""

import os
import pandas as pd
import sys

path = 'C:/Users/djoll/OneDrive/Documents/work/CU_trust/'
sys.path.append(path)
os.chdir(path)

from functions import align

#~ end setup ~#

# =============================================================================
# First get the CU data in a good shape
# =============================================================================

master = pd.ExcelFile(path + 'CU reasearch and Data Jan 2019.xlsx')

df = master.parse(sheet_name="CU_LA_N_o's")

# rename cols
df = df.rename(columns={'Local Authority':'la'})

df['region'] = None
# just do it manually...
df.loc[:13, 'region'] = 'North East'
df.loc[14:37, 'region'] = 'North West'
df.loc[39:54, 'region'] = 'Yorkshire and the Humber'
df.loc[56:65, 'region'] = 'East Midlands'
df.loc[67:81, 'region'] = 'West Midlands'
df.loc[83:94, 'region'] = 'East of England'
df.loc[97:111, 'region'] = 'Inner London' # might need special handling
df.loc[113:132, 'region'] = 'Outer London'
df.loc[134:153, 'region'] = 'South East'
df.loc[155:, 'region'] = 'South West'

df = df.dropna(subset=['la'])
df = df[['la', 'region', 'Primary Schools', 'Secondary Schools', "Children's University Name"]]

# ignore region rows
df = df[~df['la'].str.isupper()]

df['la'] = align(df['la'])

# save
df.to_csv('CU_data.csv', index=None)




