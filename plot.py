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
import time


locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
server = app.server

CURRENT_DIR = os.path.dirname(__file__)

## Lê o timestamp dos dados, converte para float e traduz para datetime e mostra no dashboard
timestamp = float(open(os.path.join(CURRENT_DIR, 'datasets', 'data_timestamp.txt'), 'r').read())
DATA_DATETIME = datetime.fromtimestamp(timestamp).strftime("%d de %B de %Y, às %H:%M")

## Lê a string com a data coletada na hora de baixar os dados com baixar_csv.py
DATA_DATE_STR = open(os.path.join(CURRENT_DIR, 'datasets', 'data_date_str.txt'), 'r').read()

lista_estados = sorted(os.listdir(os.path.join(CURRENT_DIR, 'datasets')))

all_options = {
    item: ['TODOS']+sorted([mun for mun in os.listdir(os.path.join(CURRENT_DIR, 'datasets', item, 'abandono-atraso-vacinal')) if mun!='TODOS']) for item in lista_estados if item not in ['data_timestamp.txt', 'data_date_str.txt', 'velocidades_doses.csv', 'cod_cidades.csv', 'faixas_niveis_2020.zip', 'faixas_niveis_2020_ex.csv']
}

app.layout = html.Div(children=[
    html.H1(children='Painel Vacinação COVID-19'),

    html.Div(children='Iniciativa do Laboratório de Estatística e Ciência de Dados da UFAL.',
        style=dict(fontSize='25px')),
    html.Div(children="""
        Os gráficos abaixo são interativos. Você pode clicar nas legendas para selecionar as opções, dar zoom
        e selecionar partes dos gráficos, fazer download, fazer comparações interativas ao longo dos eixos, etc.
        """, style=dict(fontSize='18px', marginTop='8px')),
    html.Div(children='Dados coletados em: {}'.format(DATA_DATE_STR),
        style=dict(fontSize='18px', marginTop='8px')),
    html.Div([
        html.Div([
            html.H4('Estado'),
            dcc.Dropdown(
		        id='estado-dropdown',
		        options=[{'label': k, 'value': k} for k in all_options.keys()],
		        value='BRASIL'
		    ), 
        ], className="one columns"),

        html.Div([
            html.H4('Município'),
            dcc.Dropdown(
		        id='municipio-dropdown',
		    )
        ], className="two columns"),
    ], className="row", style=dict(display='flex', justifyContent='center')),

    html.H1('Doses aplicadas e atraso vacinal',
        style=dict(display='flex', justifyContent='center', marginTop='50px', marginBottom='50px')),

    html.Div(id='indicadores'),

    html.Div([
        html.Div([
            html.H3('Doses aplicadas por dia'),
            html.H5('Número total de doses aplicadas nos últimos dias por tipo de vacina. As cores representam os diferentes tipos de doses.'),
            html.H6('Tipo de vacina'),
                dcc.Dropdown(
                    id='tipo-vacina-dropdown',
                    options=[
                        {'label': 'TODAS', 'value': 'todas'},
                        {'label': 'AstraZeneca', 'value': 'astrazeneca'},
                        {'label': 'CoronaVac', 'value': 'coronavac'},
                        {'label': 'Pfizer', 'value': 'pfizer'}],
                    value='todas'
                ),
            html.Div(id='mostrar-doses-aplicadas'),
        ], className="six columns"),

        html.Div([
            html.Div(id='mostrar-atraso'),
        ], className="six columns"),
    ], className="row"),

    html.H1('Demandas por vacina',
        style=dict(display='flex', justifyContent='center', marginTop='50px', marginBottom='50px')),

    html.Div([
        html.Div([
            html.Div(id='mostrar-demanda'),
        ], className="six columns"),

        html.Div([
            html.Div(id='mostrar-demanda-vacina'),
        ], className="six columns"),
    ], className="row"),

    html.H1('Vacinação Precoce e Abandono Vacinal',
        style=dict(display='flex', justifyContent='center',  marginTop='50px', marginBottom='50px')),

    html.Div([
        html.Div([
            html.Div(id='mostrar-adiantamento'),
        ], className="six columns"),

        html.Div([
            html.Div(id='mostrar-abandono'),
        ], className="six columns"),
    ], className="row"),
        dcc.Markdown(
        """
        ### Intervalos para a segunda dose

        |  Tempo | Astrazeneca | CoronaVac |  Pfizer |
        |:------:|:-----------:|:---------:|:-------:|
        | Mínimo |   56 dias   |  14 dias  | 21 dias |
        | Máximo |   84 dias   |  28 dias  | 25 dias |

        ### Observações

        Foram tratadas as seguintes anomalias para a realização das análises:

        * Foram removidas as pessoas cuja 2ª dose foi registrada antes da 1ª dose;
        * Foram removidas as pessoas cuja 1ª dose foi aplicada antes de 2021;
        * Foram removidas as doses informadas mais de uma vez para a mesma pessoa, com mesma data de aplicação;
        * Foram transformadas em 1ª dose as aplicações de 2ª dose correspondentes às pessoas que têm apenas uma dose informada;
        * Foram removidas as pessoas que tomaram doses de vacinas diferentes.

        """
    ),
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
    Input('municipio-dropdown', 'value'),
    Input('tipo-vacina-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada, vacina_selecionada):
    return [
            dcc.Graph(
                id='doses-graph',
                figure=augusto.plotar_doses_por_dia(
                    estado_selecionado, municipio_selecionada, vacina_selecionada)
            )]

@app.callback(
    Output('mostrar-demanda', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'))
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Demanda por dia'),
        html.H5('Número total acumulado de doses necessárias para aplicar a segunda dose somente nas pessoas cujo o prazo máximo '
        'de aplicação vence nos próximos dias.'),
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
        html.H5('Número total acumulado de doses necessárias para aplicar a segunda dose somente nas pessoas cujo o prazo máximo '
        'de aplicação vence nos últimos dias, por tipo de vacina.'),
            dcc.Graph(
                id='demanda-vacina-graph',
                figure=augusto.plotar_demanda_por_vacina(estado_selecionado, municipio_selecionada)
            )
    ]


@app.callback(
    Output('mostrar-atraso', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value')
)
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Atraso de vacinacão'),
        html.H5('Número total de pessoas que receberam a segunda dose e que estavam com o '
                'calendário de vacinação  atrasado em cada dia, de acordo com os períodos mínimos e máximos '
                'recomendados pelos fabricantes de cada vacina listados no fim da página.'),
        dcc.Graph(
            id='delay-graph',
            figure=augusto.plot_delay(estado_selecionado, municipio_selecionada, "Fora do prazo (atrasou)")
        )
    ]


@app.callback(
    Output('mostrar-adiantamento', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value')
)
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Adiantamento de vacinacão'),
        html.H5('Número total de pessoas que receberam a segunda dose antes do dia '
                'recomendado pelo fabricante da vacina  em cada dia.'),
        dcc.Graph(
            id='sooner-graph',
            figure=augusto.plot_delay(estado_selecionado, municipio_selecionada, "Fora do prazo (antecipou)")
        )
    ]


@app.callback(
    Output('mostrar-abandono', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value')
)
def set_display_children(estado_selecionado, municipio_selecionada):
    return [
        html.H3('Abandono da vacinação'),
        html.H5('Número total de pessoas que iniciaram o esquema vacinal (tomaram a '
                'primeira dose) e não concluíram (já deveriam ter tomado a segunda dose).'),
        dcc.Graph(
            id='abandon-graph',
            figure=augusto.plot_delay(estado_selecionado, municipio_selecionada, "Abandono")
        )
    ]

@app.callback(
    Output('indicadores', 'children'),
    Input('estado-dropdown', 'value'),
    Input('municipio-dropdown', 'value'),
    Input('tipo-vacina-dropdown', 'value'))
def indicadores(estado_selecionado, municipio_selecionada, vacina_selecionada):
    total, qnt_1as_doses, qnt_2as_doses, media, previsao = augusto.indicadores(
        estado_selecionado, municipio_selecionada, vacina_selecionada
    )

    r = html.Div([
        html.Div([
            html.H2('Total Aplicado'),
            html.H4(total)
        ], className='two columns'),
        html.Div([
            html.H2('1ª Doses'),
            html.H4(qnt_1as_doses)
        ], className='two columns'),
        html.Div([
            html.H2('2ª Doses'),
            html.H4(qnt_2as_doses)
        ], className='two columns'),
        html.Div([
            html.H2('Média em 30 dias'),
            html.H4(media),
            html.P('Primeiras e segundas doses')
        ], className='three columns'),
        html.Div([
            html.H2('Fim da Vacinação'),
            html.H4('{} dias'.format(previsao)),
        ], className='three columns'),
    ], className="row")

    return r

if __name__ == '__main__':
    app.run_server(debug=True)
