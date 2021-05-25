#############################################################################################
# Author: Niklas Leander Kampe - Bachelor Thesis
# Supervisor: Prof. Dr. Alexander Braun - Institute for Insurance Economics
# Step 2: Cleaning the data sets
#############################################################################################

import pandas as pd
import numpy as np
from datetime import datetime
import os
pd.options.mode.chained_assignment = None

# Functions

def read_file(inputPath, fileName, name):
    df = pd.read_csv(inputPath + fileName, index_col = 0)
    print(name, 'data set successfully imported.')
    return df

def read_mapping_file(path, sheet, index):
    df = pd.read_excel(path, sheet_name = sheet, index_col = index)
    return df

def write_file(df, outputPath, fileName, name):
    df.to_csv(outputPath + fileName)
    print(name, 'data set successfully cleaned and saved.')

def index_setting(df):
    index = range(0, len(df))
    df['Index'] = index
    df.set_index('Index', inplace = True)
    return df

def rounding(df, column):
    df[column] = np.round(np.array(df[column], dtype = np.float), 2)
    return df

def scaling(df, column, factor):
    df[column] = df[column] / factor
    return df

def rounding_scaling(df, column, factor):
    df[column] = round(df[column] / factor, 2)
    return df

def date_transformation(df, columns):
    for column in columns:
        df[column] = pd.to_datetime(df[column])
        df[column] = df[column].dt.strftime('%Y-%m-%d')
    return df

def numeric_transformation(df, numeric_columns, i):
    for numeric_column in numeric_columns:
        df.loc[i, numeric_column] = pd.to_numeric(df.loc[i, numeric_column], errors = 'coerce')
    return df

def standard_mapping(df, mappingFile, idColumn, newColumn, i):
    if pd.isna(df.loc[i, idColumn]) == False:
        df.loc[i, newColumn] = mappingFile.loc[df.loc[i, idColumn], newColumn]
    elif df.loc[i, idColumn] == ' ':
        df.loc[i, newColumn] = np.nan
    else:
        df.loc[i, newColumn] = np.nan
    return df

def static_mapping(df, mappingFile, newColumn, idColumn, i):
    if pd.isna(df.loc[i, idColumn]) == False:
        df.loc[i, newColumn] = mappingFile.loc[df.loc[i, idColumn], newColumn]
    else:
        df.loc[i, newColumn] = np.nan
    return df

def static_mapping_multiple(df, mappingFile, mappingArray, idColumn, i):
    array = mappingArray
    for j in array:
        if pd.isna(df.loc[i, idColumn]) == False:
            df.loc[i, j] = mappingFile.loc[df.loc[i, idColumn], j]
        else:
            df.loc[i, j] = np.nan
    return df

def investment_grade_mapping(df, mappingColumnAggregated, mappingColumnGrade, aggregatedColumn, newGradeColumn, i):
    if df.loc[i, aggregatedColumn] == 'B2':
        df.loc[i, aggregatedColumn] = 'B'
    elif df.loc[i, aggregatedColumn] == 'Ba3':
        df.loc[i, aggregatedColumn] = 'BB-'
    elif df.loc[i, aggregatedColumn] == 'nr':
        df.loc[i, aggregatedColumn] = 'NR'
    # ----
    if pd.isna(df.loc[i, aggregatedColumn]) == False:
        row = ratings_mapping[ratings_mapping[mappingColumnAggregated] == df.loc[i, aggregatedColumn]].index.values[0]
        df.loc[i, newGradeColumn] = ratings_mapping.loc[row, mappingColumnGrade]
    else:
        df.loc[i, newGradeColumn] = np.nan
    return df

