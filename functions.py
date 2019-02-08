"""
Re-usable functions.
"""

import matplotlib.pyplot as plt


def check_data_input(df):
    """ Check that the input data meets our expectations:
        - check cols exist
        - check col types are numeric
        - check number of rows is as expected
    """
    cols = list(df.columns)
    
    must_contain = ['la',
                    'region',
                    'Primary Schools',
                    'Secondary Schools',
                    'education_gap_early_years (months behind)',
                    'education_gap_primary (months behind)',
                    'education_gap_secondary (months behind)',
                    'free_school_meal_%_primary',
                    'free_school_meal_%_secondary',
                    'idaci_rank',
                    'idaci_decile',
                    'total_number_of_schools',
                    'opportunity_area',
                    'smi_weighted_score',
                    'smi_decile'
                    ]
    
    for c in must_contain:
        assert c in cols, f"Error, couldn't find '{c}' column in the data, make sure you load the correct file!"
    
    for c in must_contain[2:]:
        try:
            df[c].astype(float)
        except ValueError:
            raise Exception(f"Error, '{c}' column could not be converted to numeric. Check that there is no text in this column.")
        
    nrows = df.shape[0]
    
    if not nrows == 152:
        print(f'Warning, expected 152 records, only found {nrows}')
        
    print('Input data is as expected!')
    

def align(la):
    """ Rename certain discrepancies.
        Expects pandas series input.
    """
    la = la.str.lower()
    
    rename_dict = {'durham':'county durham',
                   'herefordshire':'herefordshire, county of',
                   'shepway':'folkestone and hythe' # ltla only
                   }
    
    la = la.replace(rename_dict)
 
    return la


def scale_ae(s):
    """ Replicate the scaling as outlined in:
        https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/508392/Methodology_guidance_note_-_defining_achieving_excellence_areas.pdf
    """
    low = min(s)
    high = max(s)
    
    scaled = s.apply(lambda x: (x - low) / (high - low))
    
    # these ones need inverting, according to the docs
    inverted = [('Capacity', 'System Leaders Coverage', 'Primary pupils per primary phase Teaching School or NLE'),
                ('Capacity', 'System Leaders Coverage', 'Secondary pupils per secondary phase Teaching School or NLE'),
                ('Capacity', 'Sponsor Coverage', 'Pupils per lead or outstanding sponsor academy')
               ]
    
    if s.name in inverted:
        return scaled.apply(lambda x: 1-x)
    else:
        return scaled

    
def make_bar_chart(df,
                   col,
                   text_loc,
                   title,
                   ylabel,
                   fname,
                   ylim=None):
    """ Params:
        df      - input dataframe, must be sorted correctly
        col     - column to plot
        text_loc- coords for legend
        title   - title
        ylabel  - y axis label
        fname   - full filepath to save to
        ylim    - default None, 2-element list of y-axis min/max
    """
    purples = df[df['utla_%_schools'] > 50].index
    reds = df[(df['utla_%_schools'] <= 50) & (df['utla_%_schools'] > 20)].index
    oranges = df[(df['utla_%_schools'] <= 20) & (df['utla_%_schools'] > 10)].index
    yellows = df[(df['utla_%_schools'] <= 10) & (df['utla_%_schools'] > 0)].index
    
    plt.figure(figsize=(48,8))
    bars = plt.bar(range(df.shape[0]),
                   df[col],
                   color='white',
                   edgecolor='black')
    # colour things in!
    for loc in purples:
        bars[loc].set_color('purple')
    for loc in reds:
        bars[loc].set_color('red')
    for loc in oranges:
        bars[loc].set_color('orange')
    for loc in yellows:
        bars[loc].set_color('yellow')
    plt.xticks(range(df.shape[0]), df['la'].values, rotation=90, fontsize=12)
    text = """Colour indicates % of schools CU Trust operates in.
    Purple: over 50%.
    Red: 20-50%.
    Orange: 10-20%.
    Yellow: 0-10%.
    White: No schools."""
    plt.text(*text_loc, text, bbox={'facecolor':'lightblue'}, fontsize=20)
    plt.title(title, fontsize=15)
    plt.ylabel(ylabel, fontsize=14)
    plt.grid(axis='y')
    if ylim:
        plt.ylim(ylim)

    plt.savefig(fname, dpi=400)
    plt.close()




if __name__ == '__main__':
    print("Import me, don't run me!")