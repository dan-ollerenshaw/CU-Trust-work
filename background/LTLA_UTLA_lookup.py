"""
updated with official lookup

n.b Shepway named changed to Folkestone and Hythe
"""


import os
import pandas as pd
import sys

path = 'C:/Users/djoll/OneDrive/Documents/work/CU_trust/'
sys.path.append(path)
os.chdir(path)

from functions import align

#~ end setup ~#

master = pd.ExcelFile('lookups/LTLA18_UTLA18_EW_LUv2.xlsx')

df = master.parse('LTLA18_UTLA18_EW_LUv2')

df = df[df['LTLA18CD'].str.startswith('E')]
df = df[['LTLA18NM', 'UTLA18NM']]
df.columns = ['ltla', 'utla']

df['ltla'] = align(df['ltla'])
df['utla'] = align(df['utla'])


# we want to add population counts for LADs, and lookups for MSOA's if possible
pop = pd.read_csv('lookups/population.csv')
pop = pop.rename(columns={'name':'ltla'})

lookup = df.merge(pop,
                  on='ltla',
                  how='left')

lookup = lookup.drop(columns='geog')

lookup.to_csv('lookups/lookup.csv', index=None)

# sums match with MYE populations!

msoa = pd.read_csv('lookups/Output_Area_to_Lower_Layer_Super_Output_Area_to_Middle_Layer_Super_Output_Area_to_Local_Authority_District_December_2017_Lookup_in_Great_Britain__Classification_Version_2.csv')
msoa = msoa[['MSOA11CD', 'LAD17NM']]
msoa.columns = ['msoa', 'ltla']

# drop the lower levels
msoa = msoa.drop_duplicates()

msoa['ltla'] = align(msoa['ltla'])

# ignore other regions
msoa = msoa[msoa['msoa'].str.startswith('E')]

# add to lookup
# we don't need population, that's already provided in polar4
msoa_lookup = msoa.merge(lookup[['ltla', 'utla']],
                         how='left',
                         on='ltla')

msoa_lookup.to_csv('lookups/msoa_lookup.csv', index=None)
