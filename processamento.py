import pandas as pd
import numpy as np
import os
from tqdm import tqdm

from tratamento import GeraDados

def carrega_base(file_path):
    field_list = [
        'paciente_id',
        'paciente_idade',
        'paciente_enumSexoBiologico',
        'paciente_racaCor_valor',
        'paciente_endereco_cep',
        'estabelecimento_municipio_codigo',
        'estabelecimento_municipio_nome',
        'estabelecimento_uf',
        'vacina_grupoAtendimento_nome',
        'vacina_categoria_nome',
        'vacina_lote',
        'vacina_dataAplicacao',
        'vacina_descricao_dose',
        'vacina_nome',
        'sistema_origem',
        'data_importacao_rnds'
    ]

    fieldtype_list = {
        'paciente_id': 'str',
        'paciente_idade': 'object',
        'paciente_enumSexoBiologico': 'str',
        'paciente_racaCor_valor': 'str',
        'estabelecimento_municipio_codigo': np.uint32,
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

    dfs = pd.read_csv('/home/hugo/Downloads/base.csv', sep=';', usecols=field_list, dtype=fieldtype_list, chunksize=1000000)
    l = []
    for df in dfs:
        l.append(df)
    
    df_base = pd.concat(l)
    df_base = df_base.dropna()

    return df_base

def processa_demanda(df):
    """
    Função para gerar as tabelas
    """
    if not os.path.exists(os.path.join('datasets', 'BRASIL')):
        os.mkdir(os.path.join('datasets', 'BRASIL'))

    if not os.path.exists(os.path.join('datasets', 'BRASIL', 'demanda')):
        os.mkdir(os.path.join('datasets', 'BRASIL', 'demanda'))

    if not os.path.exists(os.path.join('datasets', 'BRASIL', 'doses_por_dia')):
        os.mkdir(os.path.join('datasets', 'BRASIL', 'doses_por_dia'))

    if not os.path.exists(os.path.join('datasets', 'BRASIL', 'abandono-atraso-vacinal')):
            os.mkdir(os.path.join('datasets', 'BRASIL', 'abandono-atraso-vacinal'))

    if not os.path.exists(os.path.join('datasets', 'BRASIL', 'abandono-atraso-vacinal', 'TODOS')):
            os.mkdir(os.path.join('datasets', 'BRASIL', 'abandono-atraso-vacinal', 'TODOS'))

    data_brasil = GeraDados(df)
    data_brasil.gera_demanda(tipo_vacina='coronavac').to_csv('datasets/BRASIL/demanda/TODOS_coronavac.csv', sep=';', index=False)
    data_brasil.gera_demanda(tipo_vacina='astrazeneca').to_csv('datasets/BRASIL/demanda/TODOS_astrazeneca.csv', sep=';', index=False)
    data_brasil.gera_demanda().to_csv('datasets/BRASIL/demanda/TODOS.csv', sep=';', index=False)
    data_brasil.gerar_doses_por_dia().to_csv('datasets/BRASIL/doses_por_dia/TODOS.csv', sep=';', index=False)
    data_brasil.gerar_doses_por_dia(tipo_vacina='coronavac').to_csv('datasets/BRASIL/doses_por_dia/TODOS_coronavac.csv', sep=';', index=False)
    data_brasil.gerar_doses_por_dia(tipo_vacina='astrazeneca').to_csv('datasets/BRASIL/doses_por_dia/TODOS_coronavac.csv', sep=';', index=False)
    data_brasil.gera_serie_atraso().to_csv('datasets/BRASIL/abandono-atraso-vacinal/TODOS/serie-atraso.csv', sep=';', index=False)
    data_brasil = None
    print('BRASIL - OK')
    for uf in df['estabelecimento_uf'].unique():
        if not os.path.exists(os.path.join('datasets', uf)):
            os.mkdir(os.path.join('datasets', uf))

        if not os.path.exists(os.path.join('datasets', uf, 'demanda')):
            os.mkdir(os.path.join('datasets', uf, 'demanda'))

        if not os.path.exists(os.path.join('datasets', uf, 'doses_por_dia')):
            os.mkdir(os.path.join('datasets', uf, 'doses_por_dia'))

        if not os.path.exists(os.path.join('datasets', uf, 'abandono-atraso-vacinal')):
            os.mkdir(os.path.join('datasets', uf, 'abandono-atraso-vacinal'))

        if not os.path.exists(os.path.join('datasets', uf, 'abandono-atraso-vacinal', 'TODOS')):
            os.mkdir(os.path.join('datasets', uf, 'abandono-atraso-vacinal', 'TODOS'))

        df_estado = df.loc[df['estabelecimento_uf']==uf].reset_index(drop=True)
        data_estado = GeraDados(df_estado)
        data_estado.gera_demanda().to_csv('datasets/{}/demanda/TODOS.csv'.format(uf), sep=';', index=False)
        data_estado.gera_demanda(tipo_vacina='coronavac').to_csv('datasets/{}/demanda/TODOS_coronavac.csv'.format(uf), sep=';', index=False)
        data_estado.gera_demanda(tipo_vacina='astrazeneca').to_csv('datasets/{}/demanda/TODOS_astrazeneca.csv'.format(uf), sep=';', index=False)
        data_estado.gerar_doses_por_dia().to_csv('datasets/{}/doses_por_dia/TODOS.csv'.format(uf), sep=';', index=False)
        data_estado.gerar_doses_por_dia(tipo_vacina='coronavac').to_csv('datasets/{}/doses_por_dia/TODOS_coronavac.csv'.format(uf), sep=';', index=False)
        data_estado.gerar_doses_por_dia(tipo_vacina='astrazeneca').to_csv('datasets/{}/doses_por_dia/TODOS_astrazeneca.csv'.format(uf), sep=';', index=False)
        data_estado.gera_serie_atraso().to_csv('datasets/{}/abandono-atraso-vacinal/TODOS/serie-atraso.csv'.format(uf), sep=';')
        data_estado = None
        for cidade in tqdm(df_estado["estabelecimento_municipio_nome"].unique()):
            if not os.path.exists(os.path.join('datasets', uf, 'abandono-atraso-vacinal', cidade)):
                os.mkdir(os.path.join('datasets', uf, 'abandono-atraso-vacinal', cidade))

            df_municipio = df_estado.loc[df_estado['estabelecimento_municipio_nome']==cidade].reset_index(drop=True)
            data = GeraDados(df_municipio)
            data.gera_demanda().to_csv('datasets/{}/demanda/{}.csv'.format(uf, cidade), sep=';', index=False)
            data.gera_demanda(tipo_vacina='astrazeneca').to_csv('datasets/{}/demanda/{}_astrazeneca.csv'.format(uf, cidade), sep=';', index=False)
            data.gera_demanda(tipo_vacina='coronavac').to_csv('datasets/{}/demanda/{}_coronavac.csv'.format(uf, cidade), sep=';', index=False)
            data.gerar_doses_por_dia().to_csv('datasets/{}/doses_por_dia/{}.csv'.format(uf, cidade), sep=';', index=False)
            data.gerar_doses_por_dia(tipo_vacina='coronavac').to_csv('datasets/{}/doses_por_dia/{}_coronavac.csv'.format(uf, cidade), sep=';', index=False)
            data.gerar_doses_por_dia(tipo_vacina='astrazeneca').to_csv('datasets/{}/doses_por_dia/{}_astrazeneca.csv'.format(uf, cidade), sep=';', index=False)
            data.gera_serie_atraso().to_csv('datasets/{}/abandono-atraso-vacinal/{}/serie-atraso.csv'.format(uf, cidade), sep=';')
        print(uf+' - OK')
            
if __name__ == '__main__':
    df = carrega_base('/home/hugo/Downloads/base.csv')
    processa_demanda(df)