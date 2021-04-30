from datetime import datetime, timedelta
import pandas as pd 

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
        df = df.loc[df['vacina_descricao_dose']=='\xa0\xa0\xa0\xa01ª\xa0Dose'].reset_index(drop=True)
        df['vacina_dataAplicacao'] = df['vacina_dataAplicacao'].apply(lambda x: datetime.strptime(x[:10], '%Y-%m-%d'))
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

class GeraDados():
    def __init__(self, df):
        self.df_primeira_dose = Tratamento(df=df).gera_df_primeira_dose_apenas()
        self.df_segunda_dose = Tratamento(df=df).gera_df_duas_doses()

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
            df_astrazeneca = df.loc[df['vacina_nome']!='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
            df_astrazeneca['dataSegundaDose'] = df_astrazeneca['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=84))
            df_coronavac = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
            df_coronavac['dataSegundaDose'] = df_coronavac['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=28))
            df = pd.concat([df_coronavac, df_astrazeneca]).reset_index(drop=True)
            df = df.loc[df['dataSegundaDose']>=pd.Timestamp('today')].groupby(['dataSegundaDose']).size()
            idx = pd.date_range(df.index.min(), df.index.max())
            df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)

        return df

    def gera_abandono(self, **kwargs):
        """
        Objeto para gerar dataframe contínuo de pessoas que tomaram apenas a primeira dose

        Parâmetros:
            tipo_vacina (opcional): especificar tipo da vacina entre 'astrazeneca' ou 'coronavac', se não for especificado irá gerar o abandono total 
        """
        df = self.df_primeira_dose
        if 'tipo_vacina' in kwargs:
            tipo_vacina = kwargs.get('tipo_vacina')
            if tipo_vacina == 'astrazeneca' or tipo_vacina == 'covishield':
                df = df.loc[(df['vacina_nome']=='Covid-19-AstraZeneca') | (df['vacina_nome']=='Vacina Covid-19 - Covishield')].reset_index(drop=True)
                df['dataSegundaDose'] = df['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=84))
                df = df.loc[(df['dataSegundaDose']<pd.Timestamp('today'))].groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
            else:
                df = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df['dataSegundaDose'] = df['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=28))
                df = df.loc[(df['dataSegundaDose']<pd.Timestamp('today'))].groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
        
        else:
            df_astrazeneca = df.loc[df['vacina_nome']!='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
            df_astrazeneca['dataSegundaDose'] = df_astrazeneca['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=84))
            df_coronavac = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
            df_coronavac['dataSegundaDose'] = df_coronavac['vacina_dataAplicacao'].apply(lambda x: x+timedelta(days=28))
            df = pd.concat([df_coronavac, df_astrazeneca]).reset_index(drop=True)
            df = df.loc[df['dataSegundaDose']<pd.Timestamp('today')].groupby(['dataSegundaDose']).size()
            idx = pd.date_range(df.index.min(), df.index.max())
            df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)

        return df

    def gera_imunizados(self, **kwargs):
        """
        Objeto para gerar dataframe de pessoas que tomaram as duas doses dentro do prazo

        Parâmetros:
            tipo_vacina (opcional): especificar tipo da vacina entre 'astrazeneca' ou 'coronavac', se não for especificado irá gerar o total de imunzados 
        """
        df = self.df_segunda_dose
        df = df.loc[df['atrasados']==False].reset_index(drop=True)

        if 'tipo_vacina' in kwargs:
            tipo_vacina = kwargs.get('tipo_vacina')
            if tipo_vacina == 'astrazeneca' or tipo_vacina == 'covishield':
                df = df.loc[df['vacina_nome']!='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df = df.groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
            else:
                df = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df = df.groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)       
        else:
            df = df.groupby(['dataSegundaDose']).size()
            idx = pd.date_range(df.index.min(), df.index.max())
            df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
        
        return df

    def gera_atrasos(self, **kwargs):
        """
        Objeto para gerar dataframe das pessoas que tomaram a segunda dose atrasada

        Parâmetros:
            tipo_vacina (opcional): especificar tipo da vacina entre 'astrazeneca' ou 'coronavac', se não for especificado irá gerar o total de imunzados 
        """
        df = self.df_segunda_dose
        
        df = df.loc[df['atrasados']==True].reset_index(drop=True)
        if 'tipo_vacina' in kwargs:
            tipo_vacina = kwargs.get('tipo_vacina')
            if tipo_vacina == 'astrazeneca' or tipo_vacina == 'covishield':
                df = df.loc[df['vacina_nome']!='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df = df.groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                .cumsum().to_frame(name='count').reset_index(drop=False)
            else:
                df = df.loc[df['vacina_nome']=='Covid-19-Coronavac-Sinovac/Butantan'].reset_index(drop=True)
                df = df.groupby(['dataSegundaDose']).size()
                idx = pd.date_range(df.index.min(), df.index.max())
                df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)       
        else:
            df = df.groupby(['dataSegundaDose']).size()
            idx = pd.date_range(df.index.min(), df.index.max())
            df = df.reindex(idx, fill_value=0).cumsum().to_frame(name='count').reset_index(drop=False)
        
        return df