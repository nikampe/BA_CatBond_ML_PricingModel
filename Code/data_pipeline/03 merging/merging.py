#############################################################################################
# Author: Niklas Leander Kampe - Bachelor Thesis
# Supervisor: Prof. Dr. Alexander Braun - Institute for Insurance Economics
# Step 3: Merging the data sets
#############################################################################################

import pandas as pd
import numpy as np
from datetime import datetime

# Functions

def read_file(inputPath, fileName, name):
    df = pd.read_csv(inputPath + fileName, index_col = 0)
    print(name, 'data set successfully imported.')
    return df

def write_file(df, outputPath, fileName, name):
    df.to_csv(outputPath + fileName)
    print(name, 'data set successfully cleaned and saved.')

def sorting(df):
    df.sort_values(by = ['ISIN', 'Ref_Date'], inplace = True)
    return df

def index_setting(df):
    index = range(0, len(df))
    df['Index'] = index
    df.set_index('Index', inplace = True)
    return df

def na_dropping_subset(df, necessaryColumns):
    n_before = len(df)
    df.dropna(subset = necessaryColumns, how = 'any', axis = 0, inplace = True)
    n_after = len(df)
    print('Rows dropped due to missing values: ', n_before - n_after)
    return df

# -----------------------------------------------------------------------------------

# Process Start
print('------------------')
print('DATA MERGING SUCCESSFULLY INITIATED.')
print('------------------')
 
# AON
name_AON = 'AON'
inputPath_AON= r'Working Data/AON_cleaned/'
## Importing
df_AON = read_file(inputPath_AON, 'df_AON_cleaned.csv', name_AON)

# Swiss Re
name_SwissRe = 'Swiss Re'
inputPath_SwissRe = r'Working Data/SwissRe_cleaned/'
## Importing
df_SwissRe = read_file(inputPath_SwissRe, 'df_SwissRe_cleaned.csv', name_SwissRe)

# S&P 500
name_SP500 = 'S&P 500'
inputPath_SP500 = r'Working Data/S&P500_cleaned/'
## Importing
df_SP500 = read_file(inputPath_SP500, 'df_S&P500_cleaned.csv', name_SP500)
for i in range(0, len(df_SP500)):
    df_SP500.loc[i, 'Date'] = (pd.to_datetime(df_SP500.loc[i, 'Date'])).strftime('%Y-%m-%d')
df_SP500.set_index('Date', inplace = True)

# Rate-on-Line Index
name_RoL = 'Rate-on-Line Index'
inputPath_RoL = r'Working Data/RoL_cleaned/'
## Importing
df_RoL = read_file(inputPath_RoL, 'df_RoL_cleaned.csv', name_RoL)
for i in range(0, len(df_RoL)):
    df_RoL.loc[i, 'Year'] = (pd.to_datetime(df_RoL.loc[i, 'Year'])).strftime('%Y')
df_RoL.set_index('Year', inplace = True)

# Credit Spreads
name_CreditSpreads = 'US Corporate Credit Spreads'
inputPath_CreditSpreads = r'Working Data/CreditSpreads_cleaned/'
## Importing
df_CreditSpreads = read_file(inputPath_CreditSpreads, 'df_CreditSpreads_cleaned.csv', name_CreditSpreads)
for i in range(0, len(df_CreditSpreads)):
    df_CreditSpreads.loc[i, 'Date'] = (pd.to_datetime(df_CreditSpreads.loc[i, 'Date'])).strftime('%Y-%m-%d')
df_CreditSpreads.set_index('Date', inplace = True)

# Seasonalities
name_Seasonalities = 'Peril Seasonalities'
inputPath_Seasonalities = r'Working Data/Seasonalities_cleaned/'
## Importing
df_Seasonalities = read_file(inputPath_Seasonalities, 'df_Seasonalities_cleaned.csv', name_Seasonalities)
df_Seasonalities.set_index('Date', inplace = True)

# Cat Bond Losses & Defaults
name_CatBondLosses = 'Cat Bond Losses & Defaults'
inputPath_CatBondLosses = r'Working Data/CatBondLosses_cleaned/'
## Importing
df_CatBondLosses = read_file(inputPath_CatBondLosses, 'df_CatBondLosses_cleaned.csv', name_CatBondLosses)

# -----------------------------------------------------------------------------------

# Merged Dataset
name_Merged = 'Merged Dataset'
outputPath_Merged = r'Final Data/'
## Merging
datasets = [df_AON, df_SwissRe]
df_Merged = pd.concat(datasets).drop_duplicates(subset = ['ISIN', 'Ref_Date'], keep = 'first')
sorting(df_Merged)
index_setting(df_Merged)
perils = ['NA_EQ', 'NA_Hurricane', 'NA_Winterstorm', 'NA_Windstorm', 'JP_EQ', 'JP_Hurricane', 'JP_Winterstorm', 'JP_Windstorm', 'EU_EQ', 'EU_Winterstorm', 'EU_Windstorm', 'AUS_EQ', 'AUS_Hurricane', 'LA_EQ', 'LA_Hurricane']
for i in range(0, len(df_Merged)):
    if pd.to_datetime(df_Merged.loc[i, 'Ref_Date']).is_quarter_end == True:
        ref_date = (pd.to_datetime(pd.to_datetime(df_Merged.loc[i, 'Ref_Date']))).strftime('%Y-%m-%d')
        df_Merged.loc[i, 'SP500_Quarterly_Return'] = df_SP500.loc[ref_date, 'SP500_Quarterly_Return']
        df_Merged.loc[i, 'Corp_Credit_Spread'] = df_CreditSpreads.loc[ref_date, df_Merged.loc[i, 'Rating']]
        for peril in perils:
            if df_Merged.loc[i, peril] == 1 and df_Seasonalities.loc[ref_date, peril] == 'High season':
                df_Merged.loc[i, 'Seasonality_Dummy'] = 1
            else:
                None
    elif (pd.to_datetime(df_Merged.loc[i, 'Ref_Date']) + pd.to_timedelta(1, unit = 'd')).is_quarter_end == True:
        ref_date = (pd.to_datetime(pd.to_datetime(df_Merged.loc[i, 'Ref_Date']) + pd.to_timedelta(1, unit = 'd'))).strftime('%Y-%m-%d')
        df_Merged.loc[i, 'SP500_Quarterly_Return'] = df_SP500.loc[ref_date, 'SP500_Quarterly_Return']
        df_Merged.loc[i, 'Corp_Credit_Spread'] = df_CreditSpreads.loc[ref_date, df_Merged.loc[i, 'Rating']]
        for peril in perils:
            if df_Merged.loc[i, peril] == 1 and df_Seasonalities.loc[ref_date, peril] == 'High season':
                df_Merged.loc[i, 'Seasonality_Dummy'] = 1
            else:
                None
    elif (pd.to_datetime(df_Merged.loc[i, 'Ref_Date']) + pd.to_timedelta(2, unit = 'd')).is_quarter_end == True:
        ref_date = (pd.to_datetime(pd.to_datetime(df_Merged.loc[i, 'Ref_Date']) + pd.to_timedelta(2, unit = 'd'))).strftime('%Y-%m-%d')
        df_Merged.loc[i, 'SP500_Quarterly_Return'] = df_SP500.loc[ref_date, 'SP500_Quarterly_Return']
        df_Merged.loc[i, 'Corp_Credit_Spread'] = df_CreditSpreads.loc[ref_date, df_Merged.loc[i, 'Rating']]
        for peril in perils:
            if df_Merged.loc[i, peril] == 1 and df_Seasonalities.loc[ref_date, peril] == 'High season':
                df_Merged.loc[i, 'Seasonality_Dummy'] = 1
            else:
                None
    ref_year = (pd.to_datetime(df_Merged.loc[i, 'Ref_Date'])).strftime('%Y')
    df_Merged.loc[i, 'Rate_on_Line_Index'] = df_RoL.loc[ref_year, 'Rate_on_Line_Index_Change']