def multiple_investment_grade_mapping(df, mappingFile, firstRating, secondRating, thirdRating, gradeMappingColumn, aggregatedMappingColumn, gradeColumn, aggregatedColumn, i):
    if pd.isna(df.loc[i, firstRating]) == False:
        row = mappingFile[mappingFile[firstRating] == df.loc[i, firstRating]].index.values[0]
        df.loc[i, gradeColumn] = mappingFile.loc[row, gradeMappingColumn]
        df.loc[i, aggregatedColumn] = mappingFile.loc[row, aggregatedMappingColumn]
    elif pd.isna(df.loc[i, secondRating]) == False:
        row = mappingFile[mappingFile[secondRating] == df.loc[i, secondRating]].index.values[0]
        df.loc[i, gradeColumn] = mappingFile.loc[row, gradeMappingColumn]
        df.loc[i, aggregatedColumn] = mappingFile.loc[row, aggregatedMappingColumn]
    elif pd.isna(df.loc[i, thirdRating]) == False:
        row = mappingFile[mappingFile[thirdRating] == df.loc[i, thirdRating]].index.values[0]
        df.loc[i, gradeColumn] = mappingFile.loc[row, gradeMappingColumn]
        df.loc[i, aggregatedColumn] = mappingFile.loc[row, aggregatedMappingColumn]
    else: 
        df.loc[i, gradeColumn] = 'NR'
        df.loc[i, aggregatedColumn] = 'NR'
    return df

def rating_grade_dummy_mapping(df, baseColumn, dummyColumn, i):
    if df.loc[i, baseColumn] == 'IG':
        df.loc[i, dummyColumn] = 1
    elif df.loc[i, baseColumn] == 'NIG':
        df.loc[i, dummyColumn] = 0
    elif df.loc[i, baseColumn] == 'NR':
        df.loc[i, dummyColumn] = 0
    else:
        df.loc[i, dummyColumn] = np.nan
    return df

def trigger_type_mapping(df, mappingFile, nameColumn, triggerMappingColumn, triggerColumn, i):
    if pd.isna(df.loc[i, nameColumn]) == False:
        row = mappingFile[mappingFile[nameColumn] == df.loc[i, nameColumn]].index.values[0]
        df.loc[i, triggerColumn] = mappingFile.loc[row, triggerMappingColumn]
    else: 
        df.loc[i, triggerColumn] = np.nan
    return df

def dates_mapping(df, mappingFile, idColumn, issuanceMappingColumn, maturityMappingColumn, issuanceColumn, maturityColumn, i):
    ID = df.loc[i, idColumn]
    if pd.isna(ID) == False:
        issuance_date = mappingFile.loc[ID, issuanceMappingColumn]
        maturity_date = mappingFile.loc[ID, maturityMappingColumn]
        df.loc[i, issuanceColumn] = pd.to_datetime(issuance_date, format = '%Y-%m-%d', errors = 'coerce')
        df.loc[i, maturityColumn] = pd.to_datetime(maturity_date, format = '%Y-%m-%d', errors = 'coerce')
    else:
        df.loc[i, issuanceColumn] = np.nan
        df.loc[i, maturityColumn] = np.nan
    return df

def coupon_mapping(df, mappingFile, idColumn, couponMappingColumn, couponColumn, i):
    ID = df.loc[i, idColumn]
    if pd.isna(ID) == False:
        coupon_rate = mappingFile.loc[ID, couponMappingColumn]
        if pd.isna(coupon_rate) == False:
            df.loc[i, couponColumn] = coupon_rate * 100
        else:
            df.loc[i, couponColumn] = np.nan
    else:
        df.loc[i, couponColumn] = np.nan
    return df

def dummy_mapping(df, typeColumn, regionColumn, triggerColumn, dummyTypeColumn, dummyRegionColumn, dummyTriggerColumn, i):
    if df.loc[i, typeColumn] == 'Multi':
        df.loc[i, dummyTypeColumn] = 1
    else:
        df.loc[i, dummyTypeColumn] = 0
    if df.loc[i, regionColumn] == 'Multi':
        df.loc[i, dummyRegionColumn] = 1
    else:
        df.loc[i, dummyRegionColumn] = 0
    if df.loc[i, triggerColumn] == 'Indemnity':
        df.loc[i, dummyTriggerColumn] = 1
    else:
        df.loc[i, dummyTriggerColumn] = 0
    return df

def advanced_EL_mappig(df, firstELColumn, secondELColumn, i):
    if pd.isna(df.loc[i, firstELColumn]) == False:
        df.loc[i, 'EL'] = df.loc[i, firstELColumn]
    else:
        df.loc[i, 'EL'] = df.loc[i, secondELColumn]
    return df

