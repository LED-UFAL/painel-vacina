import os
import argparse

from tqdm import tqdm

from process_data import main as process_data_main
from process_data import process_source_data


if __name__ == "__main__":
    
    """
    Script de geração dos dados de visualização para atraso e taxa de abandono vacinal.
    Para executá-lo no terminal:
    $ python abandon/generate_data.py csv_path='caminho/para/o/arquivo.csv'
    """

    # Lendo os parâmetros de entrada e tratando

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()
    csv_path = args.csv_path.split("=")[1]

    # Lendo o dataframe e construindo a lista de unidades federativas (Loop I)

    dataframe = process_source_data(path=csv_path)
    unique_uf = dataframe.estabelecimento_uf.unique()
    pbar_uf = tqdm(unique_uf, desc="Loop UF")

    for uf in pbar_uf:    

        # Diretório onde serão armazenados os dados da visualização

        if not os.path.exists(os.path.join('datasets', uf)):
            os.mkdir(os.path.join('datasets', uf))
        if not os.path.exists(os.path.join('datasets', uf, 'abandono-atraso-vacinal')):
            os.mkdir(os.path.join('datasets', uf, 'abandono-atraso-vacinal'))
        dest_vis_dir = f"datasets/{uf}/abandono-atraso-vacinal"

        # Filtrando o dataframe para cada UF e processando os dados por município (Loop II)
        
        dataframe_ = dataframe[dataframe.estabelecimento_uf == uf]
        pbar = tqdm(dataframe_.estabelecimento_municipio_nome.unique().tolist() + ["TODOS"])

        for municipio in pbar:
            pbar.set_description(f"Salvando dados para {uf} ... {municipio} ")
            process_data_main(uf=uf, municipio=municipio, dataframe=dataframe_, dest_vis_dir=dest_vis_dir, overwrite=True)
