import os
import json
import argparse

import numpy
import pandas
import plotly.express as px

from tqdm import tqdm
from datetime import datetime, timedelta


FIELD_LIST = [
    "paciente_id",
    "paciente_idade",
    "vacina_dataAplicacao",
    "vacina_descricao_dose",
    "vacina_nome",
    "estabelecimento_municipio_nome"
]

DATE_COLUMN = {
    1: "vacina_dose_1",
    2: "vacina_dose_2"
}

DOSE_OFFSET = {
    "Covid-19-AstraZeneca": 84,
    "Covid-19-Coronavac-Sinovac/Butantan": 28
}


def process_source_data(path):

    dataframe = pandas.read_csv(path, sep=";")

    dataframe = dataframe[FIELD_LIST]

    dataframe.loc[:, 'vacina_aplicacao'] = dataframe.loc[:, 'vacina_dataAplicacao'].apply(lambda x : x.split('T')[0]).apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    dataframe.loc[:, 'vacina_dose'] = dataframe.loc[:, 'vacina_descricao_dose'].apply(lambda x : x.replace(u'\xa0', u''))

    dataframe = dataframe[dataframe.columns.drop(["vacina_dataAplicacao", "vacina_descricao_dose"])]

    dataframe.vacina_nome = dataframe.vacina_nome.apply(lambda x: "Covid-19-AstraZeneca" if x == "Vacina Covid-19 - Covishield" else x)

    return dataframe

def compute_delay(row):
    if pandas.isna(row["vacina_dose_2"]) or pandas.isna(row["vacina_dose_1"]):
        return None
    return row["vacina_dose_2"] - (row["vacina_dose_1"] + timedelta(days=row["vacina_janela"]))

def abandon_rate(data, date, vaccine_name):
    
    data_ = data[data.vacina_nome == vaccine_name].reset_index(drop=True)
    
    data_ = data_[data_.vacina_dose_1 < date - timedelta(days=DOSE_OFFSET[vaccine_name])]
    
    first_dose_count = data_.shape[0]
    
    if not first_dose_count:
        return None
    
    second_dose_count = data_.dropna(subset=["vacina_dose_2"])[data_.vacina_dose_2 <= date].shape[0]
    
    return 100 * (first_dose_count - second_dose_count) / first_dose_count

def abandon_series(vaccine_name, date_interval, data):

    begin_date = date_interval[0] + timedelta(days=DOSE_OFFSET[vaccine_name])

    abandon_date_interval = pandas.date_range(
        begin_date, datetime.today().date(), freq='d'
    ).date

    ab_df = pandas.DataFrame(
        index=abandon_date_interval,
        data=[
            abandon_rate(
                data=data, date=d, vaccine_name=vaccine_name
            ) for d in abandon_date_interval
        ], columns=[vaccine_name]
    )

    return ab_df.dropna(subset=[vaccine_name])


def delay_df(prefix, date_interval):
    delay_df = pandas.DataFrame(
        data=numpy.zeros(
            shape=(
                date_interval.shape[0], len(DOSE_OFFSET.keys())
            )
        ), columns=["-".join([prefix, name]) for name in list(DOSE_OFFSET.keys())], index=date_interval
    )
    return delay_df, 0


def delay_series(data, date_interval):

    pos_delay, pos_delay_count = delay_df(prefix="pos", date_interval=date_interval)
    neg_delay, neg_delay_count = delay_df(prefix="neg", date_interval=date_interval)
    nul_delay, nul_delay_count = delay_df(prefix="nul", date_interval=date_interval)

    for d in data.to_dict(orient="records"):
            
        scheduled_date = d["vacina_dose_1"] + timedelta(days=d["vacina_janela"])

        if d["vacina_atraso"] > 0:
            for i in pandas.date_range(scheduled_date, d["vacina_dose_2"] - timedelta(days=1), freq='d').date:
                pos_delay.at[i, "pos-" + d["vacina_nome"]] += 1
                pos_delay_count += 1
        elif d["vacina_atraso"] < 0:
            neg_delay.at[d["vacina_dose_2"], "neg-" + d["vacina_nome"]] += 1
            neg_delay_count += 1
        else:
            nul_delay.at[d["vacina_dose_2"], "nul-" + d["vacina_nome"]] += 1
            nul_delay_count += 1

    return pandas.concat([neg_delay, nul_delay, pos_delay]), (neg_delay_count, nul_delay_count, pos_delay_count)


def main(uf, municipio, dataframe, dest_vis_dir, plot_figures=False, overwrite=False):

    dest_dir = os.path.join(dest_vis_dir, municipio)

    if not os.path.exists(dest_vis_dir):
        os.mkdir(dest_vis_dir)

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    else:
        if not overwrite:
            raise RuntimeError(f"Diretório para {uf}...{municipio} já existe em datasets. Para sobrescrever os dados adicione o parâmetro --overwrite=true")

    # # Preparação dos dados

    dataframe = dataframe.copy()

    # Filtra a tabela pelo município passado

    if not municipio in dataframe.estabelecimento_municipio_nome.unique():
        raise ValueError(f"Municipio {municipio} não encontrado na tabela!")

    dataframe = dataframe[dataframe.estabelecimento_municipio_nome == municipio]

    # Criando o intervalo de visualização dos dados (data da primeira aplicação até hoje):

    date_interval = pandas.date_range(dataframe.vacina_aplicacao.min(), datetime.today().date(), freq='d').date

    # Convertendo a coluna `paciente_id` para _tokens_ inteiros:

    paciente_id_tokens = {
        value: i for i, value in enumerate(dataframe.paciente_id.unique())
    }

    dataframe.loc[:, "paciente_id"] = dataframe.paciente_id.apply(lambda d: paciente_id_tokens[d])

    # Convertendo a coluna `vacina_dose` para _tokens_ inteiros:

    dataframe.loc[:, "vacina_dose"] = dataframe.vacina_dose.apply(lambda d: 1 if d == "1ªDose" else 2)

    # # Transformação dos dados

    # Transformando o `dataframe` para uma forma mais reduzida. Cada linha representará um único paciente:

    data = {p_id: {"paciente_id": p_id} for p_id in dataframe.paciente_id}

    for rec in dataframe.to_dict(orient="records"):
        data[rec["paciente_id"]]["vacina_janela"] = DOSE_OFFSET[rec["vacina_nome"]]
        data[rec["paciente_id"]]["vacina_nome"] = rec["vacina_nome"]
        data[rec["paciente_id"]][DATE_COLUMN[rec["vacina_dose"]]] = rec["vacina_aplicacao"]

    data = pandas.DataFrame(data=data.values())

    # ## Importante - tratamento de anomalias
    # 
    # Foram encontrados registros duvidosos onde:
    # 
    # * Não existe data de vacinação para a 1a dose. (3218 registros)
    # * A data de vacinação da segunda dose é anterior ou igual a da primeira. (688 registros)

    anomaly_count = {
        "Sem data da primeira dose":  data[data.vacina_dose_1.isna()].shape[0],
        "Data da primeira dose é maior que data da segunda dose": data[data.vacina_dose_2 <= data.vacina_dose_1].shape[0]
    }

    # Removendo os registros (sem data de 1a dose):

    data = data.dropna(subset=["vacina_dose_1"]).reset_index(drop=True)

    # Removendo registros (data 2a dose anterior ou igual à 1a):

    data = data[data.vacina_dose_1 < data.vacina_dose_2].reset_index(drop=True)

    # Calculando o atraso (em dias) entre a data prevista de aplicação da 2a dose e a data observada:

    data['vacina_atraso'] = data.apply(compute_delay, axis=1).dt.days

    # Distribuição do atraso:

    if plot_figures:

        fig = px.histogram(data, x="vacina_atraso", opacity=.8)
        fig.show()

    # Taxa de abandono hoje:

    date = datetime.today().date()

    rate_covac = abandon_rate(data=data, date=date, vaccine_name="Covid-19-Coronavac-Sinovac/Butantan")
    rate_astra = abandon_rate(data=data, date=date, vaccine_name="Covid-19-AstraZeneca")

    if plot_figures:

        print(25*"=" + " " + " ... ".join([uf, municipio]) + " " +  25*"=")

        print("Taxa de abandono vacinal Covid-19-Coronavac-Sinovac/Butantan em %s ... %.4f%%" % (str(date), rate_covac))
        print("Taxa de abandono vacinal Covid-19-AstraZeneca em %s ... %.4f%%" % (str(date), rate_astra))

    # Calculando série histórica do abandono vacinal:

    ab_df_covac = abandon_series(vaccine_name="Covid-19-Coronavac-Sinovac/Butantan", date_interval=date_interval, data=data)
    ab_df_astra = abandon_series(vaccine_name="Covid-19-AstraZeneca", date_interval=date_interval, data=data)

    # Série historica abandono

    ab_df = pandas.concat([ab_df_covac, ab_df_astra])

    ab_df.to_csv(os.path.join(dest_dir, "serie-abandono.csv"), sep=";")

    if plot_figures:

        fig = px.line(ab_df)
        fig.show()

    # Calculando quantidade de pessoas atrasadas (atraso <, > e = 0) por dia:
    
    delay_df, (neg, nul, pos) = delay_series(date_interval=date_interval, data=data)

    delay_df.to_csv(os.path.join(dest_dir, "serie-atraso.csv"), sep=";")

    with open(os.path.join(dest_dir, "resumo.json"), "w") as jfile:

        summary = {
            "anomalias": anomaly_count,
            "Tomaram a segunda dose antes do dia planejado": neg,
            "Tomaram a segunda dose no dia planejado": nul,
            "Tomaram a segunda dose após o dia planejado": pos
        }

        jfile.write(json.dumps(summary, indent=1, ensure_ascii=False))

    if plot_figures:

        print(f"Pessoas que tomaram a segunda dose com atraso = {pos}")

        fig = px.bar(delay_df[[c for c in delay_df.columns if "pos-" in c]], barmode="group")
        fig.show()

    if plot_figures:

        print(f"Pessoas que tomaram a segunda dose com antecedência = {neg}")

        fig = px.bar(delay_df[[c for c in delay_df.columns if "neg-" in c]], barmode="group")
        fig.show()

    if plot_figures:

        print(f"Pessoas que tomaram a segunda dose no dia agendado = {nul}")

        fig = px.bar(delay_df[[c for c in delay_df.columns if "nul-" in c]], barmode="group")
        fig.show()

    if plot_figures:

        print(25*"=" + " " + " ... ".join([uf, municipio]) + " " +  25*"=")


if __name__ == "__main__":

    # Lendo os parâmetros e tratando

    parser = argparse.ArgumentParser()
    
    parser.add_argument("uf")
    parser.add_argument("municipio")
    parser.add_argument("--plot_figures", default="false", choices=["true", "false"])
    parser.add_argument("--overwrite", default="false", choices=["true", "false"])

    args = parser.parse_args()

    uf = args.uf.split('=')[1]
    municipio = args.municipio.split("=")[1]

    plot_figures = True if args.plot_figures == "true" else False
    overwrite = True if args.overwrite == "true" else False

    # Carregando o dataframe e processando

    dataframe = process_source_data(path=f"datasets/source_data/{uf}/dados-vacina.csv")

    # fim do processamento do dataframe

    dest_vis_dir = f"datasets/{uf}/abandono-atraso-vacinal"

    main(
        uf=uf, municipio=municipio, dataframe=dataframe,
        dest_vis_dir=dest_vis_dir, plot_figures=plot_figures, overwrite=overwrite
    )
