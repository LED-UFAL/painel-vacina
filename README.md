# Painel da vacinação Covid-19

Análise e visualização dos dados da vacinação.

Uma iniciativa do [Laboratório de Estatística e Ciência de Dados - LED](https://im.ufal.br/laboratorio/led/).

# Instalação

Baixe ou clone o repositório. Na pasta do painel-vacina:

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    
# Servindo os dados

* Faça download do `.zip` do [conjunto de datasets](https://drive.google.com/drive/folders/1JNnK71nIsvM_6WqZA9gxF3LkHK-3F1JI?usp=sharing).

* Descompacte os arquivos na raiz da pasta do painel-vacina.

* Na pasta datasets, adicione os arquivos `cod_cidades.csv` e `faixas_niveis_2020.zip`, que podem ser baixados em: [arquivos](https://drive.google.com/drive/folders/1XXift4ZZ46zOjcC1RDyY2ZrEjuHv8fdh?usp=sharing)

* Rode os scripts `gera_velocidades.py` e, depois, `gera_dicionario.py`
    
# Executando o painel

Na pasta do painel-vacina: 

    $ python plot.py
    Dash is running on http://127.0.0.1:8050/
    
     * Serving Flask app "plot" (lazy loading)
     * Environment: production
      WARNING: This is a development server. Do not use it in a production deployment.
      Use a production WSGI server instead.
     * Debug mode: on

Acesse [http://127.0.0.1:8050/](http://127.0.0.1:8050/).

# Colaboradores

Adriano Barbosa - FACET/UFGD

Krerley Oliveira - LED/UFAL
