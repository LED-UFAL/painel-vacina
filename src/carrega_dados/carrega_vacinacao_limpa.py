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


engine = create_engine(connection_uri)


# In[3]:


sql = """
DROP TABLE IF EXISTS public.vacinacao_limpa;
"""

# Executing SQL command
with engine.connect() as con:
    con.execute(sql)


# In[4]:


sql_vacinacao = """
CREATE TABLE public.vacinacao_limpa
(
    id_vacinacao SERIAL,
    {cols}, {cols_norm}
)
""".format(cols=',\n '.join(['"{col}" {tipo}'.format(col=col['nome'], tipo=col['tipo']) for col in COLUNAS_VACINACAO if col['nome'] not in COLUNAS_CATEGORICAS]),
                                               cols_norm=',\n '.join(['"id_{col}" SMALLINT'.format(col=col) for col in COLUNAS_CATEGORICAS])
          )
print(sql_vacinacao)


# In[5]:


# Executing SQL command
with engine.connect() as con:
    con.execute(sql_vacinacao)


# In[6]:



COLUNAS_DISTINCT


# In[7]:


select_str = """SELECT DISTINCT ON ({cols_dist})
               {cols}, {cols_norm}

""".format(cols_dist=', '.join(['vacinacao_norm."{col}"'.format(col=col) for col in COLUNAS_DISTINCT]),
           cols=', '.join(['vacinacao_norm."{col}"'.format(col=col) for col in COLUNAS_GERAL]),
           cols_norm=', '.join(['vacinacao_norm."id_{col}"'.format(col=col) for col in COLUNAS_CATEGORICAS]))

print(select_str)


# In[8]:


from_str = 'FROM vacinacao_norm'
from_str


# In[9]:


insert_str = 'INSERT INTO vacinacao_limpa ({cols}, {cols_norm})\n'.format(cols=', '.join(['"{col}"'.format(col=col) for col in COLUNAS_GERAL]),
                                               cols_norm=', '.join(['"id_{col}"'.format(col=col) for col in COLUNAS_CATEGORICAS])
          )
insert_str


# In[10]:


sql = """
    {insert}
    {select}
    ;
""".format(select=select_str+from_str, insert=insert_str)
print(sql)


# In[11]:



with engine.connect() as con:
    con.execute(sql)


# In[ ]:




