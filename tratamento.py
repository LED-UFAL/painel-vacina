from datetime import datetime, timedelta
import pandas as pd
import numpy

DATE_COLUMN = {
    '1ªDose': "vacina_dose_1",
    '2ªDose': "vacina_dose_2",
}

VACCINE_NAME = {
    "Covid-19-AstraZeneca": "AstraZeneca",
    "Covid-19-Coronavac-Sinovac/Butantan": "CoronaVac",
    "Vacina covid-19 - BNT162b2 - BioNTech/Fosun Pharma/Pfizer": "Pfizer"
}

DOSE_OFFSET = {
    "AstraZeneca": (56, 84),
    "CoronaVac": (14, 28),
    "Pfizer": (21, 25)
}


def empty_df(prefix, date_interval):
    """"
    Creates a zero-entry dataframe indexed by date_interval (datetime.date numpy-array). Columns
    are named with a prefix and represents the time series of values for each type of vaccine.

    :param prefix: String representing the value type that will be stored.
    :param date_interval: Range of the time series to be created. Must be a Numpy array of datetime.date objects.
    :returns: Pandas DataFrame with columns' name prefixed by prefix and all entries equal to zero.
    """
    zero_df = pd.DataFrame(
        data=numpy.zeros(
            shape=(
                date_interval.shape[0], len(DOSE_OFFSET.keys())
            )
        ), columns=[" - ".join([prefix, name]) for name in list(DOSE_OFFSET.keys())], index=date_interval
    )
    return zero_df


def delay_series(data, date_interval):
    """
    Generates delay series by iterating over data and computing, for each day in date_interval, the distribution
    of people who received the 2nd shot among four desired categories (value type).

    :param data: Pandas DataFrame containing vacina_dose_1, vacina_dose_2 and vacina_nome in each row.
    :param date_interval: Range of the time series to be created. Must be a Numpy array of datetime.date objects.
    :returns: Pandas Dataframe with time series for each vaccine type and value type.
    """
    pos_delay = empty_df(prefix="Fora do prazo (atrasou)", date_interval=date_interval)
    neg_delay = empty_df(prefix="Fora do prazo (antecipou)", date_interval=date_interval)
    nul_delay = empty_df(prefix="Dentro do prazo", date_interval=date_interval)
    abandon = empty_df(prefix="Abandono", date_interval=date_interval)

    for i, d in data.iterrows():

        a_min = d["vacina_dose_1"] + timedelta(days=DOSE_OFFSET[d["vacina_nome"]][0])
        a_max = d["vacina_dose_1"] + timedelta(days=DOSE_OFFSET[d["vacina_nome"]][1])

        if not pd.isna(d["vacina_dose_2"]):

            if d["vacina_dose_2"] > a_max:
                for day in pd.date_range(a_max, d["vacina_dose_2"] - timedelta(days=1), freq='d').date:
                    pos_delay.at[day, "Fora do prazo (atrasou) - " + d["vacina_nome"]] += 1
            elif d["vacina_dose_2"] < a_min:
                neg_delay.at[d["vacina_dose_2"], "Fora do prazo (antecipou) - " + d["vacina_nome"]] += 1
            else:
                nul_delay.at[d["vacina_dose_2"], "Dentro do prazo - " + d["vacina_nome"]] += 1
        else:
            if datetime.today().date() > a_max:
                for day in pd.date_range(a_max, datetime.today().date(), freq='d').date:
                    abandon.at[day, "Abandono - " + d["vacina_nome"]] += 1

    return pd.concat([neg_delay, nul_delay, pos_delay, abandon], axis=1)


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
        df = df[['vacina_dataAplicacao', 'vacina_descricao_dose', 'paciente_id', 'vacina_nome']]
        df = df.drop_duplicates(subset=['paciente_id', 'vacina_dataAplicacao', 'vacina_descricao_dose'], keep='first').reset_index(drop=True)
        df['vacina_descricao_dose'] = df['vacina_descricao_dose'].apply(lambda x : x.replace(u'\xa0', u''))
        df['vacina_dataAplicacao'] = df['vacina_dataAplicacao'].apply(lambda x: datetime.strptime(x[:10], '%Y-%m-%d').date())
        df.loc[(df['vacina_dataAplicacao']>=datetime(2020, 12, 31).date()) & (df['vacina_dataAplicacao']<=datetime.today().date())].reset_index(drop=True)
        df = df.loc[(df['vacina_descricao_dose']=='1ªDose') | (df['vacina_descricao_dose']=='2ªDose')].reset_index(drop=True)
        self.df = df

    def gera_df_tratado(self):
        return self.df
        
    def gera_df_primeira_dose_apenas(self):
        """
        Objeto para gerar dataframe das pessoas que tomaram apenas a primeira dose da vacina
        """
        df = self.df
        df = df.loc[df.duplicated(subset=['paciente_id'], keep=False)==False].reset_index(drop=True)
        df = df.sort_values(by=['vacina_dataAplicacao'], ascending=True).reset_index(drop=True)
        return df

    def process_source_data(self):
        dataframe = self.df
        dataframe = dataframe.rename(columns={'vacina_dataAplicacao': 'vacina_aplicacao', 'vacina_descricao_dose': 'vacina_dose'})
        dataframe.vacina_nome = dataframe.vacina_nome.apply(lambda x: "Covid-19-AstraZeneca" if x == "Vacina Covid-19 - Covishield" else x)
        dataframe.vacina_nome = dataframe.vacina_nome.apply(lambda x: VACCINE_NAME[x])
        dataframe = dataframe.drop_duplicates(subset=['paciente_id', 'vacina_dose']).reset_index(drop=True).pivot(index=['paciente_id', 'vacina_nome'], columns='vacina_dose', values='vacina_aplicacao').reset_index(drop=False)
        dataframe = dataframe.rename(columns={'1ªDose': 'vacina_dose_1', '2ªDose': 'vacina_dose_2'})

        # ## Importante - tratamento de anomalias
        # 
        # Foram encontrados registros duvidosos onde:
        # 
        # * Nome da vacina da primeira dose é diferente da primeira
        # * Não existe data de vacinação para a 1a dose.
        # * A data de vacinação da segunda dose é anterior ou igual a da primeira.
        #anomaly_count = {
        #    "Sem data da primeira dose":  data[data.vacina_dose_1.isna()].shape[0],
        #    "Data da primeira dose é maior que data da segunda dose": data[data.vacina_dose_2 <= data.vacina_dose_1].shape[0]
        #}

        # Removendo registros com divergência no nome da vacina
        dataframe = dataframe.loc[dataframe.duplicated(subset=['paciente_id'], keep=False)==False].reset_index(drop=True)

        # Removendo os registros (sem data de 1a dose):
        dataframe = dataframe.dropna(subset=["vacina_dose_1"]).reset_index(drop=True)

        # Removendo registros (data 2a dose anterior ou igual à 1a):
        dataframe = dataframe[(dataframe.vacina_dose_1 < dataframe.vacina_dose_2) | dataframe.vacina_dose_2.isna()].reset_index(drop=True)

        return dataframe

