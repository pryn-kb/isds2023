#!/usr/bin/env python
# coding: utf-8

'''
Extracts number of persons receiving "kontanthjælp" by municipality and year.
Data is split in the two tables "KY16" and "KONT1X" from Statistics Denmark.
They contain data from 2007 to 2023 and 1994 to 2006 respectively.

This script returns one csv-file, "kontanth.csv" containing three columns:
    muni_code, Int64, municipal code consistent with other municiapal codes from Statistics Denmark
    year, Int64, the year
    kont_recip_tot, Int64, total number of people recieving "kontanthjælp"
'''

# importing pandas
import pandas as pd   

# urls
KY034 = "https://api.statbank.dk/v1/data/KY034/CSV?valuePresentation=CodeAndValue&TAL=1%2C2&OMR%C3%85DE=*&Tid=*"
KONT1X = "https://api.statbank.dk/v1/data/KONT1X/CSV?valuePresentation=CodeAndValue&OMR%C3%85DE=*&YDELSESART=TOT&Tid=*"

# Retrieving data
KY034_data = pd.read_csv(KY034, sep = ";")
KONT1X_data = pd.read_csv(KONT1X, sep = ";")    

# Helperfunction for extracting municipal codes
def clean_ds_data(df):
    df['muni_code'] = df['OMRÅDE'].str.extract(r'(\d{3})')   # extracting municipality code
    df['muni_name'] = df['OMRÅDE'].str.extract(r'(\d{3}\s+(.*))')[1] # extracting municipalit name
    df['year'] = df['TID'].str.split().str[0]
    df = df        .drop(columns=["OMRÅDE", 'TID'])
    return df



# cleaning KONT1X data. Only looking at data for january. Remember to remove november!
KONT1X_data = clean_ds_data(KONT1X_data)
KONT1X_data = KONT1X_data[KONT1X_data['year'].str.endswith('01')].copy()
KONT1X_data['year'] = KONT1X_data['year'].str.replace('M01', "")


# Reshaping kont1x data
KONT1X_data = KONT1X_data.pivot(index=["muni_code", "year"], columns = "YDELSESART", values = "INDHOLD")
KONT1X_data.name = None
KONT1X_data = KONT1X_data.reset_index()

# reshaping KY034 data
KY034_data = KY034_data.pivot(index=["OMRÅDE", "TID"], columns = "TAL", values = "INDHOLD").reset_index()
KY034_data = clean_ds_data(KY034_data)


# selecting and renaming columns.
KY034_data = KY034_data[["muni_code", "year", "1 Berørte personer (antal)"]].rename(columns={"1 Berørte personer (antal)":"kont_recip_tot"})
KONT1X_data = KONT1X_data[["muni_code", "year", "TOT Modtagere af kontanthjælp mv. i alt"]].rename(columns = {"TOT Modtagere af kontanthjælp mv. i alt":"kont_recip_tot"})

# coercing muni_code and year to integers
KY034_data['muni_code'] = KY034_data['muni_code'].astype('Int64')
KONT1X_data['muni_code'] = KONT1X_data['muni_code'].astype('Int64')

KY034_data['year'] = KY034_data['year'].astype('Int64')
KONT1X_data['year'] = KONT1X_data['year'].astype('Int64')

# KY034_data originally contains data on "landsdele". They appear as NaN in our data. Get rid of those!
KY034_data = KY034_data.dropna(subset=['muni_code']).info()


#Concatenating the data frames
total = pd.concat([KY034_data, KONT1X_data])


# writing to file
total.to_csv("kontanth.csv")