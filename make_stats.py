"""
Make some numbers / graphs from the completed tables.

We want this script to be re-runnable by CU.

Note to self: getting this to work with pyinstaller / cx_Freeze was
a MASSIVE PAIN IN THE ARSE. See setup.py
"""

import geopandas
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

path = 'C:/Users/djoll/work/CU_trust/program/'
sys.path.append(path)
from functions import align, make_bar_chart


def main(df, folder):
    """ params should be provided by GUI user
    """   
    # keep track of all the simple statistics in a table
    # generate charts and maps one at a time
    
    stat_types = ['Percentage of total schools where CU Trust operate',
                  'Percentage of total schools where CU Trust operate',
                  'Local authorities with a high proportion of pupils taking free school meals',
                  'Local authorities with a high proportion of pupils taking free school meals',
                  'Local authorities with a high proportion of pupils taking free school meals',
                  'Local authorities with a high proportion of pupils taking free school meals',
                  'Local authorities scoring poorly on the Income Deprivation Affecting Children Index',
                  'Local authorities scoring poorly on the Income Deprivation Affecting Children Index',
                  'Opportunity areas'
                  ]
    
    stat_descriptions = ['All of England',
                         'By region',
                         'Top 20% of LAs: percentage of LAs where CU Trust operate (primary schools)',
                         'Top 20% of LAs: percentage of LAs where CU Trust operate (secondary schools)',
                         'Top 10% of LAs: percentage of LAs where CU Trust operate (primary schools)',
                         'Top 10% of LAs: percentage of LAs where CU Trust operate (secondary schools)',
                         'Lowest scoring 20% of LAs: percentage of LAs where CU Trust operate',
                         'Lowest scoring 10% of LAs: percentage of LAs where CU Trust operate',
                         'Number of opportunity areas CU Trust operates (out of 12)']
    
    stats = pd.DataFrame(index=[stat_types, stat_descriptions],
                         columns=['stat'])
    
    df['Primary Schools'] = df['Primary Schools'].fillna(0)
    df['Secondary Schools'] = df['Secondary Schools'].fillna(0)
    df['CU_tot_schools'] = df['Primary Schools'] + df['Secondary Schools']
    
    df['utla_%_schools'] = df['CU_tot_schools'] / df['total_number_of_schools'] * 100
    df['utla_%_schools'] = df['utla_%_schools'].fillna(0)
    
    print('Completed data prep.')
    
    #%%
    # =============================================================================
    # % of schools CU operates in:
    # can make choropleths by region and by UTLA
    # consider P/S split
    # =============================================================================
    
    schools_total_percent = round(df['CU_tot_schools'].sum() / df['total_number_of_schools'].sum() * 100, 1)
    stats.loc[('Percentage of total schools where CU Trust operate',
               'All of England')] = f'{schools_total_percent}%'
    
    # we need to combine inner and outer london for a regional plot
    df.loc[df['region'].isin(['Inner London', 'Outer London']),
           'region'] = 'London'
    
    regions = df.groupby('region')[['CU_tot_schools', 'total_number_of_schools']].sum().reset_index()
    regions['reg_%_schools'] = (regions['CU_tot_schools'] / regions['total_number_of_schools'] * 100).round(1)
    # convert to string format
    reg_str = ''
    for idx, row in regions.iterrows():
        region = row['region']
        share = f"{row['reg_%_schools']}%"
        reg_str += f'{region}: {share}\n'
        
    stats.loc[('Percentage of total schools where CU Trust operate',
               'By region')] = f'{reg_str}%'
           
    #%%
    # choropleths
    reg_geo = geopandas.read_file('regions.shp') # these need to be packaged for cx_freeze
    
    to_merge = regions[['region', 'reg_%_schools']].copy()
    to_merge = to_merge.rename(columns={'region':'rgn15nm'})
    to_merge['rgn15nm'] = to_merge['rgn15nm'].replace({'Yorkshire and the Humber':'Yorkshire and The Humber'})
    reg_geo = reg_geo.merge(to_merge,
                            on='rgn15nm')
    
    # add region labels
    reg_geo['coords'] = reg_geo['geometry'].apply(lambda x: x.representative_point().coords[:])
    reg_geo['coords'] = [coords[0] for coords in reg_geo['coords']]
    
    reg_geo.plot(figsize=(12,16),
                 column='reg_%_schools',
                 cmap='OrRd',
                 scheme='quantiles',
                 legend=True,
                 legend_kwds={'loc':'upper left'},
                 edgecolor='black')
    plt.title("Percentage of schools Children's University Trust operates in by region", fontsize=15)
    plt.xticks([])
    plt.yticks([])
    # add labels
    for idx, row in reg_geo.iterrows():
        plt.annotate(s=row['rgn15nm'], xy=row['coords'],
                     horizontalalignment='center')
    plt.savefig(os.path.join(folder, 'schools_by_region.png'), dpi=600)
    plt.close()
    
    print('Completed regional choropleth.')
    
    # LA level choropleth
    utla_geo = geopandas.read_file(f'utla.shp') # these need to be packaged for cx_freeze
    
    # merge sch data
    # could abstract this part
    utla_geo['ctyua15nm'] = align(utla_geo['ctyua15nm'])
    utla_geo = utla_geo[utla_geo['ctyua15cd'].str.startswith('E')]
    
    to_merge = df[['la', 'utla_%_schools']].copy()
    to_merge = to_merge.rename(columns={'la':'ctyua15nm'})
    utla_geo = utla_geo.merge(to_merge,
                              on='ctyua15nm')
    
    # define categories
    bins = [-1, 0, 10, 20, 50, 100]
    labels = ['0%', '0-10%', '10-20%', '20-50%', '>50%']
    
    utla_geo['category'] = pd.cut(utla_geo['utla_%_schools'],
                                  bins=bins,
                                  labels=labels)
    
    utla_geo.plot(figsize=(12,16),
                  column='category',
                  k=len(bins)-1,
                  cmap='OrRd',
                  categorical=True,
                  legend=True,
                  legend_kwds={'loc':'upper left'},
                  edgecolor='black')
    plt.title("Percentage of schools Children's University Trust operates in by local authority", fontsize=15)
    plt.xticks([])
    plt.yticks([])
    plt.savefig(os.path.join(folder, 'schools_by_la.png'), dpi=600)
    plt.close()
    
    print('Completed LA level choropleth.')
    
    #%%
    # =============================================================================
    # Free school meals
    # keep it simple for now: look at quantiles
    # =============================================================================
    def calc_fsm(df,
                 quants='quintiles'):
        """ Params:
            df:         input data
            n_quants:   str, choose deciles or quintiles
        """
        assert quants in ('deciles', 'quintiles')
        
        df['prim_fsm_quant'] = pd.qcut(df['free_school_meal_%_primary'],
                                       10,
                                       labels=list(range(1, 11))[::-1])
        df['sec_fsm_quant'] = pd.qcut(df['free_school_meal_%_secondary'],
                                      10,
                                      labels=list(range(1, 11))[::-1])
    
        lowest = [1] if quants == 'deciles' else [1, 2]
    
        bottom_prim = df[df['prim_fsm_quant'].isin(lowest)]
        bottom_sec = df[df['sec_fsm_quant'].isin(lowest)]
    
        prim_stat = round(bottom_prim[bottom_prim['Primary Schools'] != 0].shape[0]\
                          / bottom_prim.shape[0] * 100)
        prim_stat = f'{prim_stat}%\nMissing LAs:\n'
        missing_prim = set(bottom_prim[bottom_prim['Primary Schools'] == 0]['la'])
        for m in missing_prim:
            prim_stat += f'{m}, '
        
        sec_stat = round(bottom_sec[bottom_sec['Secondary Schools'] != 0].shape[0]\
                         / bottom_sec.shape[0] * 100)
        sec_stat = f'{sec_stat}%\n'
        missing_sec = set(bottom_sec[bottom_sec['Primary Schools'] == 0]['la'])
        for m in missing_sec:
            sec_stat += f'{m}, '
        
        return {'primary': prim_stat,
                'secondary': sec_stat}
        
    
    fsm_dec = calc_fsm(df, quants='deciles')
    fsm_qui = calc_fsm(df, quants='quintiles')
    
    stats.loc[('Local authorities with a high proportion of pupils taking free school meals',
               'Top 20% of LAs: percentage of LAs where CU Trust operate (primary schools)')]\
              = fsm_qui['primary']
    
    stats.loc[('Local authorities with a high proportion of pupils taking free school meals',
               'Top 20% of LAs: percentage of LAs where CU Trust operate (secondary schools)')]\
              = fsm_qui['secondary']
    
    stats.loc[('Local authorities with a high proportion of pupils taking free school meals',
               'Top 10% of LAs: percentage of LAs where CU Trust operate (primary schools)')]\
              = fsm_dec['primary']
    
    stats.loc[('Local authorities with a high proportion of pupils taking free school meals',
               'Top 10% of LAs: percentage of LAs where CU Trust operate (secondary schools)')]\
              = fsm_dec['secondary']
    
    # make a bar chart for primary schools
    df = df.sort_values(by='free_school_meal_%_primary',
                        ascending=False).reset_index(drop=True)
    
    make_bar_chart(df,
                   col='free_school_meal_%_primary',
                   text_loc=(100, 25),
                   title='Local authorities ranked by percentage of pupils taking free school meals (primary school)',
                   ylabel='Percentage of pupils taking free school meals',
                   fname=os.path.join(folder, 'free_school_meals_primary.png'),
                   ylim=[0, 40])
    
    print('Completed free school meal bar chart.')
    
    #%%
    # =============================================================================
    # Next up: IDACI
    # This already comes with deciles, we can repeat what we did for FSM...?
    # in this case i'll combine secondary and primary (could also do this above)
    # =============================================================================
    
    bottom_qui = df[df['idaci_decile'].isin([1, 2])]
    bottom_dec = df[df['idaci_decile'] == 1]
    
    idaci_qui = round(bottom_qui[bottom_qui['CU_tot_schools'] != 0].shape[0]\
                        / bottom_qui.shape[0] * 100)
    idaci_qui = f'{idaci_qui}%\nMissing LAs:\n'
    missing = set(bottom_qui[bottom_qui['CU_tot_schools'] == 0]['la'])
    for m in missing:
        idaci_qui += f'{m}, '
        
    idaci_dec = round(bottom_dec[bottom_dec['CU_tot_schools'] != 0].shape[0]\
                        / bottom_dec.shape[0] * 100)
    idaci_dec = f'{idaci_dec}%\nMissing LAs:\n'
    missing = set(bottom_dec[bottom_dec['CU_tot_schools'] == 0]['la'])
    for m in missing:
        idaci_dec += f'{m}, '
    
    stats.loc[('Local authorities scoring poorly on the Income Deprivation Affecting Children Index',
               'Lowest scoring 20% of LAs: percentage of LAs where CU Trust operate')]\
             = idaci_qui
             
    stats.loc[('Local authorities scoring poorly on the Income Deprivation Affecting Children Index',
               'Lowest scoring 10% of LAs: percentage of LAs where CU Trust operate')]\
             = idaci_dec
    
    # do a bar chart boi
    df = df.sort_values(by='idaci_rank',
                        ascending=True).reset_index(drop=True)
    
    df['idaci_rank_plot'] = 152 - df['idaci_rank']
    
    make_bar_chart(df,
                   col='idaci_rank_plot',
                   text_loc=(100, 100),
                   title='Local authorities ranked by income deprivation affecting children index',
                   ylabel='Rank\n(higher rank equals lower score)',
                   fname=os.path.join(folder, 'idaci.png'),
                   ylim=None)
    
    print('Completed IDACI bar chart.')    
    
    #%%
    # =============================================================================
    # Opportunity areas
    # really straightforward
    # =============================================================================
    opp = df[df['opportunity_area'] == 1]
    
    n = opp[opp['CU_tot_schools'] != 0].shape[0]
    
    stats.loc[('Opportunity areas', 'Number of opportunity areas CU Trust operates (out of 12)')]\
              = n
    
    print('Completed opportunity areas stats.')
    
    #%%
    # =============================================================================
    # Education gap data
    # =============================================================================
    # bar chart
    # could do the deciles thing here too..
    df = df.sort_values(by='education_gap_primary (months behind)',
                        ascending=False).reset_index(drop=True)
    
    make_bar_chart(df,
                   col='education_gap_primary (months behind)',
                   text_loc=(100, 12.5),
                   title='Local authorities ranked by education gap for disadvantaged pupils (primary school)',
                   ylabel='Number of months a disadvantaged student is behind\ncompared to national, non-disadvantaged average.',
                   fname=os.path.join(folder, 'education_gap_primary.png'),
                   ylim=[0, 20])
    
    print('Completed education data bar chart.')
    
    #%%
    # =============================================================================
    # social mobility index
    # same as most of the others
    # =============================================================================
    # just go for rank rather than score, since the score is synthetic
    
    df = df.sort_values(by='smi_weighted_score',
                        ascending=True).reset_index(drop=True)
    
    df['smi_rank'] = df['smi_weighted_score'].rank(ascending=False)
    
    make_bar_chart(df,
                   col='smi_rank',
                   text_loc=(100, 100),
                   title='Local authorities ranked by social mobility index',
                   ylabel='Rank\n(higher rank equals lower score)',
                   fname=os.path.join(folder, 'social_mobility.png'),
                   ylim=None)
    
    print('Completed social mobility bar chart.')

    #%%
    # also save the stats data
    stats.to_csv(os.path.join(folder, 'stats.csv'))
    
    print('Saved stats.')
    
    print('Script complete! You can now quit the program.')

#%%
#TODO:
# (if we get responses) AE and POLAR

#%%
# just stick everything in one big-ol' function
# all we need to pass in is df and folder

if __name__ == '__main__':
    print("Import me, don't run me")
