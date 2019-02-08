"""
Incorporate the other data sources.
"""


import os
import pandas as pd
import sys

path = 'C:/Users/djoll/OneDrive/Documents/work/CU_trust/'
sys.path.append(path)
os.chdir(path)

from functions import align, scale_ae

# load lookup
lookup = pd.read_csv('lookups/lookup.csv')

#~ end setup ~#


# =============================================================================
# Number of schools by region
# decided to skip prim/sec distinction for now: check with them

# https://www.gov.uk/government/statistics/schools-pupils-and-their-characteristics-january-2018
# =============================================================================

sch_master = pd.ExcelFile('national_data_source/Schools_Pupils_and_their_Characteristics_2018_LA_Tables.xlsx')

sch = sch_master.parse('Table 7a', skiprows=6)
sch = sch[['LA Code', 'Unnamed: 3', 'All schools']]
sch = sch.dropna(subset=['LA Code'])
sch = sch.drop(columns='LA Code')
sch.columns = ['la', 'total_number_of_schools']

# apply tweaks for merge
sch['la'] = align(sch['la'])

sch.to_csv('national_data_formatted/n_schools.csv', index=None)

# define LA list for later
las = set(sch['la'])

# =============================================================================
# Proportion of children taking free school meals
# it's split by primary/secondary schools
# =============================================================================

free_prim = sch_master.parse('Table 8a', skiprows=6)
free_prim = free_prim[['LA Code', 'Unnamed: 3', 'Unnamed: 7']]
free_prim = free_prim.dropna(subset=['LA Code'])
free_prim = free_prim.drop(columns='LA Code')
free_prim.columns = ['la', 'free_school_meal_%']

free_sec = sch_master.parse('Table 8b', skiprows=6)
free_sec = free_sec[['LA Code', 'Unnamed: 3', 'Unnamed: 7']]
free_sec = free_sec.dropna(subset=['LA Code'])
free_sec = free_sec.drop(columns='LA Code')
free_sec.columns = ['la', 'free_school_meal_%']

# join
free_sch = free_prim.merge(free_sec,
                           on='la',
                           how='outer',
                           suffixes=('_primary', '_secondary'))

# apply tweaks for merge
free_sch['la'] = align(free_sch['la'])

free_sch.to_csv('national_data_formatted/free_school_meals.csv', index=None)


# =============================================================================
# English indices of deprivation
# or more specifically, "income deprivation affecting children index"
# This one is a bit more complex, it's debatable which measure we choose
# we want File 11: upper-tier local authority summaries

# https://www.gov.uk/government/statistics/english-indices-of-deprivation-2015
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/464597/English_Indices_of_Deprivation_2015_-_Research_Report.pdf
# =============================================================================

idaci_master = pd.ExcelFile('national_data_source/File_11_ID_2015_Upper-tier_Local_Authority_Summaries.xlsx')

idaci = idaci_master.parse('IDACI')
# it's debatable which measure we choose here.
# let's start by converting things to deciles.

idaci = idaci.rename(columns={'Upper Tier Local Authority District name (2013)':'la',
                              'Income Deprivation Affecting Children Index (IDACI) - Rank of average rank':'rank'})

idaci = idaci[['la', 'rank']]
idaci = idaci.rename(columns={'rank':'idaci_rank'})
# lower rank = more deprived
idaci['idaci_decile'] = pd.cut(idaci['idaci_rank'], bins=10, labels=range(1,11))
# lower "decile" = more deprived

# apply tweaks for merge
idaci['la'] = align(idaci['la'])

idaci.to_csv('national_data_formatted/idaci.csv', index=None)


# =============================================================================
# "opportunity areas"
# this one is easy, there are just 12
# BUT they don't always match our breakdown...

# https://www.gov.uk/government/publications/social-mobility-and-opportunity-areas
# =============================================================================

#XXX even if the names match, it doesn't necessarily mean they're referring
# to the same area...
matched_areas = ['blackpool',
                 'bradford',
                 'derby',
                 'doncaster',
                 'oldham',
                 'stoke-on-trent']

# this is dodgy, but
# we can make some assumptions about which LA they best fit into.
unmatched_areas = {'fenland and east cambridgeshire':'cambridgeshire',
                   'hastings':'east sussex',
                   'ipswich':'suffolk',
                   'north yorkshire coast':'north yorkshire',
                   'norwich':'norfolk',
                   'west somerset':'somerset'}

combined = matched_areas + list(unmatched_areas.values())

opp_area = pd.DataFrame({'la':list(las)})
opp_area['opportunity_area'] = 0
opp_area.loc[opp_area['la'].isin(combined),
             'opportunity_area'] = 1

# apply tweaks for merge
opp_area['la'] = align(opp_area['la'])
             
opp_area.to_csv('national_data_formatted/opp_area.csv', index=None)


# =============================================================================
# Education gap data
# This is at the correct geography

