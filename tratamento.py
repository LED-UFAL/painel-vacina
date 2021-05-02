from datetime import datetime, timedelta
import pandas as pd
import numpy

DATE_COLUMN = {
    1: "vacina_dose_1",
    2: "vacina_dose_2"
}

DOSE_OFFSET = {
    "Covid-19-AstraZeneca": 84,
    "Covid-19-Coronavac-Sinovac/Butantan": 28
}

def compute_delay(row):
    if pd.isna(row["vacina_dose_2"]) or pd.isna(row["vacina_dose_1"]):
        return None
    return row["vacina_dose_2"] - (row["vacina_dose_1"] + timedelta(days=row["vacina_janela"]))

def abandon_rate(data, date, vaccine_name):
    data_ = data[data.vacina_nome == vaccine_name].reset_index(drop=True)
    data_ = data_[data_.vacina_dose_1 < date - timedelta(days=DOSE_OFFSET[vaccine_name])]
    first_dose_count = data_.shape[0]
    if not first_dose_count:
        return None
    second_dose_count = data_.dropna(subset=["vacina_dose_2"])[data_.vacina_dose_2 <= date].shape[0]
    
    return 100 * (first_dose_count - second_dose_count) / first_dose_count

def abandon_series(vaccine_name, date_interval, data):
    begin_date = date_interval[0] + timedelta(days=DOSE_OFFSET[vaccine_name])
    abandon_date_interval = pd.date_range(
        begin_date, datetime.today().date(), freq='d'
    ).date
    ab_df = pd.DataFrame(
        index=abandon_date_interval,
        data=[
            abandon_rate(
                data=data, date=d, vaccine_name=vaccine_name
            ) for d in abandon_date_interval
        ], columns=[vaccine_name]
    )

    return ab_df.dropna(subset=[vaccine_name])


def delay_df(prefix, date_interval):
    delay_df = pd.DataFrame(
        data=numpy.zeros(
            shape=(
                date_interval.shape[0], len(DOSE_OFFSET.keys())
            )
        ), columns=["-".join([prefix, name]) for name in list(DOSE_OFFSET.keys())], index=date_interval
    )
    return delay_df, 0


def delay_series(data, date_interval):
    pos_delay, pos_delay_count = delay_df(prefix="pos", date_interval=date_interval)
    neg_delay, neg_delay_count = delay_df(prefix="neg", date_interval=date_interval)
    nul_delay, nul_delay_count = delay_df(prefix="nul", date_interval=date_interval)

    for d in data.to_dict(orient="records"):
            
        scheduled_date = d["vacina_dose_1"] + timedelta(days=d["vacina_janela"])

        if d["vacina_atraso"] > 0:
            for i in pd.date_range(scheduled_date, d["vacina_dose_2"] - timedelta(days=1), freq='d').date:
                pos_delay.at[i, "pos-" + d["vacina_nome"]] += 1
                pos_delay_count += 1
        elif d["vacina_atraso"] < 0:
            neg_delay.at[d["vacina_dose_2"], "neg-" + d["vacina_nome"]] += 1
            neg_delay_count += 1
        else:
            nul_delay.at[d["vacina_dose_2"], "nul-" + d["vacina_nome"]] += 1
            nul_delay_count += 1

    return pd.concat([neg_delay, nul_delay, pos_delay]), (neg_delay_count, nul_delay_count, pos_delay_count)


def prazo(row):
    if row['vacina_nome']== 'Covid-19-Coronavac-Sinovac/Butantan':
        if row['diferenca'] > 28:
            return True
        else:
            return False
    else:
        if row['diferenca'] > 84:
            return True
        else:
            return False

