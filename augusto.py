import pandas as pd
from plotly import express as px
from datetime import datetime, timedelta
from tqdm import tqdm
import os


def plotar_doses_por_dia(uf='TODOS', municipio='TODOS', grafico='DOSES POR DIA'):
	folder='datasets'
	name = ' '.join([grafico, uf, municipio])
	plotdf = pd.read_csv(os.path.join(folder, name)+'.csv', sep=';')
	fig = px.bar(plotdf, x="Data", y='Quantidade', color="Dose Aplicada", barmode="group",
		title=name)
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


if __name__ == '__main__':
	pass