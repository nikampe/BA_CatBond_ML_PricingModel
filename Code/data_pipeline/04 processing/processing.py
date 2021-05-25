#############################################################################################
# Author: Niklas Leander Kampe - Bachelor Thesis
# Supervisor: Prof. Dr. Alexander Braun - Institute for Insurance Economics
# Step 4: Processing the merged data set
#############################################################################################

import pandas as pd
import numpy as np
from datetime import datetime
import math
import seaborn as sn
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols, wls
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_white, het_breuschpagan, het_goldfeldquandt
from statsmodels.compat import lzip
from statsmodels.graphics.gofplots import qqplot
from statsmodels.tools.eval_measures import rmse
from sklearn import metrics
from sklearn.model_selection import GridSearchCV, train_test_split, GroupShuffleSplit, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, Ridge, LinearRegression, ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.metrics import make_scorer
from keras.models import Sequential
from keras.layers import Dense

def read_file(inputPath, name):
    df = pd.read_csv(inputPath, index_col = 0)
    print(name, 'data set successfully imported.')
    return df

def write_file(df, outputPath, fileName, name):
    df.to_csv(outputPath + fileName)
    print(name, 'data set successfully saved.')

def index_setting(df):
    index = range(0, len(df))
    df['Index'] = index
    df.set_index('Index', inplace = True)
    return df

# -----------------------------------------------------------------------------------

# Process Start
print('------------------')
print('DATA PROCESSING SUCCESSFULLY INITIATED.')
print('------------------')

# Raw Data Sets
name_AON = 'AON'
name_LaneFinacial = 'Lane Financial'
name_SwissRe = 'Swiss Re'
name_SP500 = 'S&P 500'
name_RoL = 'Rate-on-Line Index'
name_CreditSpreads = 'US Corporate Credit Spreads'
inputPath_AON = r'Working Data/AON_cleaned/df_AON_raw.csv'
inputPath_LaneFinancial = r'Working Data/LaneFinancial_cleaned/df_LaneFinancial_cleaned.csv'
inputPath_SwissRe = r'Working Data/SwissRe_cleaned/df_SwissRe_raw.csv'
inputPath_SP500 = r'Working Data/S&P500_cleaned/df_S&P500_cleaned.csv'
inputPath_RoL = r'Working Data/RoL_cleaned/df_RoL_cleaned.csv'
inputPath_CreditSpreads = r'Working Data/CreditSpreads_cleaned/df_CreditSpreads_cleaned.csv'
## Importing
df_AON_raw = read_file(inputPath_AON, name_AON)
df_LaneFinancial_raw = read_file(inputPath_LaneFinancial, name_LaneFinacial)
df_SwissRe_raw = read_file(inputPath_SwissRe, name_SwissRe)
df_SP500_raw = read_file(inputPath_SP500, name_SP500)
df_RoL_raw = read_file(inputPath_RoL, name_RoL)
df_CreditSpreads = read_file(inputPath_CreditSpreads, name_CreditSpreads)

# Final Data Set
name = 'Final Data Set'
inputPath = r'Final Data/df_final.csv'
## Importing
df_final = read_file(inputPath, name)

# -----------------------------------------------------------------------------------

# Summary Statistic - Raw Data Sets
summary_statistic_raw = pd.DataFrame(
    {
        'Unique': [
            '',
            df_AON_raw['Name'].nunique(),
            df_LaneFinancial_raw['CAT Issues'].nunique(),
            df_SwissRe_raw['Name'].nunique(),
            '',
            'N/A',
            'N/A',
            'N/A',
        ],
        'Obs.': [
            '',
            len(df_AON_raw),
            len(df_LaneFinancial_raw),
            len(df_SwissRe_raw),
            '',
            len(df_SP500_raw),
            len(df_RoL_raw),
            len(df_CreditSpreads) * len(df_CreditSpreads.columns),
        ],
        'Issue (Min)': [
            '',
            df_AON_raw['Issuance_Date'].min(),
            df_LaneFinancial_raw['Issue Date'].min(),
            '2003-06-19',
            '',
            'N/A',
            'N/A',
            'N/A',
        ],
        'Issue (Max)': [
            '',
            df_AON_raw['Issuance_Date'].max(),
            df_LaneFinancial_raw['Issue Date'].max(),
            '2020-12-21',
            '',
            'N/A',
            'N/A',
            'N/A',
        ],
        'Ref (Min)': [
            '',
            df_AON_raw['Ref_Date'].min(),
            'N/A',
            df_SwissRe_raw['Ref_Date'].min(),
            '',
            df_SP500_raw['Date'].min(),
            df_RoL_raw['Year'].min(),
            df_CreditSpreads['Date'].min(),
        ],
        'Ref (Max)': [
            '',
            df_AON_raw['Ref_Date'].max(),
            'N/A',
            df_SwissRe_raw['Ref_Date'].max(),
            '',
            df_SP500_raw['Date'].max(),
            df_RoL_raw['Year'].max(),
            df_CreditSpreads['Date'].max(),
        ],
        'Prim.': [
            '',
            'Yes',
            'Yes',
            'Yes',
            '',
            'N/A',
            'N/A',
            'N/A',
        ],
        'Sec.': [
            '',
            'Yes',
            'No',
            'Yes',
            '',
            'N/A',
            'N/A',
            'N/A',
        ]
    },
    index = ['Cat Bond-specific Data', '  AON', '  Lane Financial', '  Swiss Re', 'Macroeconomic Data', "  Standard & Poor's",  '  Guy Capenter', '  BofA Merril Lynch']
)
print(summary_statistic_raw)
latex_code_statistics_raw = summary_statistic_raw.to_latex()
with open(r'Figures, Tables & LaTex Code/01 Descriptive_Statistics_Raw.tex', 'w') as file_summary_statistic_raw:
    file_summary_statistic_raw.write(latex_code_statistics_raw)

# Variable Selection
variable_overview = pd.DataFrame(
    {
        'Description': [
            'Spread as of reference date in addition to reference floating interest rate (variable of interest)',
            '"International Securities Identification Number" - Unique identifier for cat bonds',
            'Name of the cat bond or the specific cat bond tranch/class',
            'Date when the cat bond was issued',
            'Date when the cat bond matures/expires',
            'Difference between maturity date and issuance date (in months)',
            'Difference between maturity date and observation/reference date (in months)',
            'Total amount of the accumulated, paid-in principals',
            'Natural logarithm of the total amount of the accumulated, paid-in principals',
            'Modelled loss percentage of the nominal value within one year',
            'Type of natural disaster covered by the cat bond',
            'Number of peril types covered by the cat bond',
            '1 = multi peril types; 0 = else',
            'Natural disaster affected geographical region covered by the cat bond',
            'Number of geographical regions covered by the cat bond',
            '1 = multi peril regions; 0 = else',
            '1 = any included peril type-region combination has high season as of reference date',
            'Type of trigger that leads to partial/full payout',
            '1 = indemnity; 0 = else',
            "Uniformed bond rating (aggregated by S&P, Moody's and Fitch)",
            '0 = No rating; 1 = B; 2 = BB; 3 = BBB; 4 = A; 5 = AA; 6 = AAA',
            'Investment, non-investment grade or not-rated grade based on aggregated rating',
            '1 = Investment grade (BBB or higher); 0 = else',
            'Cat bond market price at issuance',
            'Cat bond market price as of reference date',
            'Date of observation (quarterly)',
            'Quarterly return of the S&P500 as the benchmark financial market index',
            'Year-on-year percentage change of the Guy Carpenter Rate-on-Line Index',
            'US corporate credit spreads of different rating classes as of reference date'
        ]
    },
    index = ['Spread', 'ISIN', 'Name', 'Issuance Date', 'Maturity Date', 'Term', 'TTM', 'Volume', 'Volume_log', 'EL', 'Peril Type', 'Peril Types', 'Peril Type*', 'Peril Region', 'Peril Regions', 'Peril Region*', 'Seasonality*', 'Trigger Type', 'Trigger Type*', 'Rating Aggregated', 'Rating', 'Rating Grade', 'Rating Grade*', 'Price Primary', 'Price Secondary', 'Ref Date', 'S&P500 Return ', 'RoL Index', 'Corp. Credit Spread']
)
print(variable_overview)
latex_code_variable_overview = variable_overview.to_latex()
with open(r'Figures, Tables & LaTex Code/02 Variable_Selection.tex', 'w') as file_regr_variable_overview:
    file_regr_variable_overview.write(latex_code_variable_overview)

