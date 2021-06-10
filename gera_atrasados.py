from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from tqdm import tqdm
import os

CURRENT_DIR = os.path.dirname(__file__)

FIELD_LIST = [
    'paciente_id',
    'estabelecimento_municipio_nome',
    'estabelecimento_uf',
    'vacina_dataaplicacao',
    'vacina_descricao_dose',
    'vacina_nome'
]

def carrega_base(file_path, chunk_size=int(1e6)):
    dataframes = pd.read_csv(
        file_path, sep=';', usecols=FIELD_LIST, chunksize=chunk_size
    )
    dataframe = pd.DataFrame(columns=FIELD_LIST)

    for chunk_df in dataframes:
        dataframe = pd.concat([dataframe, chunk_df], ignore_index=True)

    dataframe = dataframe.rename(columns={'vacina_dataaplicacao': 'vacina_dataAplicacao'})

    return dataframe

if __name__ == '__main__':
    df = carrega_base('base.csv')
    df['vacina_descricao_dose'] = df['vacina_descricao_dose'].apply(lambda x: x.replace('\xa0', ''))
    df['vacina_dataAplicacao'] = df['vacina_dataAplicacao'].apply(lambda x: datetime.strptime(x[:10], '%Y-%m-%d').date())
    l = []
    set_dose2_coronavac = set(df[(df['vacina_descricao_dose']=='2ªDose') & (df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan')]['paciente_id'])
    set_dose2_astrazeneca = set(df[(df['vacina_descricao_dose']=='2ªDose') & (df['vacina_nome'].isin(['Covid-19-AstraZeneca', 'Vacina Covid-19 - Covishield']))]['paciente_id'])
    for estado in df['estabelecimento_uf'].unique():
        df_estado = df[df['estabelecimento_uf']==estado]
        for cidade in tqdm(df_estado['estabelecimento_municipio_nome'].unique()):
            dic = {}
            df_cidade = df_estado[df_estado['estabelecimento_municipio_nome']==cidade].reset_index(drop=True)
            set_dose1_coronavac_cidade = set(df_cidade[(df_cidade['vacina_descricao_dose']=='1ªDose') & (df_cidade['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan') & (df_cidade['vacina_dataAplicacao'] <= datetime.today().date() - timedelta(days=28))]['paciente_id'])
            set_dose2_coronavac_cidade = set_dose1_coronavac_cidade.intersection(set_dose2_coronavac)
            set_dose1_astrazeneca_cidade = set(df_cidade[(df_cidade['vacina_descricao_dose']=='1ªDose') & (df_cidade['vacina_nome'].isin(['Covid-19-AstraZeneca', 'Vacina Covid-19 - Covishield'])) & (df_cidade['vacina_dataAplicacao'] <= datetime.today().date() - timedelta(days=84))]['paciente_id'])
            set_dose2_astrazeneca_cidade = set_dose1_astrazeneca_cidade.intersection(set_dose2_astrazeneca)
            dic['Estado'] = estado
            dic['Município'] = cidade
            if len(set_dose1_coronavac_cidade)!=0:
                dic['Percentual de atrasados (CoronaVac)'] = '%.2f' % (len(set_dose1_coronavac_cidade.difference(set_dose2_coronavac_cidade))*100 / len(set_dose1_coronavac_cidade)) + '%'
            else:
                dic['Percentual de atrasados (CoronaVac)'] = '0%'
            if len(set_dose1_astrazeneca_cidade)!=0:
                dic['Percentual de atrasados (Astrazeneca)'] = '%.2f' % (len(set_dose1_astrazeneca_cidade.difference(set_dose2_astrazeneca_cidade))*100/ len(set_dose1_astrazeneca_cidade)) +'%'
            else:
                dic['Percentual de atrasados (Astrazeneca)'] = '0%'
            dic['Total de pacientes com primeiras doses há 28 dias (CoronaVac)'] = len(set_dose1_coronavac_cidade)
            dic['Total de atrasados (CoronaVac)'] = len(set_dose1_coronavac_cidade.difference(set_dose2_coronavac_cidade))
            dic['Total de pacientes com primeiras doses há 84 dias (Astrazeneca)'] = len(set_dose1_astrazeneca_cidade)
            dic['Total de atrasados (Astrazeneca)'] = len(set_dose1_astrazeneca_cidade.difference(set_dose2_astrazeneca_cidade))
            l.append(dic)

    df = pd.DataFrame(l).sort_values(by=['Estado', 'Município'])
    l = []
    l.append({
    'Estado': 'Todos', 'Município': 'Todos',
    'Total de pacientes com primeiras doses há 28 dias (CoronaVac)': df['Total de pacientes com primeiras doses há 28 dias (CoronaVac)'].sum(),
    'Total de atrasados (CoronaVac)': df['Total de atrasados (CoronaVac)'].sum(),
    'Total de pacientes com primeiras doses há 84 dias (Astrazeneca)': df['Total de pacientes com primeiras doses há 84 dias (Astrazeneca)'].sum(),
    'Total de atrasados (Astrazeneca)': df['Total de atrasados (Astrazeneca)'].sum(),
    'Percentual de atrasados (Astrazeneca)': '%.2f' % (df['Total de atrasados (Astrazeneca)'].sum()*100/df['Total de pacientes com primeiras doses há 84 dias (Astrazeneca)'].sum()) + '%',
    'Percentual de atrasados (CoronaVac)': '%.2f' % (df['Total de atrasados (CoronaVac)'].sum()*100/df['Total de pacientes com primeiras doses há 28 dias (CoronaVac)'].sum()) + '%',
    })
    for estado in df['Estado'].unique():
        df_estado = df.loc[df['Estado']==estado]
        l.append({
        'Estado': estado, 'Município': 'Todos',
        'Total de pacientes com primeiras doses há 28 dias (CoronaVac)': df_estado['Total de pacientes com primeiras doses há 28 dias (CoronaVac)'].sum(),
        'Total de atrasados (CoronaVac)': df_estado['Total de atrasados (CoronaVac)'].sum(),
        'Total de pacientes com primeiras doses há 84 dias (Astrazeneca)': df_estado['Total de pacientes com primeiras doses há 84 dias (Astrazeneca)'].sum(),
        'Total de atrasados (Astrazeneca)': df_estado['Total de atrasados (Astrazeneca)'].sum(),
        'Percentual de atrasados (Astrazeneca)': '%.2f' % (df_estado['Total de atrasados (Astrazeneca)'].sum()*100/df_estado['Total de pacientes com primeiras doses há 84 dias (Astrazeneca)'].sum()) + '%',
        'Percentual de atrasados (CoronaVac)': '%.2f' % (df_estado['Total de atrasados (CoronaVac)'].sum()*100/df_estado['Total de pacientes com primeiras doses há 28 dias (CoronaVac)'].sum()) + '%',
    })
    df = pd.concat([df, pd.DataFrame(l).sort_values(by=['Estado', 'Município'])], ignore_index=True)

    pd.set_option('colheader_justify', 'center')
    html_string = '''<html>
    <head><title>Atrasados</title></head>
    <link rel="stylesheet" type="text/css" href="style.css"/>
    <body><h1>Tabela de atrasados BRASIL - {date}</h1>{table}</body>
</html>
'''
    css_string = '''.mystyle {
    font-size: 11pt; 
    font-family: Arial;
    border-collapse: collapse; 
    border: 1px solid silver;

}

.mystyle td, th {
    padding: 5px;
}

.mystyle tr:nth-child(even) {
    background: #E0E0E0;
}

.mystyle tr:hover {
    background: silver;
    cursor: pointer;
}
'''
    if not os.path.exists(os.path.join(CURRENT_DIR, 'atrasados')):
        os.mkdir(os.path.join(CURRENT_DIR, 'atrasados'))
    with open(os.path.join(CURRENT_DIR, 'atrasados', 'atrasados_BRASIL_{}.html'.format(str(datetime.today().date()-timedelta(days=1)))), 'w') as f:
        f.write(html_string.format(date=str(datetime.today().date()-timedelta(days=1)), table=df.to_html(classes='mystyle', index=False)))
    with open(os.path.join(CURRENT_DIR, 'atrasados', 'style.css'), 'w') as f:
        f.write(css_string)
