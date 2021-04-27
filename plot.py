# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import augusto



df = pd.read_csv('Dados AL.csv', sep=';', low_memory=False)
df['vacina_data_processada'] = df['vacina_dataAplicacao'].apply(lambda x : x.split('T')[0])
df['vacina_data_processada'] = df['vacina_data_processada'].apply(lambda x : datetime.strptime(x, '%Y-%m-%d').date())
df['vacina_descricao_dose'] = df['vacina_descricao_dose'].apply(lambda x : x.replace(u'\xa0', u''))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Painel Vacinação COVID-19'),

    html.Div(children='''
        Iniciativa do Laboratório de Estatística e Ciência de Dados da UFAL.
    '''),

    html.Div([
        html.Div([
            html.H3('Estado'),
            dcc.Dropdown(
		        id='estado-dropdown',
		        options=[
		            {'label': 'TODOS', 'value': 'TODOS'},
		        ],
		        value='TODOS'
		    )
        ], className="one columns"),

        html.Div([
            html.H3('Município'),
            dcc.Dropdown(
		        id='municipio-dropdown',
		        options=[
		            {'label': 'TODOS', 'value': 'TODOS'},
		        ],
		        value='TODOS'
		    )
        ], className="one columns"),
    ], className="row"),

    html.Div([
            html.H3('Doses aplicadas por dia'),
            dcc.Graph(
		        id='doses-graph',
		        figure=augusto.gerar_doses_por_dia(df)
		    )
    ]),

    html.Div([
            html.H3('Abandono vacinal por dia'),
            dcc.Graph(
		        id='Abandono-graph',
		        figure=augusto.gerar_abandono_vacinal(df)
		    )
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)