# Summary Statistic Fixed - Cat Bond Determinants
summary_statistic_fixed = pd.DataFrame(
    {
        'Count': [
            '',
            df_final['Trigger_Type'].value_counts()['Indemnity'],
            df_final['Trigger_Type'].value_counts()['Industry Loss Index'],
            df_final['Trigger_Type'].value_counts()['Parametric'],
            df_final['Trigger_Type'].value_counts()['Mortality Index'],
            df_final['Trigger_Type'].value_counts()['Modelled Loss'],
            df_final['Trigger_Type'].value_counts()['Multi'],
            df_final['Trigger_Type'].value_counts()['Indemnity'] + df_final['Trigger_Type'].value_counts()['Parametric'] + df_final['Trigger_Type'].value_counts()['Industry Loss Index'] + df_final['Trigger_Type'].value_counts()['Modelled Loss'] + df_final['Trigger_Type'].value_counts()['Mortality Index'] + df_final['Trigger_Type'].value_counts()['Multi'],
            '',
            len(df_final[df_final['Peril_Type'].str.contains('Hurricane')]),
            len(df_final[df_final['Peril_Type'].str.contains('EQ')]),
            len(df_final[df_final['Peril_Type'].str.contains('Wind')]),
            len(df_final[df_final['Peril_Type'].str.contains('Other')]),
            '',
            len(df_final[df_final['Peril_Region'].str.contains('North America')]),
            len(df_final[df_final['Peril_Region'].str.contains('Europe')]),
            len(df_final[df_final['Peril_Region'].str.contains('Japan')]),
            len(df_final[df_final['Peril_Region'].str.contains('Other')]),
            '',
            len(df_final[df_final['NA_Hurricane'] == 1]),
            len(df_final[df_final['NA_EQ'] == 1]),
            len(df_final[df_final['NA_Winterstorm'] == 1]),
            len(df_final[df_final['NA_Windstorm'] == 1]),
            len(df_final[df_final['JP_EQ'] == 1]),
            len(df_final[df_final['JP_Hurricane'] == 1]),
            len(df_final[df_final['JP_Winterstorm'] == 1]),
            len(df_final[df_final['JP_Windstorm'] == 1]),
            len(df_final[df_final['EU_Windstorm'] == 1]),
            len(df_final[df_final['EU_EQ'] == 1]),
            len(df_final[df_final['EU_Winterstorm'] == 1]),
            len(df_final[df_final['AUS_Hurricane'] == 1]),
            len(df_final[df_final['AUS_EQ'] == 1]),
            len(df_final[df_final['LA_Hurricane'] == 1]),
            len(df_final[df_final['LA_EQ'] == 1]),
            '',
            len(df_final[df_final['Rating_Dummy'] == 6]),
            len(df_final[df_final['Rating_Dummy'] == 5]),
            len(df_final[df_final['Rating_Dummy'] == 4]),
            len(df_final[df_final['Rating_Dummy'] == 3]),
            len(df_final[df_final['Rating_Dummy'] == 6]) + len(df_final[df_final['Rating_Dummy'] == 5]) + len(df_final[df_final['Rating_Dummy'] == 4]) + len(df_final[df_final['Rating_Dummy'] == 3]),
            len(df_final[df_final['Rating_Dummy'] == 2]),
            len(df_final[df_final['Rating_Dummy'] == 1]),
            len(df_final[df_final['Rating_Dummy'] == 2]) + len(df_final[df_final['Rating_Dummy'] == 1]),
            len(df_final[df_final['Rating_Dummy'] == 0]),
            len(df_final[df_final['Rating_Dummy'] == 6]) + len(df_final[df_final['Rating_Dummy'] == 5]) + len(df_final[df_final['Rating_Dummy'] == 4]) + len(df_final[df_final['Rating_Dummy'] == 3]) + len(df_final[df_final['Rating_Dummy'] == 2]) + len(df_final[df_final['Rating_Dummy'] == 1]) + len(df_final[df_final['Rating_Dummy'] == 0]),
        ],
        'Percentage': [
            '',
            round(df_final['Trigger_Type'].value_counts()['Indemnity'] / len(df_final['Trigger_Type']) * 100, 2),
            round(df_final['Trigger_Type'].value_counts()['Industry Loss Index'] / len(df_final['Trigger_Type']) * 100, 2),
            round(df_final['Trigger_Type'].value_counts()['Parametric'] / len(df_final['Trigger_Type']) * 100, 2),
            round(df_final['Trigger_Type'].value_counts()['Mortality Index'] / len(df_final['Trigger_Type']) * 100, 2),
            round(df_final['Trigger_Type'].value_counts()['Modelled Loss'] / len(df_final['Trigger_Type']) * 100, 2),
            round(df_final['Trigger_Type'].value_counts()['Multi'] / len(df_final['Trigger_Type']) * 100, 2),
            round((df_final['Trigger_Type'].value_counts()['Indemnity'] + df_final['Trigger_Type'].value_counts()['Parametric'] + df_final['Trigger_Type'].value_counts()['Industry Loss Index'] + df_final['Trigger_Type'].value_counts()['Modelled Loss'] + df_final['Trigger_Type'].value_counts()['Mortality Index'] + df_final['Trigger_Type'].value_counts()['Multi']) / len(df_final['Trigger_Type']) * 100, 2),
            '',
            round(len(df_final[df_final['Peril_Type'].str.contains('Hurricane')]) / len(df_final['Peril_Type']) * 100, 2),
            round(len(df_final[df_final['Peril_Type'].str.contains('EQ')]) / len(df_final['Peril_Type']) * 100, 2),
            round(len(df_final[df_final['Peril_Type'].str.contains('Wind')]) / len(df_final['Peril_Type']) * 100, 2),
            round(len(df_final[df_final['Peril_Type'].str.contains('Other')]) / len(df_final['Peril_Type']) * 100, 2),
            '',
            round(len(df_final[df_final['Peril_Region'].str.contains('North America')]) / len(df_final['Peril_Region']) * 100, 2),
            round(len(df_final[df_final['Peril_Region'].str.contains('Europe')]) / len(df_final['Peril_Region']) * 100, 2),
            round(len(df_final[df_final['Peril_Region'].str.contains('Japan')]) / len(df_final['Peril_Region']) * 100, 2),
            round(len(df_final[df_final['Peril_Region'].str.contains('Other')]) / len(df_final['Peril_Region']) * 100, 2),
            '',
            round(len(df_final[df_final['NA_Hurricane'] == 1]) / len(df_final['NA_Hurricane']) * 100, 2),
            round(len(df_final[df_final['NA_EQ'] == 1]) / len(df_final['NA_EQ']) * 100, 2),
            round(len(df_final[df_final['NA_Winterstorm'] == 1]) / len(df_final['NA_Winterstorm']) * 100, 2),
            round(len(df_final[df_final['NA_Windstorm'] == 1]) / len(df_final['NA_Windstorm']) * 100, 2),
            round(len(df_final[df_final['JP_EQ'] == 1]) / len(df_final['JP_EQ']) * 100, 2),
            round(len(df_final[df_final['JP_Hurricane'] == 1]) / len(df_final['JP_Hurricane']) * 100, 2),
            round(len(df_final[df_final['JP_Winterstorm'] == 1]) / len(df_final['JP_Winterstorm']) * 100, 2),
            round(len(df_final[df_final['JP_Windstorm'] == 1]) / len(df_final['JP_Windstorm']) * 100, 2),
            round(len(df_final[df_final['EU_Windstorm'] == 1]) / len(df_final['EU_Windstorm']) * 100, 2),
            round(len(df_final[df_final['EU_EQ'] == 1]) / len(df_final['EU_EQ']) * 100, 2),
            round(len(df_final[df_final['EU_Winterstorm'] == 1]) / len(df_final['EU_Winterstorm']) * 100, 2),
            round(len(df_final[df_final['AUS_Hurricane'] == 1]) / len(df_final['AUS_Hurricane']) * 100, 2),
            round(len(df_final[df_final['AUS_EQ'] == 1]) / len(df_final['AUS_EQ']) * 100, 2),
            round(len(df_final[df_final['LA_Hurricane'] == 1]) / len(df_final['LA_Hurricane']) * 100, 2),
            round(len(df_final[df_final['LA_EQ'] == 1]) / len(df_final['LA_EQ']) * 100, 2),
            '',
            round(len(df_final[df_final['Rating_Dummy'] == 6]) / len(df_final['Rating_Dummy']) * 100, 2),
            round(len(df_final[df_final['Rating_Dummy'] == 5]) / len(df_final['Rating_Dummy']) * 100, 2),
            round(len(df_final[df_final['Rating_Dummy'] == 4]) / len(df_final['Rating_Dummy']) * 100, 2),
            round(len(df_final[df_final['Rating_Dummy'] == 3]) / len(df_final['Rating_Dummy']) * 100, 2),
            round((len(df_final[df_final['Rating_Dummy'] == 6]) + len(df_final[df_final['Rating_Dummy'] == 5]) + len(df_final[df_final['Rating_Dummy'] == 4]) + len(df_final[df_final['Rating_Dummy'] == 3])) / len(df_final['Rating_Dummy']) * 100, 2),
            round(len(df_final[df_final['Rating_Dummy'] == 2]) / len(df_final['Rating_Dummy']) * 100, 2),
            round(len(df_final[df_final['Rating_Dummy'] == 1]) / len(df_final['Rating_Dummy']) * 100, 2),
            round((len(df_final[df_final['Rating_Dummy'] == 2]) + len(df_final[df_final['Rating_Dummy'] == 1])) / len(df_final['Rating_Dummy']) * 100, 2),
            round(len(df_final[df_final['Rating_Dummy'] == 0]) / len(df_final['Rating_Dummy']) * 100, 2),
            round((len(df_final[df_final['Rating_Dummy'] == 6]) + len(df_final[df_final['Rating_Dummy'] == 5]) + len(df_final[df_final['Rating_Dummy'] == 4]) + len(df_final[df_final['Rating_Dummy'] == 3]) + len(df_final[df_final['Rating_Dummy'] == 2]) + len(df_final[df_final['Rating_Dummy'] == 1]) + len(df_final[df_final['Rating_Dummy'] == 0])) / len(df_final['Rating_Dummy']) * 100, 2),
        ]
    },
    index = ['Trigger Type', '  Indemnity', '  Industry Loss Index', '  Parametric', '  Mortality Index', '  Modelled Loss', '  Multi', '  Subtotal - Trigger Type', 'Peril Type', '  Hurricane', '  Earthquake','  Wind', '  Other', 'Peril Region', '  North America', '  Europe', '  Japan', '  Other', '  -----', '  NA - Hurricane', '  NA - EQ', '  NA - Winterstorm', '  NA - Windstorm', '  JP - EQ', '  JP - Typhoon', '  JP - Winterstorm', '  JP - Windstorm', '  EUR - Windstorm', '  EUR - EQ', '  EUR - Winterstorm', '  AUS - Cyclone', '  AUS - EQ', '  LA - Hurricane', '  LA - EQ', 'Rating', '  AAA', '  AA', '  A', '  BBB', '  Subsubtotal - IG', '  BB', '  B', '  Subsubtotal - NIG', '  NR', '  Subtotal - Rating']
)
print(summary_statistic_fixed)
latex_code_summary_statistic_fixed = summary_statistic_fixed.to_latex()
with open(r'Figures, Tables & LaTex Code/03 Descriptive_Statistics_Fixed.tex', 'w') as file_summary_statistic_fixed:
    file_summary_statistic_fixed.write(latex_code_summary_statistic_fixed)

# Summary Statistic Floating - Cat Bond Determinants
summary_statistic_floating = pd.DataFrame(
    {
        'Obs': [
            len(df_final['Spread_Secondary']),
            len(df_final['EL']),
            len(df_final['ISIN'].unique()),
            len(df_final['ISIN'].unique()),
            len(df_final['TTM']),
            len(df_final['ISIN'].unique()),
            len(df_final['ISIN'].unique()),
            '',
            len(df_final['SP500_Quarterly_Return'].unique()),
            len(df_final['Corp_Credit_Spread'].unique()),
            len(df_final['Rate_on_Line_Index'].unique()),
        ],
        'Mean': [
            round((df_final['Spread_Secondary'] * 100).mean(), 2),
            round((df_final['EL'] * 100).mean(), 2),
            round(df_final['Volume'].mean(), 2),
            round(df_final['Term'].mean(), 2),
            round(df_final['TTM'].mean(), 2),
            round(df_final['Peril_Types'].mean(), 2),
            round(df_final['Peril_Regions'].mean(), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).mean(), 2),
            round((df_final['Corp_Credit_Spread'] * 100).mean(), 2),
            round((df_final['Rate_on_Line_Index'] * 100).mean(), 2),
        ],
        'Std. Dev.': [
            round((df_final['Spread_Secondary'] * 100).std(), 2),
            round((df_final['EL'] * 100).std(), 2),
            round(df_final['Volume'].std(), 2),
            round(df_final['Term'].std(), 2),
            round(df_final['TTM'].std(), 2),
            round(df_final['Peril_Types'].std(), 2),
            round(df_final['Peril_Regions'].std(), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).std(), 2),
            round((df_final['Corp_Credit_Spread'] * 100).std(), 2),
            round((df_final['Rate_on_Line_Index'] * 100).std(), 2),
        ],
        'Min': [
            round((df_final['Spread_Secondary'] * 100).min(), 2),
            round((df_final['EL'] * 100).min(), 2),
            round(df_final['Volume'].min(), 2),
            round(df_final['Term'].min(), 2),
            round(df_final['TTM'].min(), 2),
            round(df_final['Peril_Types'].min(), 2),
            round(df_final['Peril_Regions'].min(), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).min(), 2),
            round((df_final['Corp_Credit_Spread'] * 100).min(), 2),
            round((df_final['Rate_on_Line_Index'] * 100).min(), 2),
        ],
        'Q25': [
            round((df_final['Spread_Secondary'] * 100).quantile(q = 0.25), 2),
            round((df_final['EL'] * 100).quantile(q = 0.25), 2),
            round(df_final['Volume'].quantile(q = 0.25), 2),
            round(df_final['Term'].quantile(q = 0.25), 2),
            round(df_final['TTM'].quantile(q = 0.25), 2),
            round(df_final['Peril_Types'].quantile(q = 0.25), 2),
            round(df_final['Peril_Regions'].quantile(q = 0.25), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).quantile(q = 0.25), 2),
            round((df_final['Corp_Credit_Spread'] * 100).quantile(q = 0.25), 2),
            round((df_final['Rate_on_Line_Index'] * 100).quantile(q = 0.25), 2),
        ],
        'Med': [
            round((df_final['Spread_Secondary'] * 100).median(), 2),
            round((df_final['EL'] * 100).median(), 2),
            round(df_final['Volume'].median(), 2),
            round(df_final['Term'].median(), 2),
            round(df_final['TTM'].median(), 2),
            round(df_final['Peril_Types'].median(), 2),
            round(df_final['Peril_Regions'].median(), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).median(), 2),
            round((df_final['Corp_Credit_Spread'] * 100).median(), 2),
            round((df_final['Rate_on_Line_Index'] * 100).median(), 2),
        ],
        'Q75': [
            round((df_final['Spread_Secondary'] * 100).quantile(q = 0.75), 2),
            round((df_final['EL'] * 100).quantile(q = 0.75), 2),
            round(df_final['Volume'].quantile(q = 0.75), 2),
            round(df_final['Term'].quantile(q = 0.75), 2),
            round(df_final['TTM'].quantile(q = 0.75), 2),
            round(df_final['Peril_Types'].quantile(q = 0.75), 2),
            round(df_final['Peril_Regions'].quantile(q = 0.75), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).quantile(q = 0.75), 2),
            round((df_final['Corp_Credit_Spread'] * 100).quantile(q = 0.75), 2),
            round((df_final['Rate_on_Line_Index'] * 100).quantile(q = 0.75), 2),
        ],
        'Max': [
            round((df_final['Spread_Secondary'] * 100).max(), 2),
            round((df_final['EL'] * 100).max(), 2),
            round(df_final['Volume'].max(), 2),
            round(df_final['Term'].max(), 2),
            round(df_final['TTM'].max(), 2),
            round(df_final['Peril_Types'].max(), 2),
            round(df_final['Peril_Regions'].max(), 2),
            '',
            round((df_final['SP500_Quarterly_Return'] * 100).max(), 2),
            round((df_final['Corp_Credit_Spread'] * 100).max(), 2),
            round((df_final['Rate_on_Line_Index'] * 100).max(), 2),
        ]
    },
    index = ['Spread Secondary (%)', 'EL (%)', 'Volume ($mio)', 'Term (mth)', 'TTM (mth)', 'Peril Types', 'Peril Regions', '-----', 'S&P500 Return (qr, %)', 'Corp. Spread (%)', 'RoL Index (yr, %)']
)
latex_code_summary_statistic_floating = summary_statistic_floating.to_latex()
print(summary_statistic_floating)
with open(r'Figures, Tables & LaTex Code/04 Descriptive_Statistics_Floating.tex', 'w') as file_summary_statistic_floating:
    file_summary_statistic_floating.write(latex_code_summary_statistic_floating)

# Correlation Matrix
correlation_data = df_final[['Spread_Secondary', 'EL', 'Volume', 'Term', 'TTM', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
correlation_data.rename(columns = {'Spread_Secondary': 'Spread', 'Peril_Types': 'Peril Types', 'Peril_Regions': 'Peril Regions', 'Seasonality_Dummy': 'Seasonality*', 'Trigger_Type_Dummy': 'Trigger Type*', 'Rating_Dummy': 'Rating*', 'SP500_Quarterly_Return': 'S&P500 Return', 'Corp_Credit_Spread': 'Corp. Spread', 'Rate_on_Line_Index': 'RoL Index'}, inplace = True)
correlation_matrix = round(correlation_data.corr(), 2)
cmap = sn.diverging_palette(10, 133, as_cmap = True)
mask = np.triu(np.ones_like(correlation_data.corr(), dtype = np.bool))
heatmap = sn.heatmap(correlation_matrix, vmin = -1, vmax = 1, mask = mask, cmap = cmap, annot = False, linewidths = .5)
heatmap.set_xticklabels(heatmap.get_xmajorticklabels(), fontsize = 10)
heatmap.set_yticklabels(heatmap.get_xmajorticklabels(), fontsize = 10)
plt.savefig('Figures, Tables & LaTex Code/06 Correlation_Heatmap.pdf', dpi = 300, bbox_inches = 'tight')
for i in range(0, len(correlation_matrix) - 1):
    for j in range(0, len(correlation_matrix) - 1):
        if (j + i + 1) <= (len(correlation_matrix) - 1):
            correlation_matrix.iloc[i, j + i + 1] = ''
        else:
            None
print(correlation_matrix)
latex_code_correlation_matrix = correlation_matrix.to_latex()
with open(r'Figures, Tables & LaTex Code/05 Correlation_Matrix.tex', 'w') as file_correlation_matrix:
    file_correlation_matrix.write(latex_code_correlation_matrix)

# Multicollinearity Check
x_temp = sm.add_constant(df_final[['EL', 'Volume', 'Term', 'TTM', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']])
VIF = pd.DataFrame()
VIF["VIF Factor"] = [variance_inflation_factor(x_temp.values, i) for i in range(x_temp.values.shape[1])]
VIF["Feature"] = x_temp.columns
VIF = VIF.round(2)
print(VIF)
latex_code_VIF = VIF.to_latex()
with open(r'Figures, Tables & LaTex Code/07 Variance_Inflation_Factors.tex', 'w') as file_VIF:
    file_VIF.write(latex_code_VIF)

# Heteroscedasticity Check - Residual Plot
regr = ols(formula = 'Spread_Secondary ~ EL + Volume + Term + TTM + Peril_Types + Peril_Regions + Seasonality_Dummy + Trigger_Type_Dummy + Rating_Dummy + SP500_Quarterly_Return + Corp_Credit_Spread + Rate_on_Line_Index', data = df_final).fit()
fig = plt.figure(num = 0, figsize = (10, 8))
plot_opts = dict(linestyle = "None", marker = "o", color = "black", markerfacecolor = "None")
_ = fig.add_subplot(2, 2, 1).plot(regr.resid, **plot_opts)
_ = plt.title("Residual Plot")
plt.savefig('Figures, Tables & LaTex Code/08 Residual_Plot.pdf', dpi = 300, bbox_inches = 'tight')

# Heteroscedasticity Check - White & Breusch Pagan Test
regr = ols(formula = 'Spread_Secondary ~ EL + Volume_log + Term + TTM + Peril_Types + Peril_Regions + Seasonality_Dummy + Trigger_Type_Dummy + Rating_Dummy + SP500_Quarterly_Return + Corp_Credit_Spread + Rate_on_Line_Index', data = df_final).fit()
white_test = het_white(resid = regr.resid, exog = regr.model.exog)
bp_test = het_breuschpagan(resid = regr.resid, exog_het = regr.model.exog)
test_summary = pd.DataFrame(
    {
        'White Test': [
            round(white_test[0], 4),
            round(white_test[1], 4),
            round(white_test[2], 4),
            round(white_test[3], 4),
        ],
        'Breusch-Pagan Test': [
            round(bp_test[0], 4),
            round(bp_test[1], 4),
            round(bp_test[2], 4),
            round(bp_test[3], 4),
        ],
    },
    index = ['LM Statistic', 'LM-Test p-value', 'F-Statistic', 'F-Test p-value']
)
print(test_summary)
latex_code_test_summary = test_summary.to_latex(index = True)
with open(r'Figures, Tables & LaTex Code/09 White_BreuschPagan_Test.tex', 'w') as file_test_summary:
    file_test_summary.write(latex_code_test_summary)

# Multiple Linear Regression
regr = ols(formula = 'Spread_Secondary ~ EL + Volume_log + Term + TTM + Peril_Types + Peril_Regions + Seasonality_Dummy + Trigger_Type_Dummy + Rating_Dummy + SP500_Quarterly_Return + Corp_Credit_Spread + Rate_on_Line_Index', data = df_final).fit(cov_type = 'HAC', cov_kwds = {'maxlags': 1})
regr_adjusted = ols(formula = 'Spread_Secondary ~ EL + Volume_log + Term + Peril_Types + Peril_Regions + Seasonality_Dummy + Trigger_Type_Dummy + Rating_Dummy + SP500_Quarterly_Return + Corp_Credit_Spread + Rate_on_Line_Index', data = df_final).fit(cov_type = 'HAC', cov_kwds = {'maxlags': 1})
print(regr.summary())
print(regr_adjusted.summary())
latex_code = regr.summary().as_latex()
latex_code_adjusted = regr_adjusted.summary().as_latex()
with open(r'Figures, Tables & LaTex Code/11.1 Multiple_Linear_Regression.tex', 'w') as file_regr:
    file_regr.write(latex_code)
with open(r'Figures, Tables & LaTex Code/11.2 Multiple_Linear_Regression_Adjusted.tex', 'w') as file_regr_adjusted:
    file_regr_adjusted.write(latex_code_adjusted)

# Rolling Sample Data Set Spliting
df_final_2003_2007 = df_final[(df_final['Ref_Date'] >= '2003-01-01') & (df_final['Ref_Date'] <= '2007-12-31')]
df_final_2003_2007_y = df_final_2003_2007['Spread_Secondary']
df_final_2003_2007_X = df_final_2003_2007[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2004_2008 = df_final[(df_final['Ref_Date'] >= '2004-01-01') & (df_final['Ref_Date'] <= '2008-12-31')]
df_final_2004_2008_y = df_final_2004_2008['Spread_Secondary']
df_final_2004_2008_X = df_final_2004_2008[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2005_2009 = df_final[(df_final['Ref_Date'] >= '2005-01-01') & (df_final['Ref_Date'] <= '2009-12-31')]
df_final_2005_2009_y = df_final_2005_2009['Spread_Secondary']
df_final_2005_2009_X = df_final_2005_2009[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2006_2010 = df_final[(df_final['Ref_Date'] >= '2006-01-01') & (df_final['Ref_Date'] <= '2010-12-31')]
df_final_2006_2010_y = df_final_2006_2010['Spread_Secondary']
df_final_2006_2010_X = df_final_2006_2010[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2007_2011 = df_final[(df_final['Ref_Date'] >= '2007-01-01') & (df_final['Ref_Date'] <= '2011-12-31')]
df_final_2007_2011_y = df_final_2007_2011['Spread_Secondary']
df_final_2007_2011_X = df_final_2007_2011[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2008_2012 = df_final[(df_final['Ref_Date'] >= '2008-01-01') & (df_final['Ref_Date'] <= '2012-12-31')]
df_final_2008_2012_y = df_final_2008_2012['Spread_Secondary']
df_final_2008_2012_X = df_final_2008_2012[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2009_2013 = df_final[(df_final['Ref_Date'] >= '2009-01-01') & (df_final['Ref_Date'] <= '2013-12-31')]
df_final_2009_2013_y = df_final_2009_2013['Spread_Secondary']
df_final_2009_2013_X = df_final_2009_2013[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2010_2014 = df_final[(df_final['Ref_Date'] >= '2010-01-01') & (df_final['Ref_Date'] <= '2014-12-31')]
df_final_2010_2014_y = df_final_2010_2014['Spread_Secondary']
df_final_2010_2014_X = df_final_2010_2014[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2011_2015 = df_final[(df_final['Ref_Date'] >= '2011-01-01') & (df_final['Ref_Date'] <= '2015-12-31')]
df_final_2011_2015_y = df_final_2011_2015['Spread_Secondary']
df_final_2011_2015_X = df_final_2011_2015[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2012_2016 = df_final[(df_final['Ref_Date'] >= '2012-01-01') & (df_final['Ref_Date'] <= '2016-12-31')]
df_final_2012_2016_y = df_final_2012_2016['Spread_Secondary']
df_final_2012_2016_X = df_final_2012_2016[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2013_2017 = df_final[(df_final['Ref_Date'] >= '2013-01-01') & (df_final['Ref_Date'] <= '2017-12-31')]
df_final_2013_2017_y = df_final_2013_2017['Spread_Secondary']
df_final_2013_2017_X = df_final_2013_2017[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2014_2018 = df_final[(df_final['Ref_Date'] >= '2014-01-01') & (df_final['Ref_Date'] <= '2018-12-31')]
df_final_2014_2018_y = df_final_2014_2018['Spread_Secondary']
df_final_2014_2018_X = df_final_2014_2018[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2015_2019 = df_final[(df_final['Ref_Date'] >= '2015-01-01') & (df_final['Ref_Date'] <= '2019-12-31')]
df_final_2015_2019_y = df_final_2015_2019['Spread_Secondary']
df_final_2015_2019_X = df_final_2015_2019[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]

df_final_2008 = df_final[(df_final['Ref_Date'] >= '2008-01-01') & (df_final['Ref_Date'] <= '2008-12-31')]
df_final_2008_y = df_final_2008['Spread_Secondary']
df_final_2008_X = df_final_2008[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2009 = df_final[(df_final['Ref_Date'] >= '2009-01-01') & (df_final['Ref_Date'] <= '2009-12-31')]
df_final_2009_y = df_final_2009['Spread_Secondary']
df_final_2009_X = df_final_2009[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2010 = df_final[(df_final['Ref_Date'] >= '2010-01-01') & (df_final['Ref_Date'] <= '2010-12-31')]
df_final_2010_y = df_final_2010['Spread_Secondary']
df_final_2010_X = df_final_2010[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2011 = df_final[(df_final['Ref_Date'] >= '2011-01-01') & (df_final['Ref_Date'] <= '2011-12-31')]
df_final_2011_y = df_final_2011['Spread_Secondary']
df_final_2011_X = df_final_2011[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2012 = df_final[(df_final['Ref_Date'] >= '2012-01-01') & (df_final['Ref_Date'] <= '2012-12-31')]
df_final_2012_y = df_final_2012['Spread_Secondary']
df_final_2012_X = df_final_2012[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2013 = df_final[(df_final['Ref_Date'] >= '2013-01-01') & (df_final['Ref_Date'] <= '2013-12-31')]
df_final_2013_y = df_final_2013['Spread_Secondary']
df_final_2013_X = df_final_2013[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2014 = df_final[(df_final['Ref_Date'] >= '2014-01-01') & (df_final['Ref_Date'] <= '2014-12-31')]
df_final_2014_y = df_final_2014['Spread_Secondary']
df_final_2014_X = df_final_2014[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2015 = df_final[(df_final['Ref_Date'] >= '2015-01-01') & (df_final['Ref_Date'] <= '2015-12-31')]
df_final_2015_y = df_final_2015['Spread_Secondary']
df_final_2015_X = df_final_2015[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2016 = df_final[(df_final['Ref_Date'] >= '2016-01-01') & (df_final['Ref_Date'] <= '2016-12-31')]
df_final_2016_y = df_final_2016['Spread_Secondary']
df_final_2016_X = df_final_2016[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2017 = df_final[(df_final['Ref_Date'] >= '2017-01-01') & (df_final['Ref_Date'] <= '2017-12-31')]
df_final_2017_y = df_final_2017['Spread_Secondary']
df_final_2017_X = df_final_2017[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2018 = df_final[(df_final['Ref_Date'] >= '2018-01-01') & (df_final['Ref_Date'] <= '2018-12-31')]
df_final_2018_y = df_final_2018['Spread_Secondary']
df_final_2018_X = df_final_2018[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2019 = df_final[(df_final['Ref_Date'] >= '2019-01-01') & (df_final['Ref_Date'] <= '2019-12-31')]
df_final_2019_y = df_final_2019['Spread_Secondary']
df_final_2019_X = df_final_2019[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2020 = df_final[(df_final['Ref_Date'] >= '2020-01-01') & (df_final['Ref_Date'] <= '2020-12-31')]
df_final_2020_y = df_final_2020['Spread_Secondary']
df_final_2020_X = df_final_2020[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]

df_final_2008_2009_robust = df_final[(df_final['Ref_Date'] >= '2008-01-01') & (df_final['Ref_Date'] <= '2009-12-31')]
df_final_2008_2009_robust_y = df_final_2008['Spread_Secondary']
df_final_2008_2009_robust_X = df_final_2008[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2009_2010_robust = df_final[(df_final['Ref_Date'] >= '2009-01-01') & (df_final['Ref_Date'] <= '2010-12-31')]
df_final_2009_2010_robust_y = df_final_2009['Spread_Secondary']
df_final_2009_2010_robust_X = df_final_2009[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2010_2011_robust = df_final[(df_final['Ref_Date'] >= '2010-01-01') & (df_final['Ref_Date'] <= '2011-12-31')]
df_final_2010_2011_robust_y = df_final_2010['Spread_Secondary']
df_final_2010_2011_robust_X = df_final_2010[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2011_2012_robust = df_final[(df_final['Ref_Date'] >= '2011-01-01') & (df_final['Ref_Date'] <= '2012-12-31')]
df_final_2011_2012_robust_y = df_final_2011['Spread_Secondary']
df_final_2011_2012_robust_X = df_final_2011[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2012_2013_robust = df_final[(df_final['Ref_Date'] >= '2012-01-01') & (df_final['Ref_Date'] <= '2013-12-31')]
df_final_2012_2013_robust_y = df_final_2012['Spread_Secondary']
df_final_2012_2013_robust_X = df_final_2012[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2013_2014_robust = df_final[(df_final['Ref_Date'] >= '2013-01-01') & (df_final['Ref_Date'] <= '2014-12-31')]
df_final_2013_2014_robust_y = df_final_2013['Spread_Secondary']
df_final_2013_2014_robust_X = df_final_2013[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2014_2015_robust = df_final[(df_final['Ref_Date'] >= '2014-01-01') & (df_final['Ref_Date'] <= '2015-12-31')]
df_final_2014_2015_robust_y = df_final_2014['Spread_Secondary']
df_final_2014_2015_robust_X = df_final_2014[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2015_2016_robust = df_final[(df_final['Ref_Date'] >= '2015-01-01') & (df_final['Ref_Date'] <= '2016-12-31')]
df_final_2015_2016_robust_y = df_final_2015['Spread_Secondary']
df_final_2015_2016_robust_X = df_final_2015[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2016_2017_robust = df_final[(df_final['Ref_Date'] >= '2016-01-01') & (df_final['Ref_Date'] <= '2017-12-31')]
df_final_2016_2017_robust_y = df_final_2016['Spread_Secondary']
df_final_2016_2017_robust_X = df_final_2016[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2017_2018_robust = df_final[(df_final['Ref_Date'] >= '2017-01-01') & (df_final['Ref_Date'] <= '2018-12-31')]
df_final_2017_2018_robust_y = df_final_2017['Spread_Secondary']
df_final_2017_2018_robust_X = df_final_2017[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2018_2019_robust = df_final[(df_final['Ref_Date'] >= '2018-01-01') & (df_final['Ref_Date'] <= '2019-12-31')]
df_final_2018_2019_robust_y = df_final_2018['Spread_Secondary']
df_final_2018_2019_robust_X = df_final_2018[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]
df_final_2019_2020_robust = df_final[(df_final['Ref_Date'] >= '2019-01-01') & (df_final['Ref_Date'] <= '2020-12-31')]
df_final_2019_2020_robust_y = df_final_2019['Spread_Secondary']
df_final_2019_2020_robust_X = df_final_2019[['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']]

IS_dates = ['2003-2007', '2004-2008', '2005-2009', '2006-2010', '2007-2011', '2008-2012', '2009-2013', '2010-2014', '2011-2015', '2012-2016', '2013-2017', '2014-2018', '2015-2019']
IS_data_y = [df_final_2003_2007_y, df_final_2004_2008_y, df_final_2005_2009_y, df_final_2006_2010_y, df_final_2007_2011_y, df_final_2008_2012_y, df_final_2009_2013_y, df_final_2010_2014_y, df_final_2011_2015_y, df_final_2012_2016_y, df_final_2013_2017_y, df_final_2014_2018_y, df_final_2015_2019_y]
IS_data_X = [df_final_2003_2007_X, df_final_2004_2008_X, df_final_2005_2009_X, df_final_2006_2010_X, df_final_2007_2011_X, df_final_2008_2012_X, df_final_2009_2013_X, df_final_2010_2014_X, df_final_2011_2015_X, df_final_2012_2016_X, df_final_2013_2017_X, df_final_2014_2018_X, df_final_2015_2019_X]
OOS_data_y = [df_final_2008_y, df_final_2009_y, df_final_2010_y, df_final_2011_y, df_final_2012_y, df_final_2013_y, df_final_2014_y, df_final_2015_y, df_final_2016_y, df_final_2017_y, df_final_2018_y, df_final_2019_y, df_final_2020_y]
OOS_data_X = [df_final_2008_X, df_final_2009_X, df_final_2010_X, df_final_2011_X, df_final_2012_X, df_final_2013_X, df_final_2014_X, df_final_2015_X, df_final_2016_X, df_final_2017_X, df_final_2018_X, df_final_2019_X, df_final_2020_X]
IS_data_robust_y = [df_final_2003_2007_y, df_final_2004_2008_y, df_final_2005_2009_y, df_final_2006_2010_y, df_final_2007_2011_y, df_final_2008_2012_y, df_final_2009_2013_y, df_final_2010_2014_y, df_final_2011_2015_y, df_final_2012_2016_y, df_final_2013_2017_y, df_final_2014_2018_y]
IS_data_robust_X = [df_final_2003_2007_X, df_final_2004_2008_X, df_final_2005_2009_X, df_final_2006_2010_X, df_final_2007_2011_X, df_final_2008_2012_X, df_final_2009_2013_X, df_final_2010_2014_X, df_final_2011_2015_X, df_final_2012_2016_X, df_final_2013_2017_X, df_final_2014_2018_X]
OOS_data_robust_y = [df_final_2008_2009_robust_y, df_final_2009_2010_robust_y, df_final_2010_2011_robust_y, df_final_2011_2012_robust_y, df_final_2012_2013_robust_y, df_final_2013_2014_robust_y, df_final_2014_2015_robust_y, df_final_2015_2016_robust_y, df_final_2016_2017_robust_y, df_final_2017_2018_robust_y, df_final_2018_2019_robust_y, df_final_2019_2020_robust_y]
OOS_data_robust_X = [df_final_2008_2009_robust_X, df_final_2009_2010_robust_X, df_final_2010_2011_robust_X, df_final_2011_2012_robust_X, df_final_2012_2013_robust_X, df_final_2013_2014_robust_X, df_final_2014_2015_robust_X, df_final_2015_2016_robust_X, df_final_2016_2017_robust_X, df_final_2017_2018_robust_X, df_final_2018_2019_robust_X, df_final_2019_2020_robust_X]

summary_statistic_Rolling_Samples = pd.DataFrame(
    {
        'IS': [
            '2003-2007', 
            '2004-2008', 
            '2005-2009', 
            '2006-2010', 
            '2007-2011', 
            '2008-2012', 
            '2009-2013', 
            '2010-2014', 
            '2011-2015', 
            '2012-2016', 
            '2013-2017', 
            '2014-2018', 
            '2015-2019',
        ],
        'No. Obs. IS': [
            len(df_final_2003_2007), 
            len(df_final_2004_2008), 
            len(df_final_2005_2009), 
            len(df_final_2006_2010), 
            len(df_final_2007_2011), 
            len(df_final_2008_2012), 
            len(df_final_2009_2013), 
            len(df_final_2010_2014), 
            len(df_final_2011_2015), 
            len(df_final_2012_2016), 
            len(df_final_2013_2017), 
            len(df_final_2014_2018), 
            len(df_final_2015_2019),
        ],
        'OOS': [
            '2008', 
            '2009', 
            '2010', 
            '2011', 
            '2012', 
            '2013', 
            '2014', 
            '2015', 
            '2016', 
            '2017', 
            '2018', 
            '2019', 
            '2020',
        ],
        'No. Obs. OOS': [
            len(df_final_2008), 
            len(df_final_2009), 
            len(df_final_2010), 
            len(df_final_2011), 
            len(df_final_2012), 
            len(df_final_2013), 
            len(df_final_2014), 
            len(df_final_2015), 
            len(df_final_2016), 
            len(df_final_2017), 
            len(df_final_2018), 
            len(df_final_2019), 
            len(df_final_2020),
        ],
        'OOS - Robustness': [
            '2008-2009', 
            '2009-2010', 
            '2010-2011', 
            '2011-2012', 
            '2012-2013', 
            '2013-2014', 
            '2014-2015', 
            '2015-2016', 
            '2016-2017', 
            '2017-2018', 
            '2018-2019', 
            '2019-2020', 
            'N/A',
        ],
        'No. Obs. OSS - Robustness': [
            len(df_final_2008_2009_robust), 
            len(df_final_2009_2010_robust), 
            len(df_final_2010_2011_robust), 
            len(df_final_2011_2012_robust), 
            len(df_final_2012_2013_robust), 
            len(df_final_2013_2014_robust), 
            len(df_final_2014_2015_robust), 
            len(df_final_2015_2016_robust), 
            len(df_final_2016_2017_robust), 
            len(df_final_2017_2018_robust), 
            len(df_final_2018_2019_robust), 
            len(df_final_2019_2020_robust), 
            'N/A'
        ]
    }
)
print(summary_statistic_Rolling_Samples)
latex_code_summary_statistic_Rolling_Samples = summary_statistic_Rolling_Samples.to_latex(index = False)
with open(r'Figures, Tables & LaTex Code/10 Summary_Statistics_Rolling_Samples.tex', 'w') as file_summary_statistic_Rolling_Samples:
    file_summary_statistic_Rolling_Samples.write(latex_code_summary_statistic_Rolling_Samples)

# Lasso, Ridge and Elastic Net Regression
## Hyperparameter Tuning
lasso_params = {
    'alpha': np.logspace(-8, 0, 200)
}
ridge_params = {
    'alpha': np.logspace(-8, 0, 200)
}
elstic_net_params = {
    'alpha': np.logspace(-8, 0, 200), 
    'l1_ratio': np.arange(0, 1, 200)
}
## Models
y = ['Spread_Secondary']
X = ['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']
grid_search_lasso = GridSearchCV(Lasso(), param_grid = lasso_params).fit(df_final[X], df_final[y].values.ravel())
grid_search_ridge = GridSearchCV(Ridge(), param_grid = ridge_params).fit(df_final[X], df_final[y].values.ravel())
grid_search_elastic_net = GridSearchCV(ElasticNet(), param_grid = elstic_net_params).fit(df_final[X], df_final[y].values.ravel())
models = {
    'OLS': LinearRegression(),
    'Lasso': grid_search_lasso.best_estimator_,
    'Ridge': grid_search_ridge.best_estimator_,
    'Elastic Net': grid_search_elastic_net.best_estimator_,
}
results = {
    'OLS': [],
    'Lasso': [],
    'Ridge': [],
    'Elastic Net': [],
}
for model in models:
    measures_regr = []
    for IS_y, IS_X, OOS_y, OOS_X in zip(IS_data_y, IS_data_X, OOS_data_y, OOS_data_X):
        measures_regr.append(np.round(np.sqrt(metrics.mean_squared_error(OOS_y, models[model].fit(IS_X, IS_y).predict(OOS_X), squared = True)), 4))
        corr_matrix = np.corrcoef(OOS_y, models[model].fit(IS_X, IS_y).predict(OOS_X))
        corr = corr_matrix[0,1]
        R_sq = corr**2
        measures_regr.append(np.round(R_sq, 4))
    measures_regr.append(np.round(np.mean(measures_regr[::2]), 4))
    measures_regr.append(np.round(np.mean(measures_regr[1::2]), 4))
    measures_regr.append(np.round(np.median(measures_regr[::2]), 4))
    measures_regr.append(np.round(np.median(measures_regr[1::2]), 4))
    measures_regr.append(np.round(np.std(measures_regr[::2]), 4))
    measures_regr.append(np.round(np.std(measures_regr[1::2]), 4))
    results[model] = measures_regr
results_robust = {
    'OLS': [],
    'Lasso': [],
    'Ridge': [],
    'Elastic Net': [],
}
for model in models:
    measures_regr_robust = []
    for IS_robust_y, IS_robust_X, OOS_robust_y, OOS_robust_X in zip(IS_data_robust_y, IS_data_robust_X, OOS_data_robust_y, OOS_data_robust_X):
        measures_regr_robust.append(np.round(np.sqrt(metrics.mean_squared_error(OOS_robust_y, models[model].fit(IS_robust_X, IS_robust_y).predict(OOS_robust_X), squared = True)), 4))
        corr_matrix = np.corrcoef(OOS_robust_y, models[model].fit(IS_robust_X, IS_robust_y).predict(OOS_robust_X))
        corr = corr_matrix[0,1]
        R_sq = corr**2
        measures_regr_robust.append(np.round(R_sq, 4))
    measures_regr_robust.append(np.round(np.mean(measures_regr_robust[::2]), 4))
    measures_regr_robust.append(np.round(np.mean(measures_regr_robust[1::2]), 4))
    measures_regr_robust.append(np.round(np.median(measures_regr_robust[::2]), 4))
    measures_regr_robust.append(np.round(np.median(measures_regr_robust[1::2]), 4))
    measures_regr_robust.append(np.round(np.std(measures_regr_robust[::2]), 4))
    measures_regr_robust.append(np.round(np.std(measures_regr_robust[1::2]), 4))
    results_robust[model] = measures_regr_robust
df_results_regr = pd.DataFrame.from_dict(results)
df_results_regr_robust = pd.DataFrame.from_dict(results_robust)
df_results_regr['IS'] = ['2003-2007', '', '2004-2008', '', '2005-2009', '', '2006-2010', '', '2007-2011', '', '2008-2012', '', '2009-2013', '', '2010-2014', '', '2011-2015', '', '2012-2016', '', '2013-2017', '', '2014-2018', '', '2015-2019', '', 'Mean', '', 'Median', '', 'Std. Dev.', '']
df_results_regr_robust['IS'] = ['2003-2007', '', '2004-2008', '', '2005-2009', '', '2006-2010', '', '2007-2011', '', '2008-2012', '', '2009-2013', '', '2010-2014', '', '2011-2015', '', '2012-2016', '', '2013-2017', '', '2014-2018', '', 'Mean', '', 'Median', '', 'Std. Dev.', '']
df_results_regr['OOS'] = ['2008', '', '2009', '', '2010', '', '2011', '', '2012', '', '2013', '', '2014', '', '2015', '', '2016', '', '2017', '', '2018', '', '2019', '', '2020', '', '', '', '', '', '', '']
df_results_regr_robust['OOS'] = ['2008-2009', '', '2009-2010', '', '2010-2011', '', '2011-2012', '', '2012-2013', '', '2013-2014', '', '2014-2015', '', '2015-2016', '', '2016-2017', '', '2017-2018', '', '2018-2019', '', '2019-2020', '', '', '', '', '', '', '']
df_results_regr['Measure'] = ['RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2']
df_results_regr_robust['Measure'] = ['RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2']
df_results_regr = df_results_regr[['IS', 'OOS', 'Measure', 'OLS', 'Lasso', 'Ridge', 'Elastic Net']]
df_results_regr_robust = df_results_regr_robust[['IS', 'OOS', 'Measure', 'OLS', 'Lasso', 'Ridge', 'Elastic Net']]
print(df_results_regr)
print(df_results_regr_robust)
print('Params Lasso: ', grid_search_lasso.best_params_)
print('Params Ridge: ', grid_search_ridge.best_params_)
print('Elastic Net: ', grid_search_elastic_net.best_params_)
df_results_regr.to_csv(r'Final Data/Forecast_Results/results_regression.csv')
df_results_regr_robust.to_csv(r'Final Data/Forecast_Results/results_regression_robustness.csv')
latex_code_regr = df_results_regr.to_latex(index = False)
latex_code_regr_robust = df_results_regr_robust.to_latex(index = False)
with open(r'Figures, Tables & LaTex Code/12 OLS_Lasso_Ridge_ElasticNet.tex', 'w') as file_regr:
    file_regr.write(latex_code_regr)
with open(r'Figures, Tables & LaTex Code/13 OLS_Lasso_Ridge_ElasticNet_Robustness.tex', 'w') as file_regr:
    file_regr.write(latex_code_regr_robust)

# Random Forest
df_results_regr = read_file(r'Final Data/Forecast_Results/results_regression.csv', 'Regression Forecasts')
df_results_regr_robust = read_file(r'Final Data/Forecast_Results/results_regression_robustness.csv', 'Regression Forecasts Robustness')
## Hyperparameter Tuning
RF_grid = {
    'n_estimators': [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)],
    'max_features': ['auto', 'sqrt'],
    'max_depth': [int(x) for x in np.linspace(start = 10, stop = 110, num = 11)],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'bootstrap': [True, False]
}
RF_grid_validated = {
    'n_estimators': [200],
    'max_features': ['sqrt'],
    'max_depth': [30],
    'min_samples_split': [5],
    'min_samples_leaf': [2],
    'bootstrap': [True]
}
## Models
y = ['Spread_Secondary']
X = ['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']
rf = RandomForestRegressor(random_state = 11)
def accuracy_score_RF(orig, pred):
    RMSE = np.sqrt(((pred - orig) ** 2).mean())
    return RMSE
custom_Scoring = make_scorer(accuracy_score_RF, greater_is_better = False)
rf_random = GridSearchCV(estimator = rf, param_grid = RF_grid_validated, scoring = custom_Scoring, cv = 5).fit(df_final[X], df_final[y].values.ravel()) 
best_random = rf_random.best_estimator_
results = {
    'RF': [],
}
measures_RF = []
for IS_y, IS_X, OOS_y, OOS_X in zip(IS_data_y, IS_data_X, OOS_data_y, OOS_data_X): 
    measures_RF.append(np.round(np.sqrt(metrics.mean_squared_error(OOS_y, best_random.predict(OOS_X), squared = True)), 4))
    corr_matrix = np.corrcoef(OOS_y, best_random.predict(OOS_X))
    corr = corr_matrix[0,1]
    R_sq = corr**2
    measures_RF.append(np.round(R_sq, 4)) 
measures_RF.append(np.round(np.mean(measures_RF[::2]), 4))
measures_RF.append(np.round(np.mean(measures_RF[1::2]), 4))
measures_RF.append(np.round(np.median(measures_RF[::2]), 4))
measures_RF.append(np.round(np.median(measures_RF[1::2]), 4))
measures_RF.append(np.round(np.std(measures_RF[::2]), 4))
measures_RF.append(np.round(np.std(measures_RF[1::2]), 4))
results['RF'] = measures_RF
results_robust = {
    'RF': [],
}
measures_RF_robust = []
for IS_robust_y, IS_robust_X, OOS_robust_y, OOS_robust_X in zip(IS_data_robust_y, IS_data_robust_X, OOS_data_robust_y, OOS_data_robust_X):
    measures_RF_robust.append(np.round(np.sqrt(metrics.mean_squared_error(OOS_robust_y, best_random.predict(OOS_robust_X), squared = True)), 4))
    corr_matrix = np.corrcoef(OOS_robust_y, best_random.predict(OOS_robust_X))
    corr = corr_matrix[0,1]
    R_sq = corr**2
    measures_RF_robust.append(np.round(R_sq, 4))
measures_RF_robust.append(np.round(np.mean(measures_RF_robust[::2]), 4))
measures_RF_robust.append(np.round(np.mean(measures_RF_robust[1::2]), 4))
measures_RF_robust.append(np.round(np.median(measures_RF_robust[::2]), 4))
measures_RF_robust.append(np.round(np.median(measures_RF_robust[1::2]), 4))
measures_RF_robust.append(np.round(np.std(measures_RF_robust[::2]), 4))
measures_RF_robust.append(np.round(np.std(measures_RF_robust[1::2]), 4))
results_robust['RF'] = measures_RF_robust
df_results_RF = pd.DataFrame.from_dict(results)
df_results_RF_robust = pd.DataFrame.from_dict(results_robust)
df_results_RF['IS'] = ['2003-2007', '', '2004-2008', '', '2005-2009', '', '2006-2010', '', '2007-2011', '', '2008-2012', '', '2009-2013', '', '2010-2014', '', '2011-2015', '', '2012-2016', '', '2013-2017', '', '2014-2018', '', '2015-2019', '', 'Mean', '', 'Median', '', 'Std. Dev.', '']
df_results_RF_robust['IS'] = ['2003-2007', '', '2004-2008', '', '2005-2009', '', '2006-2010', '', '2007-2011', '', '2008-2012', '', '2009-2013', '', '2010-2014', '', '2011-2015', '', '2012-2016', '', '2013-2017', '', '2014-2018', '', 'Mean', '', 'Median', '', 'Std. Dev.', '']
df_results_RF['OOS'] = ['2008', '', '2009', '', '2010', '', '2011', '', '2012', '', '2013', '', '2014', '', '2015', '', '2016', '', '2017', '', '2018', '', '2019', '', '2020', '', '', '', '', '', '', '']
df_results_RF_robust['OOS'] = ['2008-2009', '', '2009-2010', '', '2010-2011', '', '2011-2012', '', '2012-2013', '', '2013-2014', '', '2014-2015', '', '2015-2016', '', '2016-2017', '', '2017-2018', '', '2018-2019', '', '2019-2020', '', '', '', '', '', '', '']
df_results_RF['Measure'] = ['RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2']
df_results_RF_robust['Measure'] = ['RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2']
df_results_RF = df_results_RF['RF']
df_results_RF_robust = df_results_RF_robust['RF']
df_results_regr_RF = pd.concat([df_results_regr, df_results_RF], axis = 1)
df_results_regr_RF_robust = pd.concat([df_results_regr_robust, df_results_RF_robust], axis = 1)
print(df_results_regr_RF)
print(df_results_regr_RF_robust)
print('Params RF:', rf_random.best_params_)
df_results_regr_RF.to_csv(r'Final Data/Forecast_Results/results_regression_randomforest.csv')
df_results_regr_RF_robust.to_csv(r'Final Data/Forecast_Results/results_regression_randomforest_robustness.csv')
latex_RF_code = df_results_regr_RF.to_latex(index = False)
latex_code_RF_robust = df_results_regr_RF_robust.to_latex(index = False)
with open(r'Figures, Tables & LaTex Code/14 OLS_Lasso_Ridge_ElasticNet_RandomForest.tex', 'w') as file_regr:
    file_regr.write(latex_RF_code)
with open(r'Figures, Tables & LaTex Code/15 OLS_Lasso_Ridge_ElasticNet_RandomForest_Robustness.tex', 'w') as file_regr:
    file_regr.write(latex_code_RF_robust)
with open(r'Figures, Tables & LaTex Code/19 Hyperparameters_RF.tex', 'w') as file_hyperparameters_RF:
    file_hyperparameters_RF.write(str(rf_random.best_params_))

# Neural Network
df_results_regr_RF = read_file(r'Final Data/Forecast_Results/results_regression_randomforest.csv', 'Regression & Random Forest Forecasts')
df_results_regr_RF_robust = read_file(r'Final Data/Forecast_Results/results_regression_randomforest_robustness.csv', 'Regression & Random Forest Forecasts Robustness')
## Hyperparameter Tuning
def make_regression_NN(neuronsFirstLayer = 1, neuronsSecondLayer = 1, neuronsThirdLayer = 1, activation = 'tanh', optimizer = 'Adam'):
    model = Sequential()
    model.add(Dense(units = 11, input_dim = 11, kernel_initializer = 'normal', activation = activation))
    model.add(Dense(units = neuronsFirstLayer, kernel_initializer = 'normal', activation = activation))
    model.add(Dense(units = neuronsSecondLayer, kernel_initializer = 'normal', activation = activation))
    model.add(Dense(units = neuronsThirdLayer, kernel_initializer = 'normal', activation = activation))
    model.add(Dense(units = 1, kernel_initializer = 'normal'))
    model.compile(loss = 'mean_squared_error', optimizer = optimizer)
    return model
def accuracy_score_NN(orig, pred):
    RMSE = np.sqrt(((pred - orig) ** 2).mean())
    return RMSE
NN_grid = {
    'batch_size': [10, 25, 50, 100, 150, 200, 300],
    'epochs': [50, 75, 100, 200, 300, 500, 700],
    'activation': ['linear', 'relu', 'tanh', 'sigmoid'],
    'optimizer': ['SGD', 'RMSprop', 'Adam'],
    'neuronsFirstLayer': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'neuronsSecondLayer': [1, 2, 3, 4, 5, 6, 7, 8],
    'neuronsThirdLayer': [1, 2, 3, 4, 5]
}
NN_grid_validated = {
    'batch_size': [100],
    'epochs': [100],
    'activation': ['tanh'],
    'optimizer': ['Adam'],
    'neuronsFirstLayer': [4],
    'neuronsSecondLayer': [7],
    'neuronsThirdLayer': [5]
}
## Model
y = ['Spread_Secondary']
X = ['EL', 'Volume_log', 'Term', 'Peril_Types', 'Peril_Regions', 'Seasonality_Dummy', 'Trigger_Type_Dummy', 'Rating_Dummy', 'SP500_Quarterly_Return', 'Corp_Credit_Spread', 'Rate_on_Line_Index']
base_model = KerasRegressor(make_regression_NN, verbose = 0)
custom_Scoring = make_scorer(accuracy_score_NN, greater_is_better = False)
NN_grid_search = GridSearchCV(estimator = base_model, param_grid = NN_grid_validated, scoring = custom_Scoring, cv = 5).fit(df_final[X], df_final[y].values.ravel()) 
best_NN = NN_grid_search.best_estimator_
results = {
    'NN': [],
}
measures_NN = []
for IS_y, IS_X, OOS_y, OOS_X in zip(IS_data_y, IS_data_X, OOS_data_y, OOS_data_X):
    measures_NN.append(np.round(np.sqrt(metrics.mean_squared_error(OOS_y, best_NN.predict(OOS_X), squared = True)), 4))
    corr_matrix = np.corrcoef(OOS_y, best_NN.predict(OOS_X))
    corr = corr_matrix[0,1]
    R_sq = corr**2
    measures_NN.append(np.round(R_sq, 4))
measures_NN.append(np.round(np.mean(measures_NN[::2]), 4))
measures_NN.append(np.round(np.mean(measures_NN[1::2]), 4))
measures_NN.append(np.round(np.median(measures_NN[::2]), 4))
measures_NN.append(np.round(np.median(measures_NN[1::2]), 4))
measures_NN.append(np.round(np.std(measures_NN[::2]), 4))
measures_NN.append(np.round(np.std(measures_NN[1::2]), 4))
results['NN'] = measures_NN
results_robust = {
    'NN': [],
}
measures_NN_robust = []
for IS_robust_y, IS_robust_X, OOS_robust_y, OOS_robust_X in zip(IS_data_robust_y, IS_data_robust_X, OOS_data_robust_y, OOS_data_robust_X):
    measures_NN_robust.append(np.round(np.sqrt(metrics.mean_squared_error(OOS_robust_y, best_NN.predict(OOS_robust_X), squared = True)), 4))
    corr_matrix = np.corrcoef(OOS_robust_y, best_NN.predict(OOS_robust_X))
    corr = corr_matrix[0,1]
    R_sq = corr**2
    measures_NN_robust.append(np.round(R_sq, 4))
measures_NN_robust.append(np.round(np.mean(measures_NN_robust[::2]), 4))
measures_NN_robust.append(np.round(np.mean(measures_NN_robust[1::2]), 4))
measures_NN_robust.append(np.round(np.median(measures_NN_robust[::2]), 4))
measures_NN_robust.append(np.round(np.median(measures_NN_robust[1::2]), 4))
measures_NN_robust.append(np.round(np.std(measures_NN_robust[::2]), 4))
measures_NN_robust.append(np.round(np.std(measures_NN_robust[1::2]), 4))
results_robust['NN'] = measures_NN_robust
df_results_NN = pd.DataFrame.from_dict(results)
df_results_NN_robust = pd.DataFrame.from_dict(results_robust)
df_results_NN['IS'] = ['2003-2007', '', '2004-2008', '', '2005-2009', '', '2006-2010', '', '2007-2011', '', '2008-2012', '', '2009-2013', '', '2010-2014', '', '2011-2015', '', '2012-2016', '', '2013-2017', '', '2014-2018', '', '2015-2019', '', 'Mean', '', 'Median', '', 'Std. Dev.', '']
df_results_NN_robust['IS'] = ['2003-2007', '', '2004-2008', '', '2005-2009', '', '2006-2010', '', '2007-2011', '', '2008-2012', '', '2009-2013', '', '2010-2014', '', '2011-2015', '', '2012-2016', '', '2013-2017', '', '2014-2018', '', 'Mean', '', 'Median', '', 'Std. Dev.', '']
df_results_NN['OOS'] = ['2008', '', '2009', '', '2010', '', '2011', '', '2012', '', '2013', '', '2014', '', '2015', '', '2016', '', '2017', '', '2018', '', '2019', '', '2020', '', '', '', '', '', '', '']
df_results_NN_robust['OOS'] = ['2008-2009', '', '2009-2010', '', '2010-2011', '', '2011-2012', '', '2012-2013', '', '2013-2014', '', '2014-2015', '', '2015-2016', '', '2016-2017', '', '2017-2018', '', '2018-2019', '', '2019-2020', '', '', '', '', '', '', '']
df_results_NN['Measure'] = ['RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2']
df_results_NN_robust['Measure'] = ['RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2', 'RMSE', 'R2']
df_results_NN = df_results_NN['NN']
df_results_NN_robust = df_results_NN_robust['NN']
df_results_regr_RF_NN = pd.concat([df_results_regr_RF, df_results_NN], axis = 1)
df_results_regr_RF_NN_robust = pd.concat([df_results_regr_RF_robust, df_results_NN_robust], axis = 1)
print(df_results_regr_RF_NN)
print(df_results_regr_RF_NN_robust)
print('Params NN:', NN_grid_search.best_params_)
df_results_regr_RF_NN.to_csv(r'Final Data/Forecast_Results/results_regression_randomforest_neuralnetwork.csv')
df_results_regr_RF_NN_robust.to_csv(r'Final Data/Forecast_Results/results_regression_randomforest_neuralnetwork_robustness.csv')
latex_code_NN = df_results_regr_RF_NN.to_latex()
latex_code_NN_robust = df_results_regr_RF_NN_robust.to_latex()
with open(r'Figures, Tables & LaTex Code/16 OLS_Lasso_Ridge_ElasticNet_RandomForest_NeuralNetwork.tex', 'w') as file_NN:
    file_NN.write(latex_code_NN)
with open(r'Figures, Tables & LaTex Code/17 OLS_Lasso_Ridge_ElasticNet_RandomForest_NeuralNetwork_Robustness.tex', 'w') as file_NN_robust:
    file_NN_robust.write(latex_code_NN_robust)
with open(r'Figures, Tables & LaTex Code/20 Hyperparameters_NN.tex', 'w') as file_hyperparameters_NN:
    file_hyperparameters_NN.write(str(NN_grid_search.best_params_))

# Hyperparameters
hyperparameters = pd.DataFrame(
    {
        'Model': [
            'Lasso',
            'Ridge',
            'Elastic Net',
            '',
            'RF',
            '',
            '',
            '',
            '',
            '',
            'NN',
            '',
            '', 
            '',
            '',
            ''
        ],
        'Hyperparameter': [
            'Shrinkage parameter λ',
            'Shrinkage parameter λ',
            'Shrinkage parameter λ',
            'Mixing parameter λ1-Ratio',
            'Number of trees N',
            'Max depth of the trees',
            'Number of min samples to split internal node',
            'Number of min samples at leaf Node',
            'Number of Features during choice for best split',
            'Bootstrap samples used when building trees',
            'Batch size',
            'Number of epochs',
            'Activation function',
            'Optimizer function',
            'Number of hidden layers',
            'Number of neurons (1st, 2nd, 3rd layer)'
        ],
        'Search Interval': [
            '[e^-8, ..., e^0] , n = 200',
            '[e^-8, ..., e^0] , n = 200',
            '[e^-8, ..., e^0] , n = 200',
            '[0, ..., 1] , n = 200',
            '[200, ..., 2000] , n = 10',
            '[10, ..., 110] , n = 11',
            '[2, 5, 10]',
            '[1, 2, 4]',
            '[Auto, Sqrt]',
            '[True, False]',
            '[10, ..., 300] , n = 7',
            '[50, ..., 700] , n = 7',
            '[Linear, Relu, Tanh, Sigmoid]',
            '[SGD, RMSprop Adam]',
            '[1, 2, 3]',
            '[1, 11], [1, 11], [1, 11]'
        ],
        'Validated Value': [
            'e^-8',
            '0.00511', 
            '9.3293 * e^-07',
            '0',
            '200',
            '30', 
            '5',
            '2',
            'Sqrt',
            'True',
            '100',
            '100',
            'Tanh',
            'Adam',
            '3',
            '4, 7, 5'
        ]
    }
)
print(hyperparameters)
latex_hyperparameters = hyperparameters.to_latex(index = False)
with open(r'Figures, Tables & LaTex Code/18 Hyperparameters.tex', 'w') as file_hyperparameters:
    file_hyperparameters.write(latex_hyperparameters)

# Aggregated Ratings Overview
ratings_aggregated = pd.DataFrame(
    {
        "Standard & Poor's": [
            'AAA',
            'AA+',
            'AA',
            'AA-',
            'A+',
            'A',
            'A-',
            'BBB+',
            'BBB',
            'BBB-',
            'BB+',
            'BB',
            'BB-',
            'B+',
            'B',
            'B-'            
        ],
        "Moody's": [
            'Aaa',
            'Aa1',
            'Aa2',
            'Aa3',
            'A1',
            'A2',
            'A3',
            'Baa1',
            'Baa2',
            'Baa3',
            'Ba1',
            'Ba2',
            'Ba3',
            'B1',
            'B2',
            'B3'        ],
        'Fitch': [
            'AAA',
            'AA+',
            'AA',
            'AA-',
            'A+',
            'A',
            'A-',
            'BBB+',
            'BBB',
            'BBB-',
            'BB+',
            'BB',
            'BB-',
            'B+',
            'B',
            'B-'
        ],
        'Aggregated Ratings': [
            'AAA',
            'AA',
            'AA',
            'AA',
            'A',
            'A',
            'A',
            'BBB',
            'BBB',
            'BBB',
            'BB',
            'BB',
            'BB',
            'B',
            'B',
            'B'
        ],
    },
    index = ['Investment Grade (IG)', '', '', '', '', '', '', '', '', '', 'Non-Investment Grade (NIG)', '', '', '', '', '']
)
print(ratings_aggregated)
latex_code_ratings_aggregated= ratings_aggregated.to_latex()
with open(r'Figures, Tables & LaTex Code/21 Rating_Aggregated.tex', 'w') as file_ratings_aggregated:
    file_ratings_aggregated.write(latex_code_ratings_aggregated)

# Process End
print('------------------')
print('DATA PROCESSING SUCCESSFULLY DONE.')
print('------------------')