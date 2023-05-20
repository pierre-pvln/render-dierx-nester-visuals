#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd 
import plotly.express as px


# In[12]:


#dataset_path = "./data/final/DIERX_test.csv"
dataset_path = "http://partnersupport.neacon.eu/Dierx/print_values.php?auth=cordiplan"

locations_path = "./data/final/DIERX_locations.csv"


# In[13]:


# Read data from file 'filename.csv' 
dataset = pd.read_csv(dataset_path, sep=";",header=None, dtype=str) 

# name columns
dataset.columns =['IMEI_str', 'date-time_str', 'payload']

# remove de '<br> at the the end of the payload string
# only valid for http download
dataset['payload'] = dataset['payload'].str.replace(r'<br>$', '',regex=True)

# Split string column into two new columns
dataset[['payload_type', 'payload_1', 'payload_2']] = dataset.payload.str.split(":", expand = True)

dataset[['payload_1','payload_2']] = dataset[['payload_1','payload_2']].astype(float)


# In[14]:


# Preview the first 5 lines of the loaded data 
display(dataset.head())
display(dataset.dtypes)
display(dataset['IMEI_str'].unique())


# In[15]:


# Read data from file 'filename.csv' 
locations = pd.read_csv(locations_path, sep=";", dtype=str) 

locations['Adres'] = locations['Straat'] + " " + locations['Huisnummer'] + " " + locations['Postcode'] + " " + locations['Plaats']


# In[16]:


# Preview the first 5 lines of the loaded data 
display(locations.head())
display(locations.dtypes)
display(locations['serienr'].unique())


# In[17]:


merged = pd.merge(dataset, locations, left_on='IMEI_str', right_on='serienr')
display(merged.head())

# https://strftime.org/
merged['date-time_dt'] =  pd.to_datetime(dataset['date-time_str'], format='%Y-%m-%d %H:%M:%S')

# set dt column as index
merged.set_index('date-time_dt',inplace=True)

# sort on index
merged.sort_index(inplace=True)


# In[19]:


# Preview the first 5 lines of the loaded data 
display(merged.head())
display(merged.tail())
display(merged.dtypes)


# In[22]:


fig = px.line(merged, x="date-time_str", y=["payload_1"], color='Adres')
fig.show()


# In[23]:


fig = px.line(merged, x="date-time_str", y=["payload_2"], color='Adres')
fig.show()


# In[ ]:




