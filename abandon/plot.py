import os
import pandas
import plotly.express as px

from datetime import datetime

def plot_delay(uf, municipio, signal):

    path = os.path.join(f"datasets/{uf}/abandono-atraso-vacinal", municipio)
    
    delay_df = pandas.read_csv(os.path.join(path, "serie-atraso.csv"), sep=";", index_col=0)

    delay_df.index = delay_df.index.to_series().apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    
    fig = px.bar(delay_df[[c for c in delay_df.columns if signal + "-" in c]], barmode="group")

    fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Quantidade"), legend=dict(title="Tipo Vacina")
    )

    return fig

def plot_abandon(uf, municipio):
    
    path = os.path.join(f"datasets/{uf}/abandono-atraso-vacinal", municipio)
    
    ab_df = pandas.read_csv(os.path.join(path, "serie-abandono.csv"), sep=";", index_col=0)

    ab_df.index = ab_df.index.to_series().apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    
    fig = px.line(ab_df)

    fig.update_layout(
        xaxis=dict(title="Data"), yaxis=dict(title="Taxa de abandono"), legend=dict(title="Tipo Vacina")
    )

    return fig