class Tratamento():
    def __init__(self, df):
        self.df = df.drop_duplicates(subset=['paciente_id', 'vacina_dataAplicacao', 'vacina_descricao_dose'], keep='first').reset_index(drop=True)

    def gera_df_primeira_dose_apenas(self):
        """
        Objeto para gerar dataframe das pessoas que tomaram apenas a primeira dose da vacina
        """
        df = self.df
        df = df.loc[df.duplicated(subset=['paciente_id'], keep=False)==False].reset_index(drop=True)
        df['vacina_dataAplicacao'] = df['vacina_dataAplicacao'].apply(lambda x: datetime.strptime(x[:10], '%Y-%m-%d').date())
        df = df.sort_values(by=['vacina_dataAplicacao'], ascending=True).reset_index(drop=True)
        return df

    def gera_df_duas_doses(self):
        """
        Objeto para gerar dataframe das pessoas que tomaram as duas doses
        """
        df = self.df

        df = df.loc[df.duplicated(subset=['paciente_id'], keep=False)==True].reset_index(drop=True)
        df['vacina_dataAplicacao'] = df['vacina_dataAplicacao'].apply(lambda x: datetime.strptime(x[:10], '%Y-%m-%d'))

        drop_anomalias = df.groupby(['paciente_id']).size().to_frame(name='count').reset_index(drop=False)
        drop_anomalias = drop_anomalias.loc[drop_anomalias['count']==2]

        df = df.loc[df['paciente_id'].isin(drop_anomalias['paciente_id'])]
        df = df.sort_values(by=['paciente_id', 'vacina_dataAplicacao'], ascending=True)

        condicao1 = (df['paciente_id'].isin(df.iloc[::2].loc[df.iloc[::2]['vacina_descricao_dose']=='\xa0\xa0\xa0\xa01ª\xa0Dose']['paciente_id'])) & (df['paciente_id'].isin(df.iloc[1::2].loc[df.iloc[1::2]['vacina_descricao_dose']=='\xa0\xa0\xa0\xa02ª\xa0Dose']['paciente_id']))
        condicao2 = (df['paciente_id'].isin(df.iloc[::2].loc[df.iloc[::2]['vacina_descricao_dose']=='\xa0\xa0\xa0\xa02ª\xa0Dose']['paciente_id'])) & (df['paciente_id'].isin(df.iloc[1::2].loc[df.iloc[1::2]['vacina_descricao_dose']=='\xa0\xa0\xa0\xa01ª\xa0Dose']['paciente_id']))

        df = df.loc[(condicao1) | (condicao2)].sort_values(by=['paciente_id', 'vacina_dataAplicacao'], ascending=True).reset_index(drop=True)

        serie_segunda_dose = df.iloc[1::2]['vacina_dataAplicacao'].reset_index(drop=True)
        df = df.iloc[::2].reset_index(drop=True)
        df['dataSegundaDose'] = serie_segunda_dose
        df['diferenca'] = df['dataSegundaDose'] - df['vacina_dataAplicacao']
        df['diferenca'] = df['diferenca'].apply(lambda x: x.days)

        df['atrasados'] = df.apply(lambda row: prazo(row), axis=1)

        return df

    def gerar_doses_por_dia(self):
        df = self.df
        df['vacina_descricao_dose'] = df['vacina_descricao_dose'].apply(lambda x : x.replace(u'\xa0', u''))
        df['vacina_dataAplicacao'] = df['vacina_dataAplicacao'].apply(lambda x: datetime.strptime(x[:10], '%Y-%m-%d').date())
        df = df.groupby(by=['vacina_descricao_dose', 'vacina_dataAplicacao']).size().to_frame(name='Quantidade').reset_index(drop=False).rename(columns={'vacina_dataAplicacao': 'Data', 'vacina_descricao_dose': 'Dose Aplicada'})
        return df

    def process_source_data(self):
        dataframe = self.df
        dataframe.loc[:, 'vacina_aplicacao'] = dataframe.loc[:, 'vacina_dataAplicacao'].apply(lambda x : x.split('T')[0]).apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
        dataframe.loc[:, 'vacina_dose'] = dataframe.loc[:, 'vacina_descricao_dose'].apply(lambda x : x.replace(u'\xa0', u''))
        dataframe = dataframe[dataframe.columns.drop(["vacina_dataAplicacao", "vacina_descricao_dose"])]
        dataframe.vacina_nome = dataframe.vacina_nome.apply(lambda x: "Covid-19-AstraZeneca" if x == "Vacina Covid-19 - Covishield" else x)

        data = {p_id: {"paciente_id": p_id} for p_id in dataframe.paciente_id}

        for rec in dataframe.to_dict(orient="records"):
            data[rec["paciente_id"]]["vacina_janela"] = DOSE_OFFSET[rec["vacina_nome"]]
            data[rec["paciente_id"]]["vacina_nome"] = rec["vacina_nome"]
            data[rec["paciente_id"]][DATE_COLUMN[rec["vacina_dose"]]] = rec["vacina_aplicacao"]

        data = pandas.DataFrame(data=data.values())

        # ## Importante - tratamento de anomalias
        # 
        # Foram encontrados registros duvidosos onde:
        # 
        # * Não existe data de vacinação para a 1a dose. (3218 registros)
        # * A data de vacinação da segunda dose é anterior ou igual a da primeira. (688 registros)
        anomaly_count = {
            "Sem data da primeira dose":  data[data.vacina_dose_1.isna()].shape[0],
            "Data da primeira dose é maior que data da segunda dose": data[data.vacina_dose_2 <= data.vacina_dose_1].shape[0]
        }

        # Removendo os registros (sem data de 1a dose):
        data = data.dropna(subset=["vacina_dose_1"]).reset_index(drop=True)

        # Removendo registros (data 2a dose anterior ou igual à 1a):
        data = data[data.vacina_dose_1 < data.vacina_dose_2].reset_index(drop=True)

        # Calculando o atraso (em dias) entre a data prevista de aplicação da 2a dose e a data observada:
        data['vacina_atraso'] = data.apply(compute_delay, axis=1).dt.days

        return data

