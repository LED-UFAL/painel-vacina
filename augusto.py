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


if __name__ == '__main__':
	pass