def rating_adjustment(df, rating_columns, i):
    for rating_column in rating_columns:
        if df.loc[i, rating_column] == 'Unable to resolve all requested identifiers.':
            df.loc[i, rating_column] = np.nan
        elif df.loc[i, rating_column] == 'NR':
            df.loc[i, rating_column] = np.nan
        elif df.loc[i, rating_column] == 'WR':
            df.loc[i, rating_column] = np.nan
        elif df.loc[i, rating_column] == 'WD':
            df.loc[i, rating_column] = np.nan
        elif df.loc[i, rating_column] == 'PIF':
            df.loc[i, rating_column] = np.nan
    return df

def term_calculating(df, issuanceColumn, maturityColumn):
    df['Term'] = round(((pd.to_datetime(df[maturityColumn]) - pd.to_datetime(df[issuanceColumn])).dt.days / 30.416), 2)
    return df

def time_to_maturity_calculating(df, maturityColumn, referenceColumn):
    df['TTM'] = round(((pd.to_datetime(df[maturityColumn]) - pd.to_datetime(df[referenceColumn])).dt.days / 30.416), 2)
    return df

def column_dropping(df, columns):
    df.drop(columns, axis = 1, inplace = True)
    return df

def unique_values(df, column):
    df[column].unique()
    return df

def na_dropping(df, row_column, threshold, condition):
    if row_column == 1:
        n_before = len(df)
        df.dropna(axis = 1, how = condition, inplace = True)
        n_after = len(df)
        print('NA rows dropped: ', n_before - n_after)
    elif row_column == 0:
        n_before = len(df.columns)
        df.dropna(axis = 0, thresh = threshold, inplace = True)
        n_after = len(df.columns)
        print('NA columns dropped: ', n_before - n_after)
    return df

def na_dropping_subset(df, necessaryColumns):
    n_before = len(df)
    df.dropna(subset = necessaryColumns, how = 'any', axis = 0, inplace = True)
    n_after = len(df)
    print('Rows dropped due to missing values: ', n_before - n_after)
    return df

def quarterly_adjustment(df, i):
    if pd.to_datetime(df.loc[i, 'Ref_Date']).is_quarter_end == False:
        if (pd.to_datetime(df.loc[i, 'Ref_Date']) + pd.to_timedelta(1, unit = 'd')).is_quarter_end == False:
            if (pd.to_datetime(df.loc[i, 'Ref_Date']) + pd.to_timedelta(2, unit = 'd')).is_quarter_end == False:
                df.drop([i], inplace = True)
    return df

def sorting(df):
    df.sort_values(by = ['Name', 'Ref_Date'], inplace = True)
    return df

def testing(df):
    print(df.head(n = 10))

def file_merging(inputPath, fileName, name):
    df_merged = []
    for i in range(1, len(os.listdir(inputPath))):
        df = pd.read_csv(inputPath + fileName + str(i) + '.csv', index_col = 0)
        df['Ref_Date'] = df.iloc[0,22]
        df.drop([0], inplace = True)
        df.dropna(axis = 1, how = 'all', inplace = True)
        df.dropna(axis = 0, thresh = 1, inplace = True)
        df.rename(columns = {'0': 'Peril_Old', '2': 'Name', '3': 'ID', '5': 'Bloomberg_Ticker', '7': 'Volume', '8': 'Issuance_Date', '9': 'Maturity_Date', '11': 'Regions/Perils', '12': 'Long-Term_AP', '13': 'Long-Term_EL', '14': 'Near-Term_AP', '15': 'Near-Term_EL', '17': 'Rating_S&P', '18': 'Rating_Moodys', '19': 'Rating_Fitch', '20': 'Spread_Secondary', '21': 'Spread_Bid', '22': 'Spread_Ask', '23': 'Price_Bid', '24': 'Price_Ask', '25': 'Coverage_Type'}, inplace = True)
        df['Peril'] = df['Peril_Old']
        df['Peril'].fillna(method = 'ffill', inplace = True)
        df.drop(['Peril_Old'], axis = 1, inplace = True)
        df.drop([1,2,3,4], inplace = True)
        df = df[df.isnull().sum(axis = 1) < 20]
        df_merged.append(df)
        print('AON Data Set ' + str(i) + ' successfully processed.')
    df_merged = pd.concat(df_merged)
    print(name, 'data set successfully merged')
    return df_merged

def column_renaming(df, names):
    df.rename(columns = names, inplace = True)
    return df

# -----------------------------------------------------------------------------------

# Process Start
print('------------------')
print('DATA CLEANING SUCCESSFULLY INITIATED.')
print('------------------')