class GeraDados():
    def __init__(self, df):
        self.df_primeira_dose = Tratamento(df=df).gera_df_primeira_dose_apenas()
        self.df_tratado = Tratamento(df=df).gera_df_tratado()
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
                if df.shape[0]!=0:
                    idx = pd.date_range(df.index.min(), df.index.max())
                    df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
                else:
                    df = pd.DataFrame(columns=['index', 'count'])
            else:
                df = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df['dataSegundaDose'] = df['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=28))
                df = df.loc[(df['dataSegundaDose']>=pd.Timestamp('today'))].groupby(['dataSegundaDose']).size()
                if df.shape[0]!=0:
                    idx = pd.date_range(df.index.min(), df.index.max())
                    df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
                else:
                    df = pd.DataFrame(columns=['index', 'count'])
        
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

    def gerar_doses_por_dia(self, **kwargs):
        """
        Objeto para gerar quantidade de doses por dia
        """
        df = self.df_tratado.drop(columns=['paciente_id'])
        if 'tipo_vacina' in kwargs:
            tipo_vacina = kwargs.get('tipo_vacina')
            if tipo_vacina == 'coronavac':
                df = df.loc[df['vacina_nome']=="Covid-19-Coronavac-Sinovac/Butantan"].reset_index(drop=True)
            elif tipo_vacina == 'astrazeneca':
                condicao = (df['vacina_nome']=="Covid-19-AstraZeneca") | (df['vacina_nome']=="Vacina Covid-19 - Covishield")
                df = df.loc[condicao].reset_index(drop=True)
            else:
                condicao = (df['vacina_nome']!="Covid-19-Coronavac-Sinovac/Butantan") & (df['vacina_nome']!="Covid-19-AstraZeneca") & (df['vacina_nome']!="Vacina Covid-19 - Covishield")
                df = df.loc[condicao].reset_index(drop=True)
        df = df.groupby(by=['vacina_descricao_dose', 'vacina_dataAplicacao']).size().to_frame(name='Quantidade').reset_index(drop=False).rename(columns={'vacina_dataAplicacao': 'Data', 'vacina_descricao_dose': 'Dose Aplicada'})
        return df

    def gera_serie_atraso(self):
        data = self.process_source_data
        if data.shape[0]!=0:
            date_interval = pd.date_range(data.vacina_dose_1.min(), datetime.today().date(), freq='d').date
            # Calculando quantidade de pessoas atrasadas (atraso <, > e = 0) por dia:
            delay_df = delay_series(date_interval=date_interval, data=data)
        else:
            delay_df = pd.DataFrame(columns=[tip+item for tip in ['neg-', 'nul-', 'pos-'] for item in DOSE_OFFSET])

        return delay_df
