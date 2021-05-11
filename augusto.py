import pandas as pd
from plotly import express as px
from plotly import graph_objects as go
from datetime import datetime, timedelta
from tqdm import tqdm
import os

CURRENT_DIR = os.path.dirname(__file__)


def plotar_doses_por_dia(uf='TODOS', municipio='TODOS', vacina='todas', grafico='DOSES POR DIA'):
	## NUMERO TOTAL DE DOSES APLICADA POR DIA <ESTADO>, <CIDADE> (se tiver)
	folder = os.path.join(CURRENT_DIR, 'datasets', uf,'doses_por_dia')
	if vacina=='coronavac':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_coronavac.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		)
	elif vacina=='astrazeneca':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_astrazeneca.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		)
	elif vacina=='pfizer':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_pfizer.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		)
	else:
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		)
	#fig.update_layout(
	#    xaxis_tickformat = '%d/%m/%y'
	#)
	return fig

def plotar_demanda_por_dia(uf='TODOS', municipio='TODOS', grafico='DEMANDA'):
	folder = os.path.join(CURRENT_DIR, 'datasets', uf, 'demanda')
	plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
	fig = px.bar(plotdf, x="index", y='count')

	fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade")
    )
	return fig

def plotar_demanda_por_vacina(uf='TODOS', municipio='TODOS', grafico='DEMANDA POR VACINA'):
	folder = CURRENT_DIR + os.path.join(f'/datasets/{uf}', 'demanda')
	plotdf_astrazeneca = pd.read_csv(os.path.join(folder, municipio)+'_astrazeneca.csv', sep=';')
	plotdf_coronavac = pd.read_csv(os.path.join(folder, municipio)+'_coronavac.csv', sep=';')
	plotdf_pfizer = pd.read_csv(os.path.join(folder, municipio)+'_pfizer.csv', sep=';')
	data = [
		go.Bar(x=plotdf_astrazeneca['index'], y=plotdf_astrazeneca['count'], name='Astrazeneca'),
		go.Bar(x=plotdf_coronavac['index'], y=plotdf_coronavac['count'], name='Coronavac'),
		go.Bar(x=plotdf_pfizer['index'], y=plotdf_pfizer['count'], name='Pfizer')
	]
	fig = go.Figure(data=data)

	fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade")
    )
	return fig


def plot_delay(uf, municipio, prefix):
    path = os.path.join(CURRENT_DIR, "datasets", uf, "abandono-atraso-vacinal", municipio)
    delay_df = pd.read_csv(os.path.join(path, "serie-atraso.csv"), sep=";", index_col=0)
    delay_df.index = delay_df.index.to_series().apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    delay_df = delay_df[[c for c in delay_df.columns if prefix + " - " in c]]
    delay_df.columns = [c.replace(prefix + " - ", "") for c in delay_df.columns]
    fig = px.bar(delay_df, barmode="group")
    fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade"), legend=dict(title="Tipo Vacina")
    )
    return fig


## INDICADORES
def indicadores(uf='TODOS', municipio='TODOS', vacina='todas', grafico='DOSES POR DIA'):
	## NUMERO TOTAL DE DOSES APLICADA POR DIA <ESTADO>, <CIDADE> (se tiver)
	folder = os.path.join(CURRENT_DIR, 'datasets', uf,'doses_por_dia')
	if vacina=='coronavac':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_coronavac.csv', sep=';')
	elif vacina=='astrazeneca':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_astrazeneca.csv', sep=';')
	elif vacina=='pfizer':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_pfizer.csv', sep=';')
	else:
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')

	velocidades = pd.read_csv('datasets/velocidades_doses.csv', sep=';')
	faixas = pd.read_csv('datasets/faixas_niveis_2020_ex.csv', sep=';')

	total = plotdf['Quantidade'].sum()
	qnt_1as_doses = plotdf.loc[plotdf['Dose Aplicada'] == '1ªDose']['Quantidade'].sum()
	qnt_2as_doses = plotdf.loc[plotdf['Dose Aplicada'] == '2ªDose']['Quantidade'].sum()
	date_str = plotdf['Data'].max()
	date = datetime.strptime(date_str, '%Y-%m-%d').date()
	date_minus = date - timedelta(days=30)
	date_minus_str = str(date_minus)

	plotdf = plotdf.loc[(plotdf['Data'] >= date_minus_str) & (plotdf['Data'] <= date_str)]
	media_1as = format(plotdf.loc[plotdf['Dose Aplicada'] == '1ªDose']['Quantidade'].sum()/30, ".2f")
	media_2as = plotdf.loc[plotdf['Dose Aplicada'] == '2ªDose']['Quantidade'].sum()/30

	vel = 1.0
	pop_adultos = 1

	if uf == 'BRASIL':
		vel = velocidades['Velocidade'].min()
		pop_adultos = faixas.loc[faixas['Estado'] == 'TODOS']['Adultos'].sum()

		# print(uf, municipio, vel, pop_adultos)
	elif municipio == 'TODOS':
		vel = velocidades.loc[velocidades['Estado'] == uf]['Velocidade'].min()
		pop_adultos = faixas.loc[(faixas['Estado'] == uf) & (faixas['Municipio'] == municipio)]['Adultos'].sum()
	else:
		vel = velocidades.loc[(velocidades['Estado'] == uf) & (velocidades['Municipio'] == municipio)]['Velocidade'].min()
		pop_adultos = faixas.loc[(faixas['Estado'] == uf) & (faixas['Municipio'] == municipio)]['Adultos'].sum()

	previsao = pop_adultos/vel
	previsao = format(previsao, ".2f")

	# apenas pq o krerley pediu por enquanto
	previsao = format(pop_adultos/media_2as, ".2f")
	media_2as = format(plotdf.loc[plotdf['Dose Aplicada'] == '2ªDose']['Quantidade'].sum()/30, ".2f")

	return total, qnt_1as_doses, qnt_2as_doses, media_1as, media_2as, previsao