# https://epi.org.uk/education-gap-data/
# =============================================================================

eg = pd.read_csv('national_data_source/education_gap.csv')

# there are 4 metrics, i'll keep the most pertinent one
# breakdown is by early years / primary / secondary

# gap in months: the gap in academic progress between disadvantaged pupils and non-disadvantaged pupils (nationally)
# disadvantaged definition comes from DfE: those eligible for free school meals

eg = eg[['Local Authority',
         'Gap in months relative to non-disadvantaged pupils nationally Early years',
         'Gap in months relative to non-disadvantaged pupils nationally Primary school',
         'Gap in months relative to non-disadvantaged pupils nationally Secondary school',
         ]]

eg.columns = ['la',
              'education_gap_early_years (months behind)',
              'education_gap_primary (months behind)',
              'education_gap_secondary (months behind)'
              ]

# apply tweaks for merge
eg['la'] = align(eg['la'])

eg.to_csv('national_data_formatted/education_gap.csv', index=None)


# =============================================================================
# great place scheme
# similar to opportunity areas

# https://www.greatplacescheme.org.uk/england
# =============================================================================

# keys are descriptions from site, values are my attempt to match to
# LA. This isn't always possible.

gps_areas = {'barnsley and rotherham':['barnsley', 'rotherham'],
             'great yarmouth and lowestoft':'norfolk',
             'gloucester':'gloucestershire',
             'walthamstow':'waltham forest',
             'coventry city of culture trust':'coventry',
             'craven district council':'north yorkshire',
             'derbyshire county council':['derbyshire', 'derby'],
             'greater manchester combined authority':'manchester',
             'old oak and park royal development corporation':None, # somewhere is west london
             'reading borough council':'reading',
             'rural media charity':'herefordshire',
             'sunderland culture':'sunderland',
             'tees valley combined authority':None, # bigger than UAs
             'the creative foundation':'kent', 
             'torbay economic development company ltd':'torbay'}

# don't want to save this: too many gaps...


# =============================================================================
# Social mobility index
# https://www.gov.uk/government/publications/social-mobility-index-2017-data
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/662744/State_of_the_Nation_2017_-_Social_Mobility_in_Great_Britain.pdf

# this will need some interpretation...
#XXX this is done at LAD level, will need aggregating...
# that could be nasty with "ranks"...
# =============================================================================

# this is a ranking exercise, as with idaci
# but it's complicated to aggregate, since it's already a weighted composite index
# stick with default weights

# i think doing a decile system is best: it's what's published here anyway
# keep it simple. take population weighted average of overall score, then rank

smi_master = pd.ExcelFile('national_data_source/SMI_2017_Final_v1.1.xlsx')

smi = smi_master.parse('Standardised scores', skiprows=2, )
smi = smi[['Local Authority', 'Overall score']]
smi.columns = ['ltla', 'smi']
smi['ltla'] = align(smi['ltla'])

# no data for CoL / IoS
smi = smi.merge(lookup,
                on='ltla',
                how='outer')

# group
smi['pop_sum'] = smi['ltla_population']\
                        .groupby(smi['utla'])\
                        .transform('sum')
                        
smi['ltla_weight'] = smi['ltla_population'] / smi['pop_sum']
                        
smi['smi_weighted_score'] = smi['smi'] * smi['ltla_weight']

utla_smi = smi.groupby('utla')['smi_weighted_score'].sum().reset_index()

utla_smi['smi_decile'] = pd.qcut(utla_smi['smi_weighted_score'], q=10, labels=range(1,11))
# lower decile = lower social mobility

utla_smi = utla_smi.rename(columns={'utla':'la'})
utla_smi.to_csv('national_data_formatted/smi.csv', index=None)


# =============================================================================
# Achieving Excellence areas
# cat 5 and 6 are low scorers
# https://www.gov.uk/government/publications/defining-achieving-excellence-areas-methodology

# It's at the LAD level, but does map to upper tiers...
#XXX there's a gap in their documentation, waiting on an email response...
# =============================================================================
# as with SMI, it's a weighted index (kind of)
# it's not in the table, so i'll recompute the index according to:
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/508392/Methodology_guidance_note_-_defining_achieving_excellence_areas.pdf

ae_master = pd.ExcelFile('national_data_source/Indicator_data_-_defining_Achieving_Excellence_Areas.xlsx')

ae = ae_master.parse('Sheet1', skiprows=3)

