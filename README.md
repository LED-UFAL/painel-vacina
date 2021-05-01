# Painel da vacinação Covid-19

Análise e visualização dos dados da vacinação.

Uma iniciativa do [Laboratório de Estatística e Ciência de Dados - LED](https://im.ufal.br/laboratorio/led/).

# Instalação

Baixe ou clone o repositório. Na pasta do painel-vacina:

    $ python3 -m venv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    
# Executando o painel

Na pasta do paine-vacina: 

    $ python plot.py
    Dash is running on http://127.0.0.1:8050/
    
     * Serving Flask app "plot" (lazy loading)
     * Environment: production
      WARNING: This is a development server. Do not use it in a production deployment.
      Use a production WSGI server instead.
     * Debug mode: on

Acesse [http://127.0.0.1:8050/](http://127.0.0.1:8050/).
