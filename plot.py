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
from abandon import plot as abandon_plot


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

mun_list = [
    'MACEIO', 'SAO JOSE DA TAPERA', 'MATRIZ DE CAMARAGIBE', 'ATALAIA',
    'DELMIRO GOUVEIA', 'ARAPIRACA', 'MARECHAL DEODORO', 'CORURIPE',
    'IGACI', 'PIACABUCU', 'VICOSA', 'SANTANA DO MUNDAU', 'ROTEIRO',
    'MARIBONDO', 'SAO JOSE DA LAJE', 'PARIPUEIRA', 'FEIRA GRANDE',
    'CAPELA', 'GIRAU DO PONCIANO', 'RIO LARGO', 'MURICI',
    'PORTO CALVO', 'PENEDO', 'SAO LUIS DO QUITUNDE', 'TEOTONIO VILELA',
    'AGUA BRANCA', 'PASSO DE CAMARAGIBE', 'PORTO DE PEDRAS',
    'PORTO REAL DO COLEGIO', 'MATA GRANDE', 'PARICONHA', 'CAJUEIRO',
    'SAO SEBASTIAO', 'MARAVILHA', 'TAQUARANA', 'BELEM', 'TRAIPU',
    'PALMEIRA DOS INDIOS', 'COITE DO NOIA', 'JACARE DOS HOMENS',
    'PIRANHAS', 'BARRA DE SAO MIGUEL', 'LAGOA DA CANOA',
    'SAO MIGUEL DOS CAMPOS', 'BATALHA', 'LIMOEIRO DE ANADIA', 'CANAPI',
    'CAMPO ALEGRE', 'SANTANA DO IPANEMA', 'JUNQUEIRO',
    'SAO MIGUEL DOS MILAGRES', 'SATUBA', 'SAO BRAS',
    'UNIAO DOS PALMARES', 'DOIS RIACHOS', 'FLEXEIRAS', 'IBATEGUARA',
    'OLIVENCA', 'SANTA LUZIA DO NORTE', 'PAO DE ACUCAR',
    'JOAQUIM GOMES', 'INHAPI', 'ANADIA', 'COLONIA LEOPOLDINA',
    'SENADOR RUI PALMEIRA', 'PILAR', 'POCO DAS TRINCHEIRAS',
    'MAR VERMELHO', 'CHA PRETA', 'BARRA DE SANTO ANTONIO',
    'MAJOR ISIDORO', 'CRAIBAS', 'BOCA DA MATA', 'BRANQUINHA',
    "OLHO D'AGUA DAS FLORES", 'ESTRELA DE ALAGOAS', 'JARAMATAIA',
    'FELIZ DESERTO', 'CARNEIROS', 'MINADOR DO NEGRAO', 'QUEBRANGULO',
    'MONTEIROPOLIS', 'MARAGOGI', 'MESSIAS', 'JAPARATINGA',
    'JEQUIA DA PRAIA', 'CAMPESTRE', 'NOVO LINO', 'PALESTINA',
    'OURO BRANCO', 'IGREJA NOVA', 'CAMPO GRANDE', "OLHO D'AGUA GRANDE",
    'COQUEIRO SECO', 'JACUIPE', 'CACIMBINHAS', 'BELO MONTE',
    "OLHO D'AGUA DO CASADO", "TANQUE D'ARCA", 'JUNDIA',
    'PAULO JACINTO', 'PINDOBA'
]

mun_list.sort()

all_options = {
       #'TODOS': ['TODOS'],
       'AL': ['TODOS',]+mun_list}

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
            dcc.Graph(
                id='doses-graph',
                figure=augusto.plotar_doses_por_dia(estado_selecionado, municipio_selecionada)
            )]

@app.callback(
    Output('mostrar-demanda', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Demanda por dia'),
            dcc.Graph(
                id='demanda-graph',
                figure=augusto.plotar_demanda_por_dia(estado_selecionado, municipio_selecionada)
            )
    ]

@app.callback(
    Output('mostrar-atraso', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Atraso vacinacao'),
            dcc.Graph(
                id='delay-graph',
                figure=abandon_plot.plot_delay(estado_selecionado, municipio_selecionada, "pos")
            )
    ]

@app.callback(
    Output('mostrar-adiantamento', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Adiantamento vacinacao'),
            dcc.Graph(
                id='sooner-graph',
                figure=abandon_plot.plot_delay(estado_selecionado, municipio_selecionada, "neg")
            )
    ]

@app.callback(
    Output('mostrar-abandono', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Taxa abandono vacinacao'),
            dcc.Graph(
                id='abandon-graph',
                figure=abandon_plot.plot_abandon(estado_selecionado, municipio_selecionada)
            )
    ]

if __name__ == '__main__':
    app.run_server(debug=True)