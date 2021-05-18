#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sqlalchemy import create_engine
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import pandas as pd
import numpy as np

from settings import *


# In[2]:


data_dir = os.path.join(os.path.abspath(''), '../../datasets/raw/')

file = 'open-datasus_AC-2021_05_11.csv'

chunk_size=int(1e6)


# In[3]:


# obtém lista de arquivos
files = [f for f in listdir(data_dir) if isfile(join(data_dir, f)) and f.startswith('open-datasus')]
files.sort()


# obtém sufixo (data) dos arquivos mais recentes
suffix = files[-1].split('-')[2]

# seleciona arquivos mais recentes
last_files = [f for f in files if f.endswith(suffix)]

last_files


# In[4]:


engine = create_engine(connection_uri)


# In[5]:




sql = """
DELETE FROM staging;
"""

# Executing SQL command
with engine.connect() as con:
    con.execute(sql)


# In[6]:


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
    'paciente_idade': 'str',
    'paciente_enumSexoBiologico': 'str',
    'paciente_racaCor_valor': 'str',
    'paciente_endereco_coIbgeMunicipio': 'str',
    'estabelecimento_municipio_codigo': 'str',
    'estabelecimento_municipio_nome': 'str',
    'estabelecimento_uf': 'str',
    'vacina_grupoAtendimento_nome': 'str',
    'vacina_categoria_nome': 'str',
    'vacina_lote': 'str',
    'vacina_dataAplicacao': 'str',
    'vacina_descricao_dose': 'str',
    'vacina_nome': 'str',
    'sistema_origem': 'str',
}


# In[7]:


FIELD_TYPE_LIST = dict((k.lower(), v.lower()) for k,v in FIELD_TYPE_LIST.items())

FIELD_TYPE_LIST


# In[8]:


COLUNAS_DATA


# In[9]:



for file in last_files[:2]:
    print('Processing...', file)
    for chunk in pd.read_csv(data_dir + file, sep=';', dtype=FIELD_TYPE_LIST, parse_dates=COLUNAS_DATA, chunksize=chunk_size):
        chunk.to_sql(
            name='staging',
            con=engine,
            if_exists='append',
            index=False)


# In[10]:


COLUNAS_VACINACAO


# ## Limpa espaços (trim) de todos os campos string

# In[11]:


sql = """
    UPDATE staging SET {to_trim}
    ;
    """.format(to_trim = ', '.join(['"{col}" = TRIM("{col}")'.format(col=col['nome']) for col in COLUNAS_VACINACAO if col['trim']]))

print(sql)


# In[12]:


with engine.connect() as con:
    con.execute(sql)


# In[13]:



for col in COLUNAS_CATEGORICAS:
    sql = """
    DROP TABLE IF EXISTS "{col}";
    CREATE TABLE "{col}"(
      "id_{col}" SMALLSERIAL,
      "{col}" text  
    );
    """.format(col = col)
    with engine.connect() as con:
        con.execute(sql)
    sql = """
    INSERT INTO "{col}" ("{col}")
    SELECT DISTINCT "{col}" FROM staging WHERE "{col}" IS NOT NULL
    """.format(col = col)
    with engine.connect() as con:
        con.execute(sql)


# In[ ]:




