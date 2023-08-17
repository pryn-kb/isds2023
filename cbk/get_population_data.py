#!/usr/bin/env python
# coding: utf-8

'''
Retrieves population data from Statistics Denmark.
In 2007 a restructuring of municipalites took places. Some municipalities were unchanged, others 
established as mergers of existing municipalities. 
For this reason population data is provided in three different tables:
FOLK1A: 2008ff
BEF1A07: 2005 to 2009
BEF1A: 1979 to 2006

The most recent data contains population data for each quarter. To get consistent data, only the 1st quarter
from that dataset is extracted

Data on municipalities from before the restructuring are consolidated into the present time municipalities,
based on the concordance build in "nye_og_gamle_kommuner.csv", and the result stored as population_data.csv,
with a municipal code ("muni_code"), year and population

'''

# importing libraries
import requests
import pandas as pd

# Retrieves population data from all municipalities

## Defining calls to Statistic Denmark API
# 2008 to date
FOLK1A = 'https://api.statbank.dk/v1/data/FOLK1A/CSV?valuePresentation=CodeAndValue&OMR%C3%85DE=*&Tid=*'

# 2005 to 2009
BEF1A07 = "https://api.statbank.dk/v1/data/BEF1A07/CSV?valuePresentation=CodeAndValue&OMR%C3%85DE=*&Tid=*"

# 1979 to 2006
BEF1A = "https://api.statbank.dk/v1/data/BEF1A/CSV?valuePresentation=CodeAndValue&OMR%C3%85DE=*&Tid=*"

# Retrieving data
FOLK1A_data = pd.read_csv(FOLK1A, sep = ";")
BEF1A07_data = pd.read_csv(BEF1A07, sep = ";")
BEF1A_data = pd.read_csv(BEF1A, sep = ";")



# helper function for cleaning the data

def clean_pop_data(df):
    df['muni_code'] = df['OMRÅDE'].str.extract(r'(\d{3})')   # extracting municipality code
    df['muni_name'] = df['OMRÅDE'].str.extract(r'(\d{3}\s+(.*))')[1] # extracting municipalit name
    df['year'] = df['TID'].str.split().str[0]
    df = df        .drop(columns=["OMRÅDE", 'TID'])        .rename(columns={'INDHOLD':'pop'})
    return df

FOLK1A_data = clean_pop_data(FOLK1A_data)
BEF1A_data = clean_pop_data(BEF1A_data)
BEF1A07_data = clean_pop_data(BEF1A07_data)



FOLK1A_data["muni_code"] = FOLK1A_data["muni_code"].astype("Int64")
BEF1A_data["muni_code"] = BEF1A_data["muni_code"].astype("Int64")
BEF1A07_data["muni_code"] = BEF1A07_data["muni_code"].astype("Int64")


# additional cleaning of FOLK1A data
FOLK1A_data = FOLK1A_data[FOLK1A_data['year'].str.endswith('1')]
FOLK1A_data['year'] = FOLK1A_data['year'].str.replace('K1', "")


#The two newest datasets have an overlap, but consistent minicipality codes. They are concatenated, and 
# duplicates are dropped
pop_data = pd.concat([FOLK1A_data, BEF1A07_data])\
    .reset_index(drop = True)\
    .drop_duplicates()

# reading descriptoin of mapping between new and old municiplaties

konkordans = pd.read_csv("../nye_og_gamle_kommuner.csv")

#making sure we have consistent datatypes
konkordans['old_muni_code'] = konkordans['old_muni_code'].astype('Int64')
konkordans['muni_code'] = konkordans['muni_code'].astype('Int64')
BEF1A_data['muni_code'] = BEF1A_data['muni_code'].astype('Int64')



nye = pop_data[["muni_code", 'year', "pop"]]

# merging old municipalities to new, and aggregating population data
gamle = BEF1A_data\
    .merge(konkordans, how='left', left_on = 'muni_code', right_on = 'old_muni_code')\
    .groupby(["muni_code_x", "year"])["pop"].agg("sum")\
    .reset_index()\
    .rename(columns={'muni_code_x':'muni_code'})

gamle["muni_code"] = gamle["muni_code"].astype('Int64')


# concatenating new and old data
totalen = pd.concat([nye, gamle])

# saving to csv:
totalen.to_csv("population_data.csv", index=False)