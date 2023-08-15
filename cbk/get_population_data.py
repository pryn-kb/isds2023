#!/usr/bin/env python
# coding: utf-8

'''
Henter befolkningstal for alle områder i danmark
'''

import requests
import pandas as pd

# Henter befolkningstal for alle kommuner

# FOLK1A har data fra primo 2008 til dato
FOLK1A = 'https://api.statbank.dk/v1/data/FOLK1A/CSV?valuePresentation=CodeAndValue&OMR%C3%85DE=*&K%C3%98N=TOT&ALDER=IALT&Tid=*'
data = pd.read_csv(FOLK1A, sep = ";")





data['Tal'] = data['OMRÅDE'].str.extract(r'(\d{3})')

# Udtræk tekst
data['lokation'] = data['OMRÅDE'].str.extract(r'(\d{3}\s+(.*))')[1]


data

