import pandas as pd
from plotly import express as px
from plotly import graph_objects as go
from datetime import datetime, timedelta
from tqdm import tqdm
import os
from math import ceil

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

def plotar_cobertura(uf='TODOS', municipio='TODOS'):
	sample_multiply = 1 # Produção
	# sample_multiply = 100 # Testes

	folder = os.path.join(CURRENT_DIR, 'datasets', uf, 'cobertura')
	dfFinal = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
	dfFinal = dfFinal.set_index(['Sexo', 'Dose', 'Faixa'])

	women_bins = dfFinal.loc[('F', '1ªDose'), 'Total'] * -1
	men_bins = dfFinal.loc[('M', '1ªDose'), 'Total']

	y = dfFinal.index.get_level_values(2).unique()

	layout = go.Layout(title='Cobertura vacinal',
					   yaxis=go.layout.YAxis(title='Faixa etária'),
					   xaxis=go.layout.XAxis(
						   # range=[-10000000, 10000000],
						   # tickvals=[-10000000, -5000000, 0, 5000000, 10000000],
						   # ticktext=['10M', '5M', 0, '5M', '10M'],
						   showticklabels=False,
						   title='Mulheres X Homens'),
					   barmode='overlay',
					   bargap=0.1)
	data=[]
	data = [go.Bar(y=y,
				   x=men_bins,
				   orientation='h',
				   name='População',
				   hoverinfo='x',
				   hovertemplate='%{x:,}<extra></extra>',
				   marker=dict(color='powderblue')
				   ),
			go.Bar(y=y,
				   x=women_bins,
				   orientation='h',
				   showlegend=False,
				   text=-1 * women_bins.astype('int'),
				   hoverinfo='x',
				   hovertemplate='%{text:,}<extra></extra>',
				   marker=dict(color='powderblue')
				   )]

	if len(dfFinal.index.get_level_values(1).unique()) >= 1:
		women_vac_bins = dfFinal.loc[('F', '1ªDose'), 'Vacinados'] * -1 * sample_multiply
		men_vac_bins = dfFinal.loc[('M', '1ªDose'), 'Vacinados'] * sample_multiply

		data = data + [
			go.Bar(y=y,
				   x=men_vac_bins,
				   orientation='h',
				   name='1a Dose',
				   hoverinfo='x',
				   hovertemplate='%{x:,}<extra></extra>',
				   opacity=0.5,
				   marker=dict(color='teal')
				   ),
			go.Bar(y=y,
				   x=women_vac_bins,
				   orientation='h',
				   text=-1 * women_vac_bins.astype('int'),
				   hoverinfo='x',
				   hovertemplate='%{text:,}<extra></extra>',
				   showlegend=False,
				   opacity=0.5,
				   marker=dict(color='teal')
				   )]

	if len(dfFinal.index.get_level_values(1).unique()) == 2:
		women_vac2_bins = dfFinal.loc[('F', '2ªDose'), 'Vacinados'] * -1 * sample_multiply
		men_vac2_bins = dfFinal.loc[('M', '2ªDose'), 'Vacinados'] * sample_multiply

		data = data + [
			go.Bar(y=y,
				   x=men_vac2_bins,
				   orientation='h',
				   name='2a Dose',
				   hoverinfo='x',
				   hovertemplate='%{x:,}<extra></extra>',
				   opacity=0.75,
				   marker=dict(color='seagreen')
				   ),
			go.Bar(y=y,
				   x=women_vac2_bins,
				   orientation='h',
				   text=-1 * women_vac2_bins.astype('int'),
				   hoverinfo='x',
				   hovertemplate='%{text:,}<extra></extra>',
				   showlegend=False,
				   opacity=0.75,
				   marker=dict(color='seagreen')
				   )]
	fig = go.Figure(data=data, layout=layout)
	return fig

def plotar_cobertura_total(uf='TODOS', municipio='TODOS'):
	sample_multiply = 1 # Produção
	# sample_multiply = 100 # Testes

	folder = os.path.join(CURRENT_DIR, 'datasets', uf, 'cobertura')
	dfFinal = pd.read_csv(os.path.join(folder, municipio)+'.csv', sep=';')
	dfFinal = dfFinal.set_index(['Sexo', 'Dose', 'Faixa'])

	dfTotal = dfFinal.groupby(level=[1]).sum()

	duas_doses = dfTotal.loc['2ªDose', 'Vacinados'] * sample_multiply
	uma_dose = (dfTotal.loc['1ªDose', 'Vacinados'] * sample_multiply) - duas_doses
	nao_vacinados = dfTotal.loc['1ªDose', 'Total'] - uma_dose
	fig = px.pie(values=[uma_dose, duas_doses, nao_vacinados] , names=['Uma dose', 'Duas doses', 'Não vacinados'],
				 title='Cobertura total')
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
	media_1as = ceil(plotdf.loc[plotdf['Dose Aplicada'] == '1ªDose']['Quantidade'].sum()/30)
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
	previsao = ceil((0.8*pop_adultos-qnt_2as_doses)/media_2as)
	media_2as = ceil(plotdf.loc[plotdf['Dose Aplicada'] == '2ªDose']['Quantidade'].sum()/30)

	translate_dict = {'Janeiro':1, 'Fevereiro':2, 'Março':3, 'Abril':4, 'Maio':5, 'Junho':6, 'Julho':7, 'Agosto':8, 'Setembro':9, 'Outubro':10, 'Novembro':11, 'Dezembro':12}
	DATA_DATE_STR = open(os.path.join(CURRENT_DIR, 'datasets', 'data_date_str.txt'), 'r').read()
	DATA_DATE_STR = DATA_DATE_STR.split('/')
	day = int(DATA_DATE_STR[0])
	month = translate_dict[DATA_DATE_STR[1]]
	year = int(DATA_DATE_STR[2])
	previsao = datetime(day=day, month=month, year=year).date() + timedelta(days=previsao)

	return total, qnt_1as_doses, qnt_2as_doses, media_1as, media_2as, previsao.strftime("%d/%m/%Y")
