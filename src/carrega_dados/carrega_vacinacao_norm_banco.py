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
DROP TABLE IF EXISTS public.vacinacao_norm;
"""

# Executing SQL command
with engine.connect() as con:
    con.execute(sql)


# In[4]:


# sql_vacinacao = """
# CREATE TABLE public.vacinacao
# (
#     {cols}
# )
# """.format(cols = ",\n".join(['"{col}" {tipo}'.format(col=col['nome'], tipo=col['tipo']) for col in COLUNAS_VACINACAO]))

# print(sql_vacinacao)


# In[5]:


sql_vacinacao = """
CREATE TABLE public.vacinacao_norm
(
    {cols}, {cols_norm}
)
""".format(cols=',\n '.join(['"{col}" {tipo}'.format(col=col['nome'], tipo=col['tipo']) for col in COLUNAS_VACINACAO if col['nome'] not in COLUNAS_CATEGORICAS]),
                                               cols_norm=',\n '.join(['"id_{col}" SMALLINT'.format(col=col) for col in COLUNAS_CATEGORICAS])
          )
print(sql_vacinacao)


# In[6]:



# sql_vacinacao = """
# CREATE TABLE public.vacinacao
# (
#     paciente_id text,
#     paciente_idade text,
#     "paciente_dataNascimento" text,
#     "paciente_enumSexoBiologico" VARCHAR,
#     "paciente_racaCor_valor" text,
#     "paciente_endereco_coIbgeMunicipio" text,
#     paciente_endereco_uf text,
#     paciente_endereco_cep double precision,
#     "paciente_nacionalidade_enumNacionalidade" text,
#     estabelecimento_valor bigint,
#     "estabelecimento_razaoSocial" text,
#     "estalecimento_noFantasia" text,
#     estabelecimento_municipio_codigo text,
#     estabelecimento_uf text,
#     "vacina_grupoAtendimento_nome" text,
#     vacina_categoria_codigo double precision,
#     vacina_categoria_nome text,
#     "vacina_dataAplicacao" date,
#     vacina_descricao_dose text,
#     vacina_nome text,
#     sistema_origem text,
#     vacina_grupoAtendimento_nome bigint,
#     data_importacao_rnds date
# )
# WITH (
#     OIDS = FALSE
# )
# TABLESPACE pg_default;

# ALTER TABLE public.staging
#     OWNER to luizcelso;
# """


# In[7]:


# Executing SQL command
with engine.connect() as con:
    con.execute(sql_vacinacao)


# In[8]:


cols = [x.strip().split(" ")[0] for x in ''.join(sql_vacinacao.split("(")[1]).split(")")[0].split(',')]

cols_str = ', '.join(cols)

cols_str


# In[9]:


cols


# In[10]:


# sql_vacinacao_insert = """
# INSERT INTO vacinacao
# SELECT {} 
# FROM staging 
# --LIMIT 10
# ;
# """.format(cols_str)

# print(sql_vacinacao_insert)


# In[11]:


select_str = 'SELECT {cols}, {cols_norm}\n'.format(cols=', '.join(['staging."{col}"'.format(col=col) for col in COLUNAS_GERAL]),
                                               cols_norm=', '.join(['"{col}"."id_{col}"'.format(col=col) for col in COLUNAS_CATEGORICAS])
          )

select_str


# In[12]:


from_str = 'FROM staging {tables}\n'.format(tables=' '.join(['LEFT JOIN "{c}" ON (staging."{c}"="{c}"."{c}")'.format(c=x) for x in COLUNAS_CATEGORICAS])
          )
from_str


# In[13]:


insert_str = 'INSERT INTO vacinacao_norm ({cols}, {cols_norm})\n'.format(cols=', '.join(['"{col}"'.format(col=col) for col in COLUNAS_GERAL]),
                                               cols_norm=', '.join(['"id_{col}"'.format(col=col) for col in COLUNAS_CATEGORICAS])
          )
insert_str


# In[14]:


sql = """
    {insert}
    {select}
    ;
""".format(select=select_str+from_str, insert=insert_str)
print(sql)


# In[15]:



with engine.connect() as con:
    con.execute(sql)


# In[16]:




COLUNAS_GERAL


# In[ ]:




