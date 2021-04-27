import requests
from bs4 import BeautifulSoup


url = 'https://dados.gov.br/dataset/covid-19-vacinacao/resource/ef3bd0b8-b605-474b-9ae5-c97390c197a8'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
prose_notes = soup.find_all('div', attrs={'class':'prose notes', 'property':'rdfs:label'})[0]
a_tags = prose_notes.find_all('a')

for a_tag in a_tags:
	if a_tag.text == 'Dados AL':
		r = requests.get(a_tag['href'])
		open('Dados AL.csv', 'wb').write(r.content)
		break