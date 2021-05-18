import pandas as pd

COLUNAS_VACINACAO = [
    {'nome': 'paciente_id', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'paciente_idade', 'tipo': 'int', 'tipo_pandas': 'Int64', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'paciente_dataNascimento', 'tipo': 'date', 'tipo_pandas': 'date', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'paciente_enumSexoBiologico', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'paciente_racaCor_valor', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 1, 'distinct': 1, 'trim': 1},
    {'nome': 'paciente_endereco_coIbgeMunicipio', 'tipo': 'int', 'tipo_pandas': pd.Int64Dtype(), 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'paciente_endereco_uf', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'paciente_endereco_cep', 'tipo': 'double precision', 'tipo_pandas': pd.Int64Dtype(), 'categorica': 0, 'distinct': 0, 'trim': 0},
    {'nome': 'paciente_nacionalidade_enumNacionalidade', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 1},
    {'nome': 'estabelecimento_valor', 'tipo': 'bigint', 'tipo_pandas': 'Int64', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'estabelecimento_razaoSocial', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 1},
    {'nome': 'estalecimento_noFantasia', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 1},
    {'nome': 'estabelecimento_municipio_codigo', 'tipo': 'int', 'tipo_pandas': pd.Int64Dtype(), 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'estabelecimento_uf', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 1},
    {'nome': 'vacina_grupoAtendimento_nome', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 1, 'distinct': 1, 'trim': 1},
    {'nome': 'vacina_categoria_codigo', 'tipo': 'double precision', 'tipo_pandas': pd.Int64Dtype(), 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'vacina_categoria_nome', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 1},
    {'nome': 'vacina_dataAplicacao', 'tipo': 'date', 'tipo_pandas': 'date', 'categorica': 0, 'distinct': 1, 'trim': 0},
    {'nome': 'vacina_descricao_dose', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 0, 'distinct': 1, 'trim': 1},
    {'nome': 'vacina_nome', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 1, 'distinct': 1, 'trim': 1},
    {'nome': 'sistema_origem', 'tipo': 'text', 'tipo_pandas': 'str', 'categorica': 1, 'distinct': 0, 'trim': 1},
    {'nome': 'data_importacao_rnds', 'tipo': 'date', 'tipo_pandas': 'date', 'categorica': 0, 'distinct': 0, 'trim': 0}
]

COLUNAS_VACINACAO = [dict((k, v.lower() if isinstance(v, str) else v) for k,v in col.items()) for col in COLUNAS_VACINACAO]

COLUNAS_TODAS = [col['nome'] for col in COLUNAS_VACINACAO]

COLUNAS_CATEGORICAS = [col['nome'] for col in COLUNAS_VACINACAO if col['categorica']]

COLUNAS_GERAL = list(set(COLUNAS_TODAS) - set(COLUNAS_CATEGORICAS))

COLUNAS_DISTINCT = [('id_' if col['categorica'] else '') + col['nome'] for col in COLUNAS_VACINACAO if col['distinct']]

COLUNAS_DATA = [col['nome'] for col in COLUNAS_VACINACAO if col['tipo'] == 'date']

connection_uri = 'postgres://usr_vacinas:sovacinasalva@localhost:5432/vacinas'
