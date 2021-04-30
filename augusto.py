import pandas as pd
from plotly import express as px
from plotly import graph_objects as go
from datetime import datetime, timedelta
from tqdm import tqdm
import os


def plotar_doses_por_dia(uf='TODOS', municipio='TODOS', grafico='DOSES POR DIA'):
	## NUMERO TOTAL DE DOSES APLICADA POR DIA <ESTADO>, <CIDADE> (se tiver)
	folder='datasets/{}/doses_por_dia/'.format(uf)
	name = grafico + ' - {} - {}'.format(uf, municipio)
	plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
	fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
	#fig.update_layout(
	#    xaxis_tickformat = '%d/%m/%y'
	#)
	return fig

def plotar_demanda_por_dia(uf='TODOS', municipio='TODOS', grafico='DEMANDA'):
	folder='datasets/{}/demanda/'.format(uf)
	name = 'DEMANDA - {} - {}'.format(uf, municipio)
	plotdf = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
	fig = px.bar(plotdf, x="index", y='count', title=name)

	fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade")
    )
	return fig

def plotar_demanda_por_vacina(uf='TODOS', municipio='TODOS', grafico='DEMANDA POR VACINA'):
	folder='datasets/{}/demanda/'.format(uf)
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


if __name__ == '__main__':
	pass