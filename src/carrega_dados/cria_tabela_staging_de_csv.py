#!/usr/bin/env python
# coding: utf-8

# In[4]:


# !pip install psycopg2
from sqlalchemy import create_engine
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import pandas as pd
import numpy as np

from settings import *


# In[6]:


data_dir = os.path.join(os.path.abspath(''), '../../datasets/raw/')

pop_data_dir = os.path.join(os.path.abspath(''), '../../datasets/datasus/')


# In[7]:


# obtém lista de arquivos
files = [f for f in listdir(data_dir) if isfile(join(data_dir, f)) and f.startswith('open-datasus')]
files.sort()


# obtém sufixo (data) dos arquivos mais recentes
suffix = files[-1].split('-')[2]

# seleciona arquivos mais recentes
last_files = [f for f in files if f.endswith(suffix)]

last_files


# In[4]:


file = last_files[1]

file


# In[5]:


FIELD_LIST = [
    'paciente_id',
    'paciente_idade',
    'paciente_enumSexoBiologico',
    'paciente_racaCor_valor',
    'paciente_endereco_cep',
    'paciente_endereco_coIbgeMunicipio',
    'estabelecimento_municipio_codigo',
    'estabelecimento_municipio_nome',
    'estabelecimento_uf',
    'vacina_grupoAtendimento_nome',
    'vacina_categoria_codigo',
    'vacina_categoria_nome',
    'vacina_lote',
    'vacina_dataAplicacao',
    'vacina_descricao_dose',
    'vacina_nome',
    'sistema_origem',
    'data_importacao_rnds'
]

FIELD_TYPE_LIST = {
    'paciente_id': 'str',
    'paciente_idade': np.uint8,
    'paciente_enumSexoBiologico': 'str',
    'paciente_racaCor_valor': 'str',
    'paciente_endereco_coIbgeMunicipio': 'int',
    'estabelecimento_municipio_codigo': 'int',
    'estabelecimento_municipio_nome': 'str',
    'estabelecimento_uf': 'str',
    'vacina_grupoAtendimento_nome': 'str',
    'vacina_categoria_nome': 'str',
    'vacina_lote': 'str',
    'vacina_dataAplicacao': 'str',
    'vacina_descricao_dose': 'str',
    'vacina_nome': 'str',
    'sistema_origem': 'str',
    'data_importacao_rnds': 'object'
}


# In[6]:


FIELD_TYPE_LIST = {col['nome']: col['tipo_pandas'] for col in COLUNAS_VACINACAO if col['tipo'] not in ['date']}
FIELD_TYPE_LIST


# In[7]:


df = pd.read_csv(data_dir + file, dtype=FIELD_TYPE_LIST,sep=';', parse_dates=COLUNAS_DATA) #dtype=FIELD_TYPE_LIST, 

df


# In[8]:


df.describe(include='all')


# In[9]:


engine = create_engine(connection_uri)


# In[10]:




df.to_sql(
    name='staging',
    con=engine,
    if_exists='replace',
    index=False)


# In[11]:


data_dir


# In[14]:


df_pop = pd.read_csv(pop_data_dir + 'faixas_niveis_2020.csv', sep=';')

df_pop


# In[15]:


df_pop.to_sql(
    name='populacao',
    con=engine,
    if_exists='fail',
    index=False)


# In[ ]:




