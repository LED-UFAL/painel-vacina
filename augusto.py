import pandas as pd
from plotly import express as px
from datetime import datetime, timedelta
from tqdm import tqdm


'''df = pd.read_csv('Dados AL.csv', sep=';', low_memory=False)
df['vacina_data_processada'] = df['vacina_dataAplicacao'].apply(lambda x : x.split('T')[0])
df['vacina_data_processada'] = df['vacina_data_processada'].apply(lambda x : datetime.strptime(x, '%Y-%m-%d'))

data = {
	'data': [],
	'quantidade': [],
	'dose': []
}

for date in tqdm(df['vacina_data_processada'].unique()):
	for dose in df['vacina_descricao_dose'].unique():
		data['data'].append(date)
		data['dose'].append(dose)
		loc = (df['vacina_data_processada'] == date) & (df['vacina_descricao_dose'] == dose)
		data['quantidade'].append(len(df.loc[loc]))

plotdf = pd.DataFrame(data=data)

fig = px.bar(plotdf, x="data", y='quantidade', color="dose", barmode="group")
##############################################################################
print(df['vacina_nome'].unique())
dict_abandono = {}

for idx, row in tqdm(df.iterrows()):
	if row['paciente_id'] not in dict_abandono.keys():
		dict_abandono[row['paciente_id']] = 0

	dict_abandono[row['paciente_id']] += 1'''


def gerar_doses_por_dia(df):
	dados = {
	'data': [],
	'quantidade': [],
	'dose': []
	}

	for date in tqdm(df['vacina_data_processada'].unique()):
		for dose in df['vacina_descricao_dose'].unique():
			dados['data'].append(date)
			dados['dose'].append(dose)
			loc = (df['vacina_data_processada'] == date) & (df['vacina_descricao_dose'] == dose)
			dados['quantidade'].append(len(df.loc[loc]))

	plotdf = pd.DataFrame(data=dados)
	fig = px.bar(plotdf, x="data", y='quantidade', color="dose", barmode="group")

	return fig

def gerar_abandono_vacinal(df):
	datas = df['vacina_data_processada'].unique()
	vacinas = df['vacina_nome'].unique()

	dados = {
	'data': [],
	'quantidade': [],
	'vacina': []
	}

	janela_2dose = {
	'Covid-19-AstraZeneca': 84,
	'Vacina Covid-19 - Covishield': 84,
	'Covid-19-Coronavac-Sinovac/Butantan': 28
	}

	dict_abandono = {}

	for idx, row in tqdm(df.iterrows()):
		data = row['vacina_data_processada']
		vacina = row['vacina_nome']
		dose = row['vacina_descricao_dose']

		ndata = data + timedelta(days=janela_2dose[vacina])

		if data not in dict_abandono.keys():
			dict_abandono[data] = {}

		if ndata not in dict_abandono.keys():
			dict_abandono[ndata] = {}

		if vacina not in dict_abandono[data].keys():
			dict_abandono[data][vacina] = 0

		if vacina not in dict_abandono[ndata].keys():
			dict_abandono[ndata][vacina] = 0

		if dose == '1ªDose':
			dict_abandono[ndata][vacina] += 1
		elif dose == '2ªDose':
			dict_abandono[data][vacina] -= 1

	for data,dict_vacinas in dict_abandono.items():
		for vacina,quantidade in dict_vacinas.items():
			if quantidade >= 0:
				dados['data'].append(data)
				dados['vacina'].append(vacina)
				dados['quantidade'].append(quantidade)


	plotdf = pd.DataFrame(data=dados)
	fig = px.bar(plotdf, x="data", y='quantidade', color="vacina", barmode="group")

	return fig


if __name__ == '__main__':
	pass