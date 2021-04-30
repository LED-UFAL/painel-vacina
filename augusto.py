import pandas as pd
from plotly import express as px
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
	return fig


if __name__ == '__main__':
	pass