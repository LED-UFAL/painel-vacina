import pandas as pd 

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
        df_estado = df.loc[df['estabelecimento_uf']==uf].reset_index(drop=True)
        GeraDados(df_estado).gera_demanda().to_csv('datasets/{}/demanda/TODOS.csv'.format(uf), sep=';', index=False)
        for cidade in df["estabelecimento_municipio_nome"].unique():
            df_municipio = df.loc[df['estabelecimento_municipio_nome']==cidade].reset_index(drop=True)
            data = GeraDados(df_municipio)
            data.gera_demanda().to_csv('datasets/{}/demanda/{}.csv'.format(uf, cidade), sep=';', index=False)

if __name__ == '__main__':
    df = pd.read_csv('AL.csv', sep=';')
    processa_demanda(df)