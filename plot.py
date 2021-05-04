# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
import augusto
from dash.dependencies import Input, Output
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Adiciona o script externo
CURRENT_DIR = '/'.join(__file__.split('/')[:-1])
external_scripts = [{'external_url': CURRENT_DIR+'/assets/gtag.js'}]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
server = app.server

mun_list = [
    'BIGUACU', 'ORLEANS', 'CHAPECO', 'BRUSQUE', 'BLUMENAU',
    'FLORIANOPOLIS', 'SAO LOURENCO DO OESTE', 'ITAPEMA', 'ICARA',
    'OTACILIO COSTA', 'SAO JOAQUIM', 'IPUACU', 'BRACO DO NORTE',
    'IRANI', 'RODEIO', "HERVAL D'OESTE", 'ITAIOPOLIS',
    'SAO JOAO DO OESTE', 'MAJOR VIEIRA', 'ILHOTA', 'JARAGUA DO SUL',
    'GASPAR', 'JOSE BOITEUX', 'LAGES', 'IPORA DO OESTE',
    'BALNEARIO CAMBORIU', 'TANGARA', 'CANOINHAS', 'JAGUARUNA',
    'JOINVILLE', 'IMBITUBA', 'TUBARAO', 'RIO DO SUL', 'RIO FORTUNA',
    'SAO JOSE', 'MAFRA', 'ANGELINA', 'VIDEIRA', 'SANGAO',
    'AGUAS FRIAS', 'BOMBINHAS', 'XANXERE', 'LAURO MULLER', 'LAGUNA',
    'AGROLANDIA', 'CUNHA PORA', 'BALNEARIO PICARRAS', 'NAVEGANTES',
    'PORTO UNIAO', 'CACADOR', 'PALHOCA', 'ERVAL VELHO', 'URUBICI',
    'ITAJAI', 'CORONEL FREITAS', 'CRICIUMA', 'SAO BENTO DO SUL',
    'GOVERNADOR CELSO RAMOS', 'RIO NEGRINHO', 'PENHA', 'LEBON REGIS',
    'CAMBORIU', 'MARAVILHA', 'JOACABA', 'BARRA VELHA', 'PALMITOS',
    'ANTONIO CARLOS', 'CURITIBANOS', 'URUSSANGA', 'SANTA ROSA DO SUL',
    'MONTE CARLO', 'INDAIAL', 'SANTA CECILIA', 'CORUPA', 'POMERODE',
    'CAPINZAL', 'SCHROEDER', 'ANITA GARIBALDI', 'SEARA', 'ITA',
    'IOMERE', 'ZORTEA', 'GRAO PARA', 'TREZE DE MAIO', 'TRES BARRAS',
    'NOVA ITABERABA', 'SOMBRIO', 'ARARANGUA', 'RIO RUFINO',
    'ITUPORANGA', 'DIONISIO CERQUEIRA', 'RIQUEZA',
    'BALNEARIO BARRA DO SUL', 'BALNEARIO ARROIO DO SILVA', 'CONCORDIA',
    'AGRONOMICA', 'ROMELANDIA', 'OURO VERDE', 'WITMARSUM',
    'RIO DO OESTE', 'SIDEROPOLIS', 'BOM JARDIM DA SERRA',
    'BENEDITO NOVO', 'ANITAPOLIS', 'MONDAI', 'XAVANTINA', 'AURORA',
    'BALNEARIO GAIVOTA', 'SANTO AMARO DA IMPERATRIZ', 'MONTE CASTELO',
    'SAO PEDRO DE ALCANTARA', 'LUIZ ALVES', 'GARUVA', 'RIO DAS ANTAS',
    'ANCHIETA', 'AGUAS DE CHAPECO', 'LACERDOPOLIS', 'ITAPOA',
    'SAO JOAO BATISTA', 'LAURENTINO', 'PAPANDUVA', 'CAMPOS NOVOS',
    'QUILOMBO', 'MORRO GRANDE', 'MORRO DA FUMACA',
    'SAO JOSE DO CERRITO', 'VIDAL RAMOS', 'MASSARANDUBA',
    'ABELARDO LUZ', 'IPIRA', 'SANTA ROSA DE LIMA', 'VARGEAO',
    'ARMAZEM', 'FAXINAL DOS GUEDES', 'SALETE', 'RIO DOS CEDROS',
    'TIGRINHOS', 'ASCURRA', 'CAMPO BELO DO SUL', 'CAMPO ALEGRE',
    'VITOR MEIRELES', 'GUARAMIRIM', 'FORQUILHINHA', 'PORTO BELO',
    'SAO JOSE DO CEDRO', 'TIMBO', 'ITAPIRANGA', 'POUSO REDONDO',
    'GUARACIABA', 'ATALANTA', 'CATANDUVAS',
    'SANTA TEREZINHA DO PROGRESSO', 'JACINTO MACHADO', 'PERITIBA',
    'SAO MIGUEL DO OESTE', 'ABDON BATISTA', 'TREZE TILIAS', 'SALTINHO',
    'CAPIVARI DE BAIXO', 'CORDILHEIRA ALTA', 'OURO',
    'BOM JESUS DO OESTE', 'TIMBO GRANDE', 'SAO LUDGERO',
    'TIMBE DO SUL', 'ARVOREDO', 'MELEIRO', 'DESCANSO', 'NOVA VENEZA',
    'APIUNA', 'TROMBUDO CENTRAL', 'SAUDADES', 'CELSO RAMOS', 'CAIBI',
    'LONTRAS', 'XAXIM', 'IMARUI', 'SAO MIGUEL DA BOA VISTA',
    'JARDINOPOLIS', 'BRACO DO TROMBUDO', 'CUNHATAI', 'PINHEIRO PRETO',
    'ARAQUARI', 'TIJUCAS', 'SAO CARLOS', 'BALNEARIO RINCAO', 'URUPEMA',
    'RANCHO QUEIMADO', 'IBIRAMA', 'GUARUJA DO SUL', 'PASSOS MAIA',
    'PETROLANDIA', 'SAO CRISTOVAO DO SUL', 'NOVO HORIZONTE', 'TAIO',
    'JUPIA', 'PLANALTO ALEGRE', 'ENTRE RIOS', 'AGUAS MORNAS',
    'CANELINHA', 'AGUA DOCE', 'PAIAL', 'PONTE SERRADA',
    'PRESIDENTE CASTELLO BRANCO', 'PALMA SOLA', 'MODELO',
    'CORREIA PINTO', 'JABORA', 'FRAIBURGO', 'TREVISO', 'BOTUVERA',
    'SANTIAGO DO SUL', 'CAXAMBU DO SUL', 'PASSO DE TORRES', 'LUZERNA',
    'TURVO', 'VARGEM BONITA', 'PINHALZINHO', 'GAROPABA',
    'SANTA TEREZINHA', 'LINDOIA DO SUL', 'COCAL DO SUL',
    'FLOR DO SERTAO', 'NOVA TRENTO', 'UNIAO DO OESTE',
    'SAO JOAO DO SUL', 'SUL BRASIL', 'ALTO BELA VISTA', 'BOM RETIRO',
    'PONTE ALTA DO NORTE', 'PIRATUBA', 'PRAIA GRANDE', 'VARGEM',
    'PRINCESA', 'ALFREDO WAGNER', 'GALVAO', 'MATOS COSTA',
    'SAO BONIFACIO', 'PESCARIA BRAVA', 'PRESIDENTE GETULIO',
    'CAMPO ERE', 'TUNAPOLIS', 'ARROIO TRINTA', 'SANTA HELENA',
    'CHAPADAO DO LAGEADO', 'PARAISO', 'PAINEL', 'RIO DO CAMPO',
    'IMBUIA', 'GRAVATAL', 'BOM JESUS', 'DONA EMMA', 'IPUMIRIM',
    'ARABUTA', 'CERRO NEGRO', 'BELA VISTA DO TOLDO', 'IBICARE',
    'MARACAJA', 'SERRA ALTA', 'CORONEL MARTINS', 'BOCAINA DO SUL',
    'NOVA ERECHIM', 'IRATI', 'IRINEOPOLIS', 'MAJOR GERCINO',
    'GUATAMBU', 'PONTE ALTA', 'PEDRAS GRANDES', 'BANDEIRANTE',
    'CALMON', 'MACIEIRA', 'BELMONTE', 'LEOBERTO LEAL', 'SAO MARTINHO',
    'MIRIM DOCE', 'ERMO', 'MAREMA', 'CAPAO ALTO', 'PALMEIRA',
    'DOUTOR PEDRINHO', 'SALTO VELOSO', 'IBIAM', 'BARRA BONITA',
    'FORMOSA DO SUL', 'PRESIDENTE NEREU', 'PAULO LOPES',
    'SAO DOMINGOS', 'IRACEMINHA', 'FREI ROGERIO', 'BRUNOPOLIS',
    'LAJEADO GRANDE', 'SAO JOAO DO ITAPERIU', 'SAO BERNARDINO',
    'GUABIRUBA', 'SAO FRANCISCO DO SUL'
]

