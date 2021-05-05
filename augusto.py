import pandas as pd
from plotly import express as px
from plotly import graph_objects as go
from datetime import datetime, timedelta
from tqdm import tqdm
import os

CURRENT_DIR = os.getcwd()


def plotar_doses_por_dia(uf='TODOS', municipio='TODOS', vacina='todas', grafico='DOSES POR DIA'):
	## NUMERO TOTAL DE DOSES APLICADA POR DIA <ESTADO>, <CIDADE> (se tiver)
	folder = os.path.join(CURRENT_DIR, 'datasets', uf,'doses_por_dia')
	name = grafico + ' - {} - {}'.format(uf, municipio)
	if vacina=='coronavac':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_coronavac.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
	elif vacina=='astrazeneca':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_astrazeneca.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
	elif vacina=='pfizer':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_pfizer.csv', sep=';')
		print(plotdf.columns)
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
	else:
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
	#fig.update_layout(
	#    xaxis_tickformat = '%d/%m/%y'
	#)
	return fig

def plotar_demanda_por_dia(uf='TODOS', municipio='TODOS', grafico='DEMANDA'):
	folder = os.path.join(CURRENT_DIR, 'datasets', uf, 'demanda')
	name = 'DEMANDA - {} - {}'.format(uf, municipio)
	plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
	fig = px.bar(plotdf, x="index", y='count', title=name)

	fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade")
    )
	return fig

def plotar_demanda_por_vacina(uf='TODOS', municipio='TODOS', grafico='DEMANDA POR VACINA'):
	folder = CURRENT_DIR + os.path.join(f'/datasets/{uf}', 'demanda')
	name = grafico+' - {} - {}'.format(uf, municipio)
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
        title=name, xaxis=dict(title="Data"), yaxis=dict(title="Quantidade")
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