# the columns are a mess, just write them out manually
cols = ['ltla_code',
        'ltla',
        'utla',
        'region',
        None,
        ('Standards', 'KS4', 'Attainment Score'),
        ('Standards', 'KS4', 'Progress Score'),
        ('Standards', 'KS2', 'Average Point Score in Reading Writing and Mathematics'),
        ('Standards', 'KS2', 'KS1-2 Value Added by District'),
        ('Standards', 'Accessibility', '% of pupils able to access a good or outstanding secondary within 5km of their home postcode'),
        None,
        ('Capacity', 'System Leaders Coverage', 'Primary pupils per primary phase Teaching School or NLE'),
        ('Capacity', 'System Leaders Coverage', 'Secondary pupils per secondary phase Teaching School or NLE'),
        ('Capacity', 'ITT Provider Coverage', 'Trainees per 10,000 pupils'),
        ('Capacity', 'Quality of Leadership', '% of primary pupils in a school with good or outstanding leadership'),
        ('Capacity', 'Quality of Leadership', '% of secondary pupils in a school with good or outstanding leadership'),
        ('Capacity', 'Sponsor Coverage', 'Pupils per lead or outstanding sponsor academy'),
        None,
        ('Composite Indicator', 'Grouping (of six)')]

ae.columns = cols
ae = ae.drop(columns=[None])
ae = ae.dropna(axis=0, thresh=2)

# there are a few suppressed values.
# i'll just use class median imputation
suppressed_cols = [('Standards', 'KS4', 'Attainment Score'),
                   ('Standards', 'KS4', 'Progress Score')]

medians = {}
for c in suppressed_cols:
    nums = ae[ae[c] != 'SUPP']
    medians[c] = nums[c].astype(float).median()
    
for c in suppressed_cols:
    ae[c] = ae[c].replace('SUPP', medians[c])
    ae[c] = ae[c].astype(float)

# now apply scaling func
relevant_cols = [c for c in ae.columns if c[0] in ('Standards', 'Capacity')]
for c in relevant_cols:
    ae[c] = scale_ae(ae[c])

# we now weight each group equally, and each measure equally
std_cols = [c for c in ae.columns if c[0] == 'Standards']
cap_cols = [c for c in ae.columns if c[0] == 'Capacity']

ae['std_avg'] = ae[std_cols].mean(axis=1)
ae['cap_avg'] = ae[cap_cols].mean(axis=1)

ae['score'] = ae[['std_avg', 'cap_avg']].mean(axis=1)
# low score is bad, high score is good

ae['group'] = pd.qcut(ae['score'], q=6, labels=[6,5,4,3,2,1])


#XXX check we get the sextiles right
# this needs to be correct...

#ae.to_csv('national_data_formatted/achieving_excellence.csv', index=None)


# =============================================================================
# POLAR 4 data
# measures participation in university
# data is at the MSOA level, but has population counts, so should
# be simple to aggregate

# https://www.officeforstudents.org.uk/data-and-analysis/polar-participation-of-local-areas/polar4-data/
# =============================================================================

polar = pd.read_csv('national_data_source/polar4_classification_msoa_sep18.csv',
                    skiprows=26)

str_cols = list(polar.select_dtypes(include=[object]).columns)

for c in str_cols:
    polar[c] = polar[c].str.strip()

polar.columns = [c.strip() for c in polar.columns]

polar = polar[polar['Country'] == 'England']
polar.columns = [c.lower() for c in polar.columns]
polar = polar[['msoa', 'population', 'entrants']]

# some entries are unclassified ('.')
# we'll drop them for now

polar = polar[(polar['population'] != '.') & (polar['entrants'] != '.')]

polar['population'] = polar['population'].astype(int)
polar['entrants'] = polar['entrants'].astype(int)


# now we aggregate to UTLA
msoa_lookup = pd.read_csv('lookups/msoa_lookup.csv')

joined = msoa_lookup[['msoa', 'utla']].merge(polar,
                                             on='msoa',
                                             how='outer')

# aggregate

polar_utla = joined.groupby('utla')[['population', 'entrants']].sum()
polar_utla['YPR'] = polar_utla['entrants'] / polar_utla['population']

# cap at 1
polar_utla.loc[polar_utla['YPR'] > 1,
               'YPR'] = 1
               
# recalculate quintiles
#XXX on hold: their quintiles don't add up...       

# =============================================================================
# NCOP
# it's not obvious how this could be matched up...


# https://www.officeforstudents.org.uk/advice-and-guidance/promoting-equal-opportunities/national-collaborative-outreach-programme-ncop/ncop-in-your-area/
# =============================================================================


# =============================================================================
# LTLA level population data
# =============================================================================
    
pop_master = pd.ExcelFile('national_data_source/ukmidyearestimates2017finalversion.xls')

pop = pop_master.parse('MYE2 - All', skiprows=4)
pop = pop[['Name', 'Geography1', 'All ages']]
pop.columns = ['name', 'geog', 'ltla_population']
pop = pop.dropna(axis=0)

# get rid of unneeded regions
pop = pop.loc[:371]
pop = pop[~pop['name'].str.isupper()]

# good enough...?
assert pop['name'].nunique() == pop.shape[0]

pop['name'] = align(pop['name'])

pop.to_csv('lookups/population.csv', index=None)