# Mapping files
## Global
ratings_mapping = read_mapping_file(r'Mapping Data/ratings_mapping_global.xlsx', 'ratings', None)
## AON
ISIN_mapping_AON = read_mapping_file(r'Mapping Data/mapping_AON.xlsx', 'ISIN_mapping_STATIC', 0)
perils_mapping_AON = read_mapping_file(r'Mapping Data/mapping_AON.xlsx', 'perils_mapping', 0)
triggers_mapping_AON = read_mapping_file(r'Mapping Data/mapping_AON.xlsx', 'triggers_mapping', None)
ratings_mapping_AON = read_mapping_file(r'Mapping Data/mapping_AON.xlsx', 'ratings_mapping', 0)
spreads_mapping_AON = read_mapping_file(r'Mapping Data/mapping_spreads_global.xlsx', 'spreads_AON_STATIC', 0)
prices_mapping_AON = read_mapping_file(r'Mapping Data/mapping_spreads_global.xlsx', 'prices_AON_STATIC', 0)
## Swiss Re
mapping_SwissRe = read_mapping_file(r'Mapping Data/mapping_SwissRe.xlsx', 'mapping_STATIC', 0)
perils_mapping_SwissRe = read_mapping_file(r'Mapping Data/mapping_SwissRe.xlsx', 'perils_mapping', 0)
triggers_mapping_SwissRe = read_mapping_file(r'Mapping Data/mapping_SwissRe.xlsx', 'triggers_mapping', 0)
ratings_mapping_SwissRe = read_mapping_file(r'Mapping Data/mapping_SwissRe.xlsx', 'ratings_mapping', 0)
spreads_mapping_SwissRe = read_mapping_file(r'Mapping Data/mapping_spreads_global.xlsx', 'spreads_SwissRe_STATIC', 0)
prices_mapping_SwissRe = read_mapping_file(r'Mapping Data/mapping_spreads_global.xlsx', 'prices_SwissRe_STATIC', 0)

# -----------------------------------------------------------------------------------

# AON
name_AON = 'AON'
inputPath_AON = r'Working Data/AON_imported/'
outputPath_AON = r'Working Data/AON_cleaned/'
## Cleaning
df_AON_merged = file_merging(inputPath_AON, 'df_AON_', name_AON)
column_dropping(df_AON_merged, ['10','32','33','16','6','4'])
write_file(df_AON_merged, outputPath_AON, 'df_AON_raw.csv', name_AON)
term_calculating(df_AON_merged, 'Issuance_Date', 'Maturity_Date')
time_to_maturity_calculating(df_AON_merged, 'Maturity_Date', 'Ref_Date')
index_setting(df_AON_merged)
numeric_columns = ['Volume', 'EL', 'Spread_Secondary', 'Spread_Bid', 'Spread_Ask', 'Price_Bid', 'Price_Ask']
perils = ['NA_EQ', 'NA_Hurricane', 'NA_Winterstorm', 'NA_Windstorm', 'JP_EQ', 'JP_Hurricane', 'JP_Winterstorm', 'JP_Windstorm', 'EU_EQ', 'EU_Winterstorm', 'EU_Windstorm', 'AUS_EQ', 'AUS_Hurricane', 'LA_EQ', 'LA_Hurricane']
for i in range(0, len(df_AON_merged)):
    standard_mapping(df_AON_merged, ISIN_mapping_AON, 'ID', 'ISIN', i)
    advanced_EL_mappig(df_AON_merged, 'Near-Term_EL', 'Long-Term_EL', i)
    numeric_transformation(df_AON_merged, numeric_columns, i)
    static_mapping(df_AON_merged, perils_mapping_AON, 'Peril_Type', 'Name', i)
    static_mapping(df_AON_merged, perils_mapping_AON, 'Peril_Types', 'Name', i)
    static_mapping(df_AON_merged, perils_mapping_AON, 'Peril_Region', 'Name', i)
    static_mapping(df_AON_merged, perils_mapping_AON, 'Peril_Regions', 'Name', i)
    static_mapping_multiple(df_AON_merged, perils_mapping_AON, perils, 'Name', i)
    static_mapping(df_AON_merged, ratings_mapping_AON, 'Rating', 'Name', i)
    static_mapping(df_AON_merged, ratings_mapping_AON, 'Rating_Dummy', 'Name', i)
    static_mapping(df_AON_merged, ratings_mapping_AON, 'Rating_Grade', 'Name', i)
    static_mapping(df_AON_merged, ratings_mapping_AON, 'Rating_Grade_Dummy', 'Name', i)
    trigger_type_mapping(df_AON_merged, triggers_mapping_AON, 'Name', 'Trigger', 'Trigger_Type', i)
    dummy_mapping(df_AON_merged, 'Peril_Type', 'Peril_Region', 'Trigger_Type', 'Peril_Type_Dummy', 'Peril_Region_Dummy', 'Trigger_Type_Dummy', i)
    standard_mapping(df_AON_merged, spreads_mapping_AON, 'ISIN', 'Spread_Primary', i)
    standard_mapping(df_AON_merged, prices_mapping_AON, 'ISIN', 'Price_Primary', i)
    quarterly_adjustment(df_AON_merged, i)
