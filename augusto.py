import pandas as pd
from plotly import express as px
from datetime import datetime
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


def gerar_doses_por_dia():
	df = pd.read_csv('Dados AL.csv', sep=';', low_memory=False)
	df['vacina_data_processada'] = df['vacina_dataAplicacao'].apply(lambda x : x.split('T')[0])
	df['vacina_data_processada'] = df['vacina_data_processada'].apply(lambda x : datetime.strptime(x, '%Y-%m-%d').date())

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

	return fig


if __name__ == '__main__':
    pass