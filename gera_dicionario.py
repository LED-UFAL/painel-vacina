import pandas as pd
from tqdm import tqdm


faixas = pd.read_csv('datasets/faixas_niveis_2020.zip', sep=';')
codigos = pd.read_csv('datasets/cod_cidades.csv', sep=';')
faixas['Adultos'] = faixas[faixas.columns[8:]].sum(axis=1).values

siglas = {
	11: 'RO',
	12: 'AC',
	13: 'AM',
	14: 'RR',
	15: 'PA',
	16: 'AP',
	17: 'TO',
	21: 'MA',
	22: 'PI',
	23: 'CE',
	24: 'RN',
	25: 'PB',
	26: 'PE',
	27: 'AL',
	28: 'SE',
	29: 'BA',
	31: 'MG',
	32: 'ES',
	33: 'RJ',
	35: 'SP',
	41: 'PR',
	42: 'SC',
	43: 'RS',
	50: 'MS',
	51: 'MT',
	52: 'GO',
	53: 'DF',
}

estado = []
municipio = []
for idx, row in tqdm(faixas.iterrows()):
	if row['CodMun'] == row['CodMun']:
		cod_mun = int(row['CodMun'])
		estado_municipio = codigos.loc[codigos['estabelecimento_municipio_codigo'] == cod_mun][['estabelecimento_municipio_nome','estabelecimento_uf']]
		print(cod_mun)
		try:
			estado.append(estado_municipio['estabelecimento_uf'].values[0])
			municipio.append(estado_municipio['estabelecimento_municipio_nome'].values[0])
		except:
			estado.append(float('NaN'))
			municipio.append(float('NaN'))
	elif row['CodEst'] == row['CodEst']:
		cod_est = int(row['CodEst'])
		estado.append(siglas[cod_est])
		municipio.append('TODOS')
	else:
		estado.append('TODOS')
		municipio.append('TODOS')


print(estado)
print(municipio)
faixas['Estado'] = estado
faixas['Municipio'] = municipio
faixas.to_csv('datasets/faixas_niveis_2020_ex.csv', sep=';', index=False)