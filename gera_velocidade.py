import pandas as pd
import os
from datetime import datetime, timedelta



datasets_folder = 'datasets'

data = {
	'Velocidade': [],
	'Estado': [],
	'Municipio': []
}

for file0 in os.listdir(datasets_folder):
	if not file0.endswith('.txt') and not file0.endswith('velocidades_doses.csv') and not file0.endswith('faixas_niveis_2020_ex.csv') and not file0.endswith('faixas_niveis_2020.zip') and not file0.endswith('cod_cidades.csv') and not file0.endswith('datasus'):
		for file1 in os.listdir(os.path.join(datasets_folder, file0, 'doses_por_dia')):
			if not file1.endswith('_astrazeneca.csv') and not file1.endswith('_coronavac.csv') and not file1.endswith('_pfizer.csv') and not file1.endswith('TODOS.csv'):
				filename = os.path.join(datasets_folder, file0, 'doses_por_dia', file1)
				print(file0, file1)
				plotdf = pd.read_csv(filename, sep=';')

				data['Estado'].append(file0)
				data['Municipio'].append(file1.replace('.csv', ''))
				data['Velocidade']

				date_str = plotdf['Data'].max()
				date = datetime.strptime(date_str, '%Y-%m-%d').date()
				date_minus = date - timedelta(days=30)
				date_minus_str = str(date_minus)

				plotdf = plotdf.loc[(plotdf['Data'] >= date_minus_str) & (plotdf['Data'] <= date_str)]
				media = format(plotdf['Quantidade'].sum()/30, ".2f")

				data['Velocidade'].append(media)


pd.DataFrame(data=data).to_csv('datasets/velocidades_doses.csv', sep=';', index=False)