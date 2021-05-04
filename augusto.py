import pandas as pd
from plotly import express as px
from plotly import graph_objects as go
from datetime import datetime, timedelta
from tqdm import tqdm
import os

CURRENT_DIR = '/'.join(__file__.split('/')[:-1])

def plotar_doses_por_dia(uf='TODOS', municipio='TODOS', vacina='TODAS', grafico='DOSES POR DIA'):
	## NUMERO TOTAL DE DOSES APLICADA POR DIA <ESTADO>, <CIDADE> (se tiver)
	folder = CURRENT_DIR + os.path.join(f'/datasets/{uf}', 'doses_por_dia')
	name = grafico + ' - {} - {}'.format(uf, municipio)
	if vacina=='coronavac':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_coronavac.csv', sep=';')
		fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
	elif vacina=='astrazeneca':
		plotdf = pd.read_csv(os.path.join(folder, municipio)+'_astrazeneca.csv', sep=';')
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

#def plotar_doses_por_vacina(uf='TODOS', municipio='TODOS', grafico='DOSES POR DIA'):


def plotar_demanda_por_dia(uf='TODOS', municipio='TODOS', grafico='DEMANDA'):
	folder = CURRENT_DIR + os.path.join(f'/datasets/{uf}', 'demanda')
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
	data = [
		go.Bar(x=plotdf_astrazeneca['index'], y=plotdf_astrazeneca['count'], name='Astrazeneca'),
		go.Bar(x=plotdf_coronavac['index'], y=plotdf_coronavac['count'], name='Coronavac')
	]
	fig = go.Figure(data=data)
	fig.update_layout(
        title=name, xaxis=dict(title="Data"), yaxis=dict(title="Quantidade")
    )
	return fig

def plot_delay(uf, municipio, signal):
	path = CURRENT_DIR + os.path.join(f"/datasets/{uf}/abandono-atraso-vacinal", municipio)
	delay_df = pd.read_csv(os.path.join(path, "serie-atraso.csv"), sep=";", index_col=0)
	delay_df.index = delay_df.index.to_series().apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
	fig = px.bar(delay_df[[c for c in delay_df.columns if signal + "-" in c]], barmode="group")
	fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade"), legend=dict(title="Tipo Vacina")
    )
	return fig

def plot_abandon(uf, municipio):
    path = CURRENT_DIR + '/'+os.path.join(f"/datasets/{uf}/abandono-atraso-vacinal", municipio)
    ab_df = pd.read_csv(os.path.join(path, "serie-abandono.csv"), sep=";", index_col=0)
    ab_df.index = ab_df.index.to_series().apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    fig = px.line(ab_df)
    fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Taxa de abandono"), legend=dict(title="Tipo Vacina")
    )
    return fig


if __name__ == '__main__':
	pass