mun_list.sort()

all_options = {
       #'TODOS': ['TODOS'],
       'SC': ['TODOS',]+mun_list}

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
		        value='SC'
		    )
        ], className="one columns"),

        html.Div([
            html.H3('Município'),
            dcc.Dropdown(
		        id='municipio-dropdown',
		    )
        ], className="two columns"),
    ], className="row"),
    html.H3('Doses aplicadas por dia'),
    html.H5('Neste gráfico informamos o número total de doses aplicadas nos últimos dias. As cores representam os diferentes tipos de doses.'),
    html.Div([
                html.H6('Tipo de vacina'),
                dcc.Dropdown(
                    id='tipo-vacina-dropdown',
             options=[
                {'label': 'TODAS', 'value': 'todas'},
                {'label': 'Covid-19-Coronavac-Sinovac/Butantan', 'value': 'coronavac'},
                {'label': 'Covid-19-AstraZeneca', 'value': 'astrazeneca'},
            ],
        )
    ]),
    html.Div(id='mostrar-doses-aplicadas'),
    html.H3('Demanda por dia'),
    html.H5('Neste gráfico informamos o número total de doses necessárias nos próximos dias para cumprir os prazos de vacinação, independente do tipo de vacina.'),
    html.Div(id='mostrar-demanda'),
    html.H3('Demanda por vacina'),
    html.H5('Neste gráfico informamos o número total de doses necessárias nos próximos dias para cumprir os prazos de vacinação, pelo tipo de vacina.'),
    html.Div(id='mostrar-demanda-vacina'),
    html.H3('Atraso de vacinacão'),
    html.H5('Neste gráfico informamos o número total de pessoas que receberam a segunda dose e que estavam com o calendário de vacinação  atrasado em cada dia.'),
    html.Div(id='mostrar-atraso'),
    html.H3('Adiantamento de vacinacão'),
    html.H5('Neste gráfico informamos o número total de pessoas que receberam a segunda dose antes do dia recomendado pelo fabricante da vacina  em cada dia.'),
    html.Div(id='mostrar-adiantamento'),
    html.H3('Taxa de abandono de vacinacão'),
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
    Output('tipo-vacina-dropdown', 'value'),
    Input('tipo-vacina-dropdown', 'options'))
def set_valor_vacina(opcoes_disponiveis):
    return opcoes_disponiveis[0]['value']

@app.callback(
    Output('mostrar-doses-aplicadas', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'),
    Input('tipo-vacina-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada, vacina_selecionada):
    return [
            dcc.Graph(
                id='doses-graph',
                figure=augusto.plotar_doses_por_dia(
                    estado_selecionado, municipio_selecionada, vacina_selecionada
                )
            )]

@app.callback(
    Output('mostrar-demanda', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
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
            dcc.Graph(
                id='abandon-graph',
                figure=augusto.plot_abandon(estado_selecionado, municipio_selecionada)
            )
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
