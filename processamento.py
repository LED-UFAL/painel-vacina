import pandas as pd
import os

from tratamento import GeraDados

fields = [
    "paciente_id",
    "paciente_idade",
    "paciente_dataNascimento",
    "vacina_dataAplicacao",
    "vacina_descricao_dose",
    "vacina_codigo",
    "vacina_nome",
    "estabelecimento_uf",
    "estabelecimento_municipio_nome",
]

def processa_demanda(df):
    """
    Função para gerar as tabelas
    """
    df = df[fields]
    for uf in df['estabelecimento_uf'].unique():
        if not os.path.exists(os.path.join('datasets', uf)):
            os.mkdir(os.path.join('datasets', uf))

        if not os.path.exists(os.path.join('datasets', uf, 'demanda')):
            os.mkdir(os.path.join('datasets', uf, 'demanda'))

        if not os.path.exists(os.path.join('datasets', uf, 'doses_por_dia')):
            os.mkdir(os.path.join('datasets', uf, 'doses_por_dia'))

        df_estado = df.loc[df['estabelecimento_uf']==uf].reset_index(drop=True)
        data_estado = GeraDados(df_estado)
        data_estado.gera_demanda().to_csv('datasets/{}/demanda/TODOS.csv'.format(uf), sep=';', index=False)
        data_estado.gera_demanda(tipo_vacina='coronavac').to_csv('datasets/{}/demanda/TODOS_coronavac.csv'.format(uf), sep=';', index=False)
        data_estado.gera_demanda(tipo_vacina='astrazeneca').to_csv('datasets/{}/demanda/TODOS_astrazeneca.csv'.format(uf), sep=';', index=False)
        data_estado.gerar_doses_por_dia().to_csv('datasets/{}/doses_por_dia/TODOS.csv'.format(uf), sep=';', index=False)
        for cidade in df["estabelecimento_municipio_nome"].unique():
            df_municipio = df.loc[df['estabelecimento_municipio_nome']==cidade].reset_index(drop=True)
            data = GeraDados(df_municipio)
            data.gera_demanda().to_csv('datasets/{}/demanda/{}.csv'.format(uf, cidade), sep=';', index=False)
            data.gera_demanda(tipo_vacina='astrazeneca').to_csv('datasets/{}/demanda/{}_astrazeneca.csv'.format(uf, cidade), sep=';', index=False)
            data.gera_demanda(tipo_vacina='coronavac').to_csv('datasets/{}/demanda/{}_coronavac.csv'.format(uf, cidade), sep=';', index=False)
            data.gerar_doses_por_dia().to_csv('datasets/{}/doses_por_dia/{}.csv'.format(uf, cidade), sep=';', index=False)

if __name__ == '__main__':
    df = pd.read_csv('AL.csv', sep=';')
    processa_demanda(df)