class GeraDados():
    def __init__(self, df):
        self.df_primeira_dose = Tratamento(df=df).gera_df_primeira_dose_apenas()
        self.df_doses_por_dia = Tratamento(df=df).gerar_doses_por_dia()
        self.process_source_data = Tratamento(df=df).process_source_data()

    def gera_demanda(self, **kwargs):
        """
        Objeto para gerar dataframe da demanda contínua total ou por vacina
        
        Parâmetros:
            tipo_vacina (opcional): especificar tipo da vacina entre 'astrazeneca' ou 'coronavac', se não for especificado irá gerar a demanda total 
        """
        df = self.df_primeira_dose
        if 'tipo_vacina' in kwargs:
            tipo_vacina = kwargs.get('tipo_vacina')
            if tipo_vacina == 'astrazeneca' or tipo_vacina == 'covishield':
                df = df.loc[(df['vacina_nome']=='Covid-19-AstraZeneca') | (df['vacina_nome']=='Vacina Covid-19 - Covishield')].reset_index(drop=True)
                df['dataSegundaDose'] = df['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=84))
                df = df.loc[(df['dataSegundaDose']>=pd.Timestamp('today'))].groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
            else:
                df = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df['dataSegundaDose'] = df['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=28))
                df = df.loc[(df['dataSegundaDose']>=pd.Timestamp('today'))].groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
        
        else:
            df_astrazeneca = df.loc[(df['vacina_nome']=='Covid-19-AstraZeneca') | (df['vacina_nome']=='Vacina Covid-19 - Covishield')].reset_index(drop=True)
            df_astrazeneca['dataSegundaDose'] = df_astrazeneca['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=84))
            df_coronavac = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
            df_coronavac['dataSegundaDose'] = df_coronavac['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=28))
            df = pd.concat([df_coronavac, df_astrazeneca]).reset_index(drop=True)
            df = df.loc[df['dataSegundaDose']>=pd.Timestamp('today')].groupby(['dataSegundaDose']).size()
            if df.shape[0]!=0:
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
            else:
                df = pd.DataFrame(columns=['index', 'count'])

        return df

    def gerar_doses_por_dia(self):
        """
        Objeto para gerar quantidade de doses por dia
        """
        return self.df_doses_por_dia

    def gera_serie_atraso(self):
        data = self.process_source_data
        
        # Calculando quantidade de pessoas atrasadas (atraso <, > e = 0) por dia:
        delay_df, (neg, nul, pos) = delay_series(date_interval=date_interval, data=data)

        return delay_df

    def gera_serie_abandono(self):
        data = self.process_source_data
        # Taxa de abandono hoje:
        date = datetime.today().date()
        rate_covac = abandon_rate(data=data, date=date, vaccine_name="Covid-19-Coronavac-Sinovac/Butantan")
        rate_astra = abandon_rate(data=data, date=date, vaccine_name="Covid-19-AstraZeneca")
        
        # Calculando série histórica do abandono vacinal:
        ab_df_covac = abandon_series(vaccine_name="Covid-19-Coronavac-Sinovac/Butantan", date_interval=date_interval, data=data)
        ab_df_astra = abandon_series(vaccine_name="Covid-19-AstraZeneca", date_interval=date_interval, data=data)

        # Série historica abandono
        ab_df = pandas.concat([ab_df_covac, ab_df_astra])

        return ab_df