dropped_nonsense = 0
for i in range(0, len(df_Merged)):
    if pd.isna(df_Merged.loc[i, 'Seasonality_Dummy']) == True:
        df_Merged.loc[i, 'Seasonality_Dummy'] = 0
    if df_Merged.loc[i, 'Volume'] == 0:
        df_Merged.drop([i], inplace = True)
    elif df_Merged.loc[i, 'TTM'] < 0:
        dropped_nonsense += 1
        df_Merged.drop([i], inplace = True)

dropped_defaults = 0
for i in range(0, len(df_CatBondLosses)):
    if df_CatBondLosses.loc[i, 'ISIN'] in df_Merged['ISIN'].values:
        dropped_defaults += 1
        df_Merged = df_Merged[df_Merged['ISIN'] != df_CatBondLosses.loc[i, 'ISIN']]
        df_Merged.drop(df_Merged[df_Merged['ISIN'] == df_CatBondLosses.loc[i, 'ISIN']].index, inplace = True)
    else:
        None

df_Merged['Corp_Credit_Spread'] = df_Merged['Corp_Credit_Spread'] / 100
df_Merged['Spread_Secondary'] = df_Merged['Spread_Secondary'] / 10000
df_Merged['Spread_Primary'] = df_Merged['Spread_Primary'] / 10000
df_Merged['EL'] = df_Merged['EL'] / 10000
df_Merged['Volume_log'] = np.log(df_Merged['Volume'])
columns = ['ISIN', 'Name', 'Issuance_Date', 'Maturity_Date', 'Term', 'TTM', 'Volume', 'Volume_log', 'Peril_Type', 'Peril_Types', 'Peril_Type_Dummy', 'Peril_Region', 'Peril_Regions', 'Peril_Region_Dummy', 'NA_EQ', 'NA_Hurricane', 'NA_Winterstorm', 'NA_Windstorm', 'JP_EQ', 'JP_Hurricane', 'JP_Winterstorm', 'JP_Windstorm', 'EU_EQ', 'EU_Winterstorm', 'EU_Windstorm', 'AUS_EQ', 'AUS_Hurricane', 'LA_EQ', 'LA_Hurricane', 'Seasonality_Dummy', 'Trigger_Type', 'Trigger_Type_Dummy', 'Rating', 'Rating_Dummy', 'Rating_Grade', 'Rating_Grade_Dummy', 'EL', 'Spread_Primary', 'Spread_Secondary', 'Price_Primary', 'Price_Secondary', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index', 'Ref_Date']
df_Merged = df_Merged[columns]
na_dropping_subset(df_Merged, ['EL', 'Volume', 'Volume_log', 'Term', 'TTM', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'Rating_Grade_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index'])
index_setting(df_Merged)
write_file(df_Merged, outputPath_Merged, 'df_final.csv', name_Merged)

print('-----AON----')
print('Unique Cat Bond Tranches:', df_AON['ISIN'].nunique())
print('Number of Observations:', len(df_AON))

print('-----SwissRe----')
print('Unique Cat Bond Tranches:', df_SwissRe['ISIN'].nunique())
print('Number of Observations:', len(df_SwissRe))

print('-----Nonsense Drops----')
print('Dropped Cat Bond Tranches:', dropped_nonsense)

print('-----Default/Loss Drops----')
print('Dropped Cat Bond Tranches:', dropped_defaults)

print('-----Merged----')
print('Unique Cat Bond Tranches:', df_Merged['ISIN'].nunique())
print('Number of Observations:', len(df_Merged))

# Process End
print('------------------')
print('DATA MERGING SUCCESSFULLY DONE.')
print('------------------')