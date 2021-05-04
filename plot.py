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
from dash.dependencies import Input, Output
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
import os
import time


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

CURRENT_DIR = os.getcwd()
lista_estados = sorted(os.listdir(CURRENT_DIR+'/datasets'))
all_options = {
    item: sorted(os.listdir(CURRENT_DIR+'/datasets/{}/abandono-atraso-vacinal'.format(item))) for item in lista_estados
}
MODIFIED_DIR_DATETIME = datetime.fromtimestamp(os.path.getmtime(os.path.join(CURRENT_DIR, 'datasets'))).strftime("%d de %B de %Y, às %H:%M")

app.layout = html.Div(children=[
    html.H1(children='Painel Vacinação COVID-19'),

    html.Div(children='Iniciativa do Laboratório de Estatística e Ciência de Dados da UFAL.',
        style=dict(fontSize='25px')),
    html.Div(children='Dados coletados em: {}'.format(MODIFIED_DIR_DATETIME),
        style=dict(fontSize='18px')),
    html.Div([
        html.Div([
            html.H4('Estado'),
            dcc.Dropdown(
		        id='estado-dropdown',
		        options=[{'label': k, 'value': k} for k in all_options.keys()],
		        value='BRASIL'
		    )
        ], className="one columns"),

        html.Div([
            html.H4('Município'),
            dcc.Dropdown(
		        id='municipio-dropdown',
		    )
        ], className="two columns"),
    ], className="row", style=dict(display='flex', justifyContent='center')),

    html.H1('Doses aplicadas e atraso vacinal',
        style=dict(display='flex', justifyContent='center')),

    html.Div([
        html.Div([
            html.Div(id='mostrar-doses-aplicadas'),
        ], className="six columns"),

        html.Div([
            html.Div(id='mostrar-atraso'),
        ], className="six columns"),
    ], className="row"),

    html.H1('Demandas por vacina',
        style=dict(display='flex', justifyContent='center')),

    html.Div([
        html.Div([
            html.Div(id='mostrar-demanda'),
        ], className="six columns"),

        html.Div([
            html.Div(id='mostrar-demanda-vacina'),
        ], className="six columns"),
    ], className="row"),

    html.Div(id='mostrar-adiantamento'),
    html.Div(id='mostrar-abandono')
])

@app.callback(
    Output('municipio-dropdown', 'options'),
    Input('estado-dropdown', 'value'))
def set_opcoes_municipios(estado_selecionado):
    return [{'label': i, 'value': i} for i in all_options[estado_selecionado]]

@app.callback(
    Output('municipio-dropdown', 'value'),
    Input('municipio-dropdown', 'options'))
def set_valor_municipio(opcoes_disponiveis):
    return opcoes_disponiveis[0]['value']

@app.callback(
    Output('mostrar-doses-aplicadas', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [html.H3('Doses aplicadas por dia'),
            html.H5('Neste gráfico informamos o número total de doses aplicadas nos últimos dias. As cores representam os diferentes tipos de doses.'),
            dcc.Graph(
                id='doses-graph',
                figure=augusto.plotar_doses_por_dia(
                    estado_selecionado, municipio_selecionada
                )
            )]

@app.callback(
    Output('mostrar-demanda', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Demanda por dia'),
        html.H5('Neste gráfico informamos o número total de doses necessárias nos próximos dias para cumprir os prazos de vacinação, independente do tipo de vacina.'),
            dcc.Graph(
                id='demanda-graph',
                figure=augusto.plotar_demanda_por_dia(estado_selecionado, municipio_selecionada)
            )
    ]

@app.callback(
    Output('mostrar-demanda-vacina', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Demanda por vacina'),
        html.H5('Neste gráfico informamos o número total de doses necessárias nos próximos dias para cumprir os prazos de vacinação, pelo tipo de vacina.'),
            dcc.Graph(
                id='demanda-vacina-graph',
                figure=augusto.plotar_demanda_por_vacina(estado_selecionado, municipio_selecionada)
            )
    ]

@app.callback(
    Output('mostrar-atraso', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Atraso de vacinacão'),
        html.H5('Neste gráfico informamos o número total de pessoas que receberam a segunda dose e que estavam com o calendário de vacinação  atrasado em cada dia.'),
            dcc.Graph(
                id='delay-graph',
                figure=augusto.plot_delay(estado_selecionado, municipio_selecionada, "pos")
            )
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
