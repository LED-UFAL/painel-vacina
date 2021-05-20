import os
import argparse
from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm

from tratamento import GeraDados


CURRENT_DIR = os.path.dirname(__file__)

OLD_FIELD_LIST = [
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

NEW_FIELD_LIST = [
    col.lower() for col in OLD_FIELD_LIST
]

FIELD_TYPE_LIST = {
    'paciente_id': 'str',
    'paciente_idade': 'Int64',
    'paciente_enumsexobiologico': 'str',
    'paciente_racacor_valor': 'str',
    'estabelecimento_municipio_codigo': np.uint32,
    'estabelecimento_municipio_nome': 'str',
    'estabelecimento_uf': 'str',
    'vacina_grupoatendimento_nome': 'str',
    'vacina_categoria_nome': 'str',
    'vacina_lote': 'str',
    'vacina_dataaplicacao': 'str',
    'vacina_descricao_dose': 'str',
    'vacina_nome': 'str',
    'sistema_origem': 'str',
    'data_importacao_rnds': 'object'
}


def carrega_base(file_path, chunk_size=int(1e6)):
    """
    Loads the dataframe in chunks keeping only columns in FIELD_LIST.

    :param file_path: Path to the source csv file.
    :param chunk_size: Size of each chunk that the dataframe will be split.
    :returns: Pandas DataFrame with filtered columns.
    """
    dataframes = pd.read_csv(
        file_path, sep=';', usecols=NEW_FIELD_LIST, dtype=FIELD_TYPE_LIST, chunksize=chunk_size
    )
    dataframe = pd.DataFrame(columns=NEW_FIELD_LIST)

    for chunk_df in dataframes:
        dataframe = pd.concat([dataframe, chunk_df], ignore_index=True)


    dataframe = dataframe.rename(columns=dict(zip(NEW_FIELD_LIST, OLD_FIELD_LIST))).dropna()

    ## Salva o timestamp dos dados baseado na hora da última vacina aplicada segundo
    ## a data de importacao rnds.
    date_str = dataframe['data_importacao_rnds'].max()
    date_timestamp = str(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
    if not os.path.exists(os.path.join('datasets')):
        os.mkdir(os.path.join('datasets'))
    open(os.path.join('datasets','data_timestamp.txt'), 'w').write(str(date_timestamp))

    return dataframe


def processa_demanda(df):
    """
    Função para gerar as tabelas
    """
    population_file = os.path.join(CURRENT_DIR, 'datasets', 'datasus') + '/faixas_niveis_2020.csv'
    df_pop = pd.read_csv(population_file,  {'CodEst': np.float64, 'CodMun': np.float64}, delimiter=';')


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

    if not os.path.exists(os.path.join('datasets', 'BRASIL', 'cobertura')):
        os.mkdir(os.path.join('datasets', 'BRASIL', 'cobertura'))

    data_brasil = GeraDados(df)
    data_brasil.gera_demanda().to_csv('datasets/BRASIL/demanda/TODOS.csv', sep=';', index=False)
    data_brasil.gerar_doses_por_dia().to_csv('datasets/BRASIL/doses_por_dia/TODOS.csv', sep=';', index=False)
    data_brasil.gera_serie_atraso().to_csv('datasets/BRASIL/abandono-atraso-vacinal/TODOS/serie-atraso.csv', sep=';')
    data_brasil.gera_cobertura(df_pop, nivel='N').to_csv('datasets/BRASIL/cobertura/TODOS.csv', sep=';')
    for vacina in ('coronavac', 'astrazeneca', 'pfizer'):
        data_brasil.gera_demanda(tipo_vacina=vacina).to_csv('datasets/BRASIL/demanda/TODOS_{}.csv'.format(vacina), sep=';', index=False)
        data_brasil.gerar_doses_por_dia(tipo_vacina=vacina).to_csv('datasets/BRASIL/doses_por_dia/TODOS_{}.csv'.format(vacina), sep=';', index=False)    
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

        if not os.path.exists(os.path.join('datasets', uf, 'cobertura')):
            os.mkdir(os.path.join('datasets', uf, 'cobertura'))

        df_estado = df.loc[df['estabelecimento_uf']==uf].reset_index(drop=True)
        data_estado = GeraDados(df_estado)
        data_estado.gera_demanda().to_csv('datasets/{}/demanda/TODOS.csv'.format(uf), sep=';', index=False)
        data_estado.gerar_doses_por_dia().to_csv('datasets/{}/doses_por_dia/TODOS.csv'.format(uf), sep=';', index=False)
        data_estado.gera_serie_atraso().to_csv('datasets/{}/abandono-atraso-vacinal/TODOS/serie-atraso.csv'.format(uf), sep=';')
        for vacina in ('coronavac', 'astrazeneca', 'pfizer'):
            data_estado.gera_demanda(tipo_vacina=vacina).to_csv('datasets/{}/demanda/TODOS_{}.csv'.format(uf, vacina), sep=';', index=False)
            data_estado.gerar_doses_por_dia(tipo_vacina=vacina).to_csv('datasets/{}/doses_por_dia/TODOS_{}.csv'.format(uf, vacina), sep=';', index=False)
        # obtem o codigo do estado do primeiro registro
        cod_estado = float(str(df_estado.iloc[0, :]['estabelecimento_municipio_codigo'])[:2])
        data_estado.gera_cobertura(df_pop, nivel='E', codigo=cod_estado).to_csv('datasets/{}/cobertura/TODOS.csv'.format(uf), sep=';')
        data_estado = None
        for cidade in tqdm(df_estado["estabelecimento_municipio_nome"].unique()):
            if not os.path.exists(os.path.join('datasets', uf, 'abandono-atraso-vacinal', cidade)):
                os.mkdir(os.path.join('datasets', uf, 'abandono-atraso-vacinal', cidade))

            df_municipio = df_estado.loc[df_estado['estabelecimento_municipio_nome']==cidade].reset_index(drop=True)
            data = GeraDados(df_municipio)
            data.gera_demanda().to_csv('datasets/{}/demanda/{}.csv'.format(uf, cidade), sep=';', index=False)
            data.gerar_doses_por_dia().to_csv('datasets/{}/doses_por_dia/{}.csv'.format(uf, cidade), sep=';', index=False)
            data.gera_serie_atraso().to_csv('datasets/{}/abandono-atraso-vacinal/{}/serie-atraso.csv'.format(uf, cidade), sep=';')
            for vacina in ('coronavac', 'astrazeneca', 'pfizer'):
                data.gera_demanda(tipo_vacina=vacina).to_csv('datasets/{}/demanda/{}_{}.csv'.format(uf, cidade, vacina), sep=';', index=False)
                data.gerar_doses_por_dia(tipo_vacina=vacina).to_csv('datasets/{}/doses_por_dia/{}_{}.csv'.format(uf, cidade, vacina), sep=';', index=False)
            cod_mun = float(str(df_estado.iloc[0, :]['estabelecimento_municipio_codigo'])[:6])
            data.gera_cobertura(df_pop, nivel='M', codigo=cod_mun).to_csv('datasets/{}/cobertura/{}.csv'.format(uf, cidade), sep=';')
        print(uf+' - OK')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_path", default="base.csv")

    args = parser.parse_args()

    df = carrega_base(file_path=args.csv_path)

    processa_demanda(df)
