import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import os


## Função para download do CSV com barra de progresso
def download(url: str, fname: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

CURRENT_DIR = os.path.dirname(__file__)

url = 'https://opendatasus.saude.gov.br/dataset/covid-19-vacinacao/resource/ef3bd0b8-b605-474b-9ae5-c97390c197a8'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

## Pega o div que contêm os links dos CSVs
prose_notes = soup.find_all('div', attrs={'class':'prose notes', 'property':'rdfs:label'})[0]

## Pega todos os links do div onde fica os links dos CSVs
a_tags = prose_notes.find_all('a')

for a_tag in a_tags:
	if a_tag.text == 'Dados Completos':
		filename = os.path.join(CURRENT_DIR, 'base.csv')
		download(a_tag['href'], filename)
		break

## Pega a tabela em que estão os dados relacionado à data
table = soup.find_all('table', attrs={'data-module':'table-toggle-more'})[0]
date_str = table.find_all('tr')[1].find_all('td')[0].text

## Escreve a data em um .txt para ser lido no plot.py
filename = os.path.join(CURRENT_DIR, 'datasets', 'data_date_str.txt')
open(filename, 'w').write(date_str)