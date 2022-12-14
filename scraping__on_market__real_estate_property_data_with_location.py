# -*- coding: utf-8 -*-
"""Scraping "On Market" Real Estate Property Data with Location.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZFSmAcVOMTlZ7r3lDGjtch5MZJ2_YgSx
"""

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
!pip install pygeocodio
from geocodio import GeocodioClient
import seaborn as sns
from google.colab import files
import matplotlib.pyplot as plt
import numpy as np
client = GeocodioClient('45166450555546465dff2463236dd666f3624f6')
#fd28e66d87e866672564f347d2666dd4f422d2e
#8d8d64d6a8a21e6f66e6126dea6ad64a4e220ad

files.upload()

file_name='Charlotte, FL'
file = file_name+'.xlsx'
df = pd.read_excel(file)

df

df['Link']

def remove_sign(x,sign):
    if type(x) is str:
        x = float(x.replace(sign,'').replace(',',''))
    return x

def remove_outlier_IQR(df):
    Q1=df.quantile(0.25)
    Q3=df.quantile(0.75)
    IQR=Q3-Q1
    df_final=df[~((df<(Q1-1.5*IQR)) | (df>(Q3+1.5*IQR)))]
    return df_final

def landwatch_grab(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        data = [soup.find('div', class_ ="_260f0").text,
              soup.find('a', class_="a73d7 _477fe").text,
              soup.find('div', class_="_477fe").text,
              soup.find('a', class_ = '_9afda').text,
              soup.find('div', class_ = '_01029').text,
              re.findall(r'\"latitude\":([+-]?\d+[.,]?\d+)',str(soup))[0],
              re.findall(r'\"longitude\":([+-]\d+[.,]?\d+)',str(soup))[0]]
    except:
        try:
            geocoded_location = client.geocode(soup.find('a', class_="a73d7 _477fe").text)
            geo = geocoded_location.coords
        except:
            geo =['NA','NA']
        data = [soup.find('div', class_ ="_260f0").text,
              soup.find('a', class_="a73d7 _477fe").text,
              soup.find('div', class_="_477fe").text,
              soup.find('a', class_ = '_9afda').text,
              soup.find('div', class_ = '_01029').text,
              geo[0],
              geo[1]]
    return data

#[price, address, area, type, lat, lon]
t = len(df['Link'])
info = []
i = 0
for i in range(t):
    
    b =landwatch_grab(df['Link'][i])
    info.append(b)
info

#print(len(geo))
len(info)

gf = pd.DataFrame (info, columns = ['Price','Address','Area','Land Type','Status','Latitude','Longitude'])
#gf = gf.drop_duplicates(subset=['Address'], keep='first')
gf

# remove rows using the drop() function
gf.drop(gf.index[gf['Latitude'] == 'NA'], inplace=True)
# display the dataframe
gf

gf['Area'] = gf['Area'].str.replace(r'[A-Z ,:a-z]', '')
gf['Status'] = gf['Status'].str.replace(r'Available', 'For Sale')
gf["Area"] = gf["Area"].astype(float)

gf['Price'] = gf['Price'].replace('\$|,', '', regex=True)
gf['Price'] = pd.to_numeric(gf['Price'])

gf['Price'] = gf['Price'].apply(remove_sign,sign='$')

gf['Per Acre Price'] = gf['Price']/gf['Area']
pd.options.display.float_format = '{:.2f}'.format
gf

#df=df[['Per Acre Value','Unit']]
#gf = pd.read_excel('test.xlsx')
df=pd.DataFrame(gf)
dt = df
dt['Per Acre Price'] = dt['Per Acre Price'].apply(remove_sign,sign='$')
sns.boxplot(y='Per Acre Price', x='Status',data=dt[['Per Acre Price','Status']])
plt.xticks(rotation=90)
plt.ylabel('Price ($)')

df_outlier_removed=remove_outlier_IQR(df['Per Acre Price'])
df_outlier_removed=pd.DataFrame(df_outlier_removed)
ind_diff=df.index.difference(df_outlier_removed.index)

for i in range(0, len(ind_diff),1):
    df_final=df.drop([ind_diff[i]])
    df=df_final
    
sns.boxplot(y='Per Acre Price', x='Status',data=df_final[['Per Acre Price','Status']])
plt.xticks(rotation=90)
plt.ylabel('Price ($)')

len(ind_diff)

df_final

tf = gf.merge(df_final, on=['Address', 'Address'], how='left', indicator=True)
tf['Data4'] = tf.pop('_merge').eq('both')
qf = tf[tf['Data4']==False]
qf

df_final.to_excel(f'{file_name} comps.xlsx')
qf.to_excel(f'{file_name} BAD COMPS.xlsx')

