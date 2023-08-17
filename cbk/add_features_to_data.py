#!/usr/bin/env python
# coding: utf-8


#importer libraries
from pathlib import Path
import pandas as pd
import numpy as np

'''
Defines a function, add_features_to_data(df) that adds the collected features
to the dataset, merged on muni_code and year.
Args: df
returns:
    df with added features

'''

def add_features_to_data(df):
    fp = Path("../cbk/")
    bolig = fp/"fittest.csv"
    indk = fp/"indkp101.csv"
    konth = fp/"kontanth.csv"
    areas = fp/"muni_areas.csv"
    pop = fp/"population_data.csv"
    pop_dens = fp/"pop_dens.csv"

    lars_fp = Path("../lars/")
    gini = lars_fp/"gini_index.csv"
        
    indk = pd.read_csv(indk)
    konth = pd.read_csv(konth)
    gini = pd.read_csv(gini)
    areas = pd.read_csv(areas)
    pop = pd.read_csv(pop)
    pop_dens = pd.read_csv(pop_dens)
    
    df = df\
        .merge(indk, on=["muni_code", "year"], how = 'left',suffixes=('_left', '_right'))\
        .merge(konth, on= ["muni_code", "year"], how= 'left',suffixes=('_left', '_right'))\
        .merge(gini, on = ["muni_code", "year"], how = 'left',suffixes=('_left', '_right'))\
        .merge(pop_dens, on = ["muni_code", "year"], how = 'left',suffixes=('_left', '_right'))\
        .sort_values(["year", "count"])\
        .dropna()\
        .assign(muni_code=lambda x: x['muni_code'].astype('category'))\
        .assign(year=lambda x: x['year'].astype('category'))\
        .assign(housing_type = lambda x: x["housing_type"].astype('category'))

    df['avg_sqm_price'] = pd.to_numeric(df['avg_sqm_price'], errors='coerce')

    #drops very useless columns
    cols_to_drop = [col for col in df.columns if col.startswith('Unnamed')]
    df.drop(columns=cols_to_drop, inplace=True)
    df.drop(columns="count", inplace =True)

    return (df)