df_AON_merged['Price_Secondary'] = (df_AON_merged['Price_Bid'] + df_AON_merged['Price_Ask']) * 0.5
scaling(df_AON_merged, 'EL', 0.01)
date_transformation(df_AON_merged, ['Issuance_Date', 'Maturity_Date', 'Ref_Date'])
columns = ['ISIN', 'Name', 'Issuance_Date', 'Maturity_Date', 'Term', 'TTM', 'Volume', 'Peril_Type', 'Peril_Types', 'Peril_Type_Dummy', 'Peril_Region', 'Peril_Regions', 'Peril_Region_Dummy', 'NA_EQ', 'NA_Hurricane', 'NA_Winterstorm', 'NA_Windstorm', 'JP_EQ', 'JP_Hurricane', 'JP_Winterstorm', 'JP_Windstorm', 'EU_EQ', 'EU_Winterstorm', 'EU_Windstorm', 'AUS_EQ', 'AUS_Hurricane', 'LA_EQ', 'LA_Hurricane', 'Trigger_Type', 'Trigger_Type_Dummy', 'Rating', 'Rating_Dummy', 'Rating_Grade', 'Rating_Grade_Dummy', 'EL', 'Spread_Primary', 'Spread_Secondary', 'Price_Primary', 'Price_Secondary', 'Ref_Date']
df_AON_merged_cleaned = df_AON_merged[columns]
na_dropping_subset(df_AON_merged_cleaned, ['Term', 'TTM', 'Volume', 'Peril_Type', 'Peril_Types', 'Peril_Region', 'Peril_Regions', 'Trigger_Type', 'Rating', 'EL', 'Spread_Primary', 'Spread_Secondary', 'Ref_Date'])
sorting(df_AON_merged_cleaned)
index_setting(df_AON_merged_cleaned)
write_file(df_AON_merged_cleaned, outputPath_AON, 'df_AON_cleaned.csv', name_AON)

# Swiss Re
name_SwissRe = 'Swiss Re'
inputPath_SwissRe = r'Working Data/SwissRe_imported/'
outputPath_SwissRe = r'Working Data/SwissRe_cleaned/'
## Cleaning
df_SwissRe = read_file(inputPath_SwissRe, 'df_SwissRe.csv', name_SwissRe)
column_renaming(df_SwissRe, {'YEAR': 'Year', 'DATE': 'Ref_Date', 'BID_PRC': 'Price_Bid', 'ASK_PRC': 'Price_Ask', 'BID_SPREAD': 'Spread_Bid', 'ASK_SPREAD': 'Spread_Ask', 'DEAL': 'Name', 'CUSIP': 'ID', 'Expected Loss  (bps)': 'EL', 'STATED SPREAD (bps)': 'Spread_Secondary', 'TRIGGER': 'Trigger_Type', 'RISK': 'Regions/Perils', 'ORIG_PRINCIPAL': 'Volume', 'OS_PRINCIPAL': 'OS_Volume', 'RATING_SP': 'Rating_S&P', 'RATING_MOODYS': 'Rating_Moodys', 'RATING_FITCH': 'Rating_Fitch'})
column_dropping(df_SwissRe, ['OS_Volume'])
index_setting(df_SwissRe)
scaling(df_SwissRe, 'Volume', 1000000)
necessary_columns = ['Volume', 'EL', 'Spread_Secondary']
na_dropping_subset(df_SwissRe, necessary_columns)
index_setting(df_SwissRe)
rating_columns_SwissRe = ['Rating_S&P', 'Rating_Moodys', 'Rating_Fitch']
perils = ['NA_EQ', 'NA_Hurricane', 'NA_Winterstorm', 'NA_Windstorm', 'JP_EQ', 'JP_Hurricane', 'JP_Winterstorm', 'JP_Windstorm', 'EU_EQ', 'EU_Winterstorm', 'EU_Windstorm', 'AUS_EQ', 'AUS_Hurricane', 'LA_EQ', 'LA_Hurricane']
for i in range(0, len(df_SwissRe)):
    standard_mapping(df_SwissRe, mapping_SwissRe, 'ID', 'ISIN', i)
    standard_mapping(df_SwissRe, triggers_mapping_SwissRe, 'Name', 'Trigger_Type', i)
    static_mapping(df_SwissRe, perils_mapping_SwissRe, 'Peril_Type', 'Name', i)
    static_mapping(df_SwissRe, perils_mapping_SwissRe, 'Peril_Types', 'Name', i)
    static_mapping(df_SwissRe, perils_mapping_SwissRe, 'Peril_Region', 'Name', i)
    static_mapping(df_SwissRe, perils_mapping_SwissRe, 'Peril_Regions', 'Name', i)
    static_mapping_multiple(df_SwissRe, perils_mapping_SwissRe, perils, 'Name', i)
    static_mapping(df_SwissRe, ratings_mapping_SwissRe, 'Rating', 'Name', i)
    static_mapping(df_SwissRe, ratings_mapping_SwissRe, 'Rating_Dummy', 'Name', i)
    static_mapping(df_SwissRe, ratings_mapping_SwissRe, 'Rating_Grade', 'Name', i)
    static_mapping(df_SwissRe, ratings_mapping_SwissRe, 'Rating_Grade_Dummy', 'Name', i)
    dates_mapping(df_SwissRe, mapping_SwissRe, 'ID', 'Issuance_Date', 'Maturity_Date', 'Issuance_Date', 'Maturity_Date', i)
    dummy_mapping(df_SwissRe, 'Peril_Type', 'Peril_Region', 'Trigger_Type', 'Peril_Type_Dummy', 'Peril_Region_Dummy', 'Trigger_Type_Dummy', i)
    standard_mapping(df_SwissRe, spreads_mapping_SwissRe, 'ISIN', 'Spread_Primary', i)
    standard_mapping(df_SwissRe, prices_mapping_SwissRe, 'ISIN', 'Price_Primary', i)
    quarterly_adjustment(df_SwissRe, i)
term_calculating(df_SwissRe, 'Issuance_Date', 'Maturity_Date')
time_to_maturity_calculating(df_SwissRe, 'Maturity_Date', 'Ref_Date')
column_dropping(df_SwissRe, ['Regions/Perils'])
pd.to_numeric(df_SwissRe['Price_Bid'])
pd.to_numeric(df_SwissRe['Price_Ask'])
df_SwissRe['Price_Secondary'] = (df_SwissRe['Price_Bid'] + df_SwissRe['Price_Ask']) * 0.5
rounding(df_SwissRe, 'Volume')
rounding(df_SwissRe, 'Price_Secondary')
columns = ['ISIN', 'Name', 'Issuance_Date', 'Maturity_Date', 'Term', 'TTM', 'Volume', 'Peril_Type', 'Peril_Types', 'Peril_Type_Dummy', 'Peril_Region', 'Peril_Regions', 'Peril_Region_Dummy', 'NA_EQ', 'NA_Hurricane', 'NA_Winterstorm', 'NA_Windstorm', 'JP_EQ', 'JP_Hurricane', 'JP_Winterstorm', 'JP_Windstorm', 'EU_EQ', 'EU_Winterstorm', 'EU_Windstorm', 'AUS_EQ', 'AUS_Hurricane', 'LA_EQ', 'LA_Hurricane', 'Trigger_Type', 'Trigger_Type_Dummy', 'Rating', 'Rating_Dummy', 'Rating_Grade', 'Rating_Grade_Dummy', 'EL', 'Spread_Primary', 'Spread_Secondary', 'Price_Primary', 'Price_Secondary', 'Ref_Date']
df_SwissRe = df_SwissRe[columns]
write_file(df_SwissRe, outputPath_SwissRe, 'df_SwissRe_raw.csv', name_SwissRe)
na_dropping_subset(df_SwissRe, ['Term', 'TTM', 'Volume', 'Peril_Type', 'Peril_Types', 'Peril_Region', 'Peril_Regions', 'Trigger_Type', 'Rating', 'EL', 'Spread_Primary', 'Spread_Secondary', 'Ref_Date'])
sorting(df_SwissRe)
index_setting(df_SwissRe)
write_file(df_SwissRe, outputPath_SwissRe, 'df_SwissRe_cleaned.csv', name_SwissRe)

# Lane Financial
name_LaneFinancial = 'Lane Financial'
inputPath_LaneFinancial = r'Working Data/LaneFinancial_imported/'
outputPath_LaneFinancial = r'Working Data/LaneFinancial_cleaned/'
## Cleaning
df_LaneFinancial_cleaned = read_file(inputPath_LaneFinancial, 'df_LaneFinancial.csv', name_LaneFinancial)
index_setting(df_LaneFinancial_cleaned)
df_LaneFinancial_cleaned.columns = df_LaneFinancial_cleaned.iloc[0]
df_LaneFinancial_cleaned.drop(labels = 0, axis = 0, inplace = True)
index_setting(df_LaneFinancial_cleaned)
write_file(df_LaneFinancial_cleaned, outputPath_LaneFinancial, 'df_LaneFinancial_cleaned.csv', name_LaneFinancial)

# S&P 500
name_SP500 = 'S&P 500'
inputPath_SP500 = r'Working Data/S&P500_imported/'
outputPath_SP500 = r'Working Data/S&P500_cleaned/'
## Cleaning
df_SP500 = read_file(inputPath_SP500, 'df_S&P500.csv', name_SP500)
df_SP500_cleaned = df_SP500[['Date', 'SP500_Quarterly_Return']]
write_file(df_SP500_cleaned, outputPath_SP500, 'df_S&P500_cleaned.csv', name_SP500)

# Rate-on-Line Index
name_RoL = 'Rate-on-Line Index'
inputPath_RoL = r'Working Data/RoL_imported/'
outputPath_RoL = r'Working Data/RoL_cleaned/'
## Cleaning
df_RoL = read_file(inputPath_RoL, 'df_RoL.csv', name_RoL)
df_RoL_cleaned = df_RoL[['Year', 'Rate_on_Line_Index', 'Rate_on_Line_Index_Change']]
write_file(df_RoL_cleaned, outputPath_RoL, 'df_RoL_cleaned.csv', name_RoL)

# Credit Spreads
name_CreditSpreads = 'US Corporate Credit Spreads'
inputPath_CreditSpreads = r'Working Data/CreditSpreads_imported/'
outputPath_CreditSpreads = r'Working Data/CreditSpreads_cleaned/'
## Cleaning
df_CreditSpreads = read_file(inputPath_CreditSpreads, 'df_CreditSpreads.csv', name_CreditSpreads)
write_file(df_CreditSpreads, outputPath_CreditSpreads, 'df_CreditSpreads_cleaned.csv', name_CreditSpreads)

# Seasonalities
name_Seasonalities = 'Peril Seasonalities'
inputPath_Seasonalities = r'Working Data/Seasonalities_imported/'
outputPath_Seasonalities = r'Working Data/Seasonalities_cleaned/'
## Cleaning
df_Seasonalities = read_file(inputPath_Seasonalities, 'df_Seasonalities.csv', name_Seasonalities)
write_file(df_Seasonalities, outputPath_Seasonalities, 'df_Seasonalities_cleaned.csv', name_Seasonalities)

# Cat Bond Losses & Defaults
name_CatBondLosses = 'Cat Bond Losses & Defaults'
inputPath_CatBondLosses = r'Working Data/CatBondLosses_imported/'
outputPath_CatBondLosses = r'Working Data/CatBondLosses_cleaned/'
## Cleaning
df_CatBondLosses = read_file(inputPath_CatBondLosses, 'df_CatBondLosses.csv', name_CatBondLosses)
write_file(df_CatBondLosses, outputPath_CatBondLosses, 'df_CatBondLosses_cleaned.csv', name_CatBondLosses)

# Process End
print('------------------')
print('DATA CLEANING SUCCESSFULLY DONE')
print('------------------')