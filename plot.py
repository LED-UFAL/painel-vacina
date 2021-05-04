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
import os
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

CURRENT_DIR = os.getcwd()
lista_estados = sorted(os.listdir(os.path.join(CURRENT_DIR, 'datasets')))
all_options = {
    item: sorted(os.listdir(CURRENT_DIR+'/datasets/{}/abandono-atraso-vacinal'.format(item))) for item in lista_estados
}

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
		        options=[{'label': k, 'value': k} for k in all_options.keys()],
		        value='AL'
		    )
        ], className="one columns"),

        html.Div([
            html.H3('Município'),
            dcc.Dropdown(
		        id='municipio-dropdown',
		    )
        ], className="two columns"),
    ], className="row"),

    html.Div(id='mostrar-doses-aplicadas'),
    html.Div(id='mostrar-demanda'),
    html.Div(id='mostrar-demanda-vacina'),
    html.Div(id='mostrar-atraso'),
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

@app.callback(
    Output('mostrar-adiantamento', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Adiantamento de vacinacão'),
        html.H5('Neste gráfico informamos o número total de pessoas que receberam a segunda dose antes do dia recomendado pelo fabricante da vacina  em cada dia.'),
            dcc.Graph(
                id='sooner-graph',
                figure=augusto.plot_delay(estado_selecionado, municipio_selecionada, "neg")
            )
    ]

@app.callback(
    Output('mostrar-abandono', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Taxa de abandono de vacinacão'),
            dcc.Graph(
                id='abandon-graph',
                figure=augusto.plot_abandon(estado_selecionado, municipio_selecionada)
            )
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
