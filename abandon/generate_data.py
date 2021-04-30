import os

from tqdm import tqdm

from process_data import main as process_data_main
from process_data import process_source_data


if __name__ == "__main__":

    CSV_PATH = "datasets/source_data/AL/dados-vacina.csv"

    dataframe = process_source_data(path=CSV_PATH)

    unique_uf = dataframe.estabelecimento_uf.unique()

    pbar_uf = tqdm(unique_uf, desc="Loop UF")

    for uf in pbar_uf:    
        
        dataframe_ = dataframe[dataframe.estabelecimento_uf == uf]

        if not os.path.exists(os.path.join('datasets', uf)):
            os.mkdir(os.path.join('datasets', uf))

        if not os.path.exists(os.path.join('datasets', uf, 'abandono-atraso-vacinal"')):
            os.mkdir(os.path.join('datasets', uf, 'abandono-atraso-vacinal"'))

        dest_vis_dir = f"datasets/{uf}/abandono-atraso-vacinal"

        pbar = tqdm(dataframe_.estabelecimento_municipio_nome.unique())

        for municipio in pbar:
            
            pbar.set_description(f"Salvando dados para {uf} ... {municipio} ")

            process_data_main(uf=uf, municipio=municipio, dataframe=dataframe_, dest_vis_dir=dest_vis_dir, overwrite=True)
