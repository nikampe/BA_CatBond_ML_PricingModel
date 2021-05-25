#############################################################################################
# Author: Niklas Leander Kampe - Bachelor Thesis
# Supervisor: Prof. Dr. Alexander Braun - Institute for Insurance Economics
# Step 1: Importing & inspecting the data set
#############################################################################################

import pandas as pd
import numpy as np
import os

def read_file(inputPath, sheet, headerColumn, name):
    df = pd.read_excel(inputPath, sheet_name = sheet, header = headerColumn)
    print(name, 'data set succesfully imported.')
    return df

def read_multiple_files(files, inputPath, fileName, outputPath, name):
    for index, file in enumerate(files, start = 1):
        df = pd.read_excel(inputPath + file, header = None)
        df.to_csv(outputPath + fileName + str(index) + '.csv')
        print(file + " successfully imported and saved as CSV.")
    print('All', name, 'data sets successfully imported and saved as CSV.')

def read_file_structure (inputPath):
    files = os.listdir(inputPath)
    files.sort()
    return files

def write_csv(df, outputPath, name):
    df.to_csv(outputPath)
    print(name, 'data set successfully saved as CSV.')

# 1: Import

# Process Start
print('------------------')
print('DATA IMPORT SUCCESSFULLY INITIATED.')
print('------------------')

# AON
name_AON = 'AON'
inputPath_AON = r'Raw Data/AON - Secondary Cat Bond Data/'
outputPath_AON = r'Working Data/AON_imported/'
## Importing
files = read_file_structure(inputPath_AON)
read_multiple_files(files, inputPath_AON, 'df_AON_', outputPath_AON, name_AON)

# Lane Financial
name_LaneFinancial = 'Lane Financial'
inputPath_LaneFinancial = r'Raw Data/Lane Financial - Secondary Cat Bond Data.xlsx'
outputPath_LaneFinancial = r'Working Data/LaneFinancial_imported/df_LaneFinancial.csv'
# Importing
df_LaneFinancial= read_file(inputPath_LaneFinancial, 'All Cat ILS', 0, name_LaneFinancial)
write_csv(df_LaneFinancial, outputPath_LaneFinancial, name_LaneFinancial)

# Swiss Re
name_SwissRe = 'Swiss Re'
inputPath_SwissRe = r'Raw Data/SwissRe - Secondary Cat Bond Data.xlsx'
outputPath_SwissRe = r'Working Data/SwissRe_imported/df_SwissRe.csv'
# Importing
df_SwissRe = read_file(inputPath_SwissRe, 'hist_prc_mst_STATIC', 0, name_SwissRe)
write_csv(df_SwissRe, outputPath_SwissRe, name_SwissRe)

# S&P 500
name_SP500 = 'S&P 500'
inputPath_SP500 = r'Raw Data/S&P 500 - Quarterly Returns.xlsx'
outputPath_SP500 = r'Working Data/S&P500_imported/df_S&P500.csv'
# Importing
df_SP500 = read_file(inputPath_SP500, 'Quarterly Returns', 0, name_SP500)
write_csv(df_SP500, outputPath_SP500, name_SP500)

# Rate-on-Line Index
name_RoL = 'Rate-on-Line Index'
inputPath_RoL = r'Raw Data/Guy Carpenter - Rate-on-Line Index.xlsx'
outputPath_RoL = r'Working Data/RoL_imported/df_RoL.csv'
# Importing
df_RoL = read_file(inputPath_RoL, 'Rate-on-Line Index', 0, name_RoL)
write_csv(df_RoL, outputPath_RoL, name_RoL)

# Corporate Credit Spreads
name_CreditSpreads = 'US Corporate Credit Spreads'
inputPath_CreditSpreads = r'Raw Data/BofA Merrill Lynch - US Corporate Credit Spreads.xlsx'
outputPath_CreditSpreads = r'Working Data/CreditSpreads_imported/df_CreditSpreads.csv'
# Importing
df_CreditSpreads = read_file(inputPath_CreditSpreads, 'Credit_Spreads', 0, name_CreditSpreads)
write_csv(df_CreditSpreads, outputPath_CreditSpreads, name_CreditSpreads)

# Seasonalities
name_Seasonalities = 'Peril Seasonalities'
inputPath_Seasonalities = r'Raw Data/Peril Seasonalities.xlsx'
outputPath_Seasonalities = r'Working Data/Seasonalities_imported/df_Seasonalities.csv'
# Importing
df_Seasonalities = read_file(inputPath_Seasonalities, 'seasonalities', 0, name_Seasonalities)
write_csv(df_Seasonalities, outputPath_Seasonalities, name_Seasonalities)

# Cat Bond Losses & Defaults
name_CatBondLosses = 'Cat Bond Losses & Defaults'
inputPath_CatBondLosses = r'Raw Data/Cat Bond Losses & Defaults.xlsx'
outputPath_CatBondLosses = r'Working Data/CatBondLosses_imported/df_CatBondLosses.csv'
# Importing
df_CatBondLosses = read_file(inputPath_CatBondLosses, 'losses_defaults', 0, name_CatBondLosses)
write_csv(df_CatBondLosses, outputPath_CatBondLosses, name_CatBondLosses)

# Process End
print('------------------')
print('DATA IMPORT SUCCESSFULLY DONE')
print('------------------')