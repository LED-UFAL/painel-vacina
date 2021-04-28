import os
import json
import pandas

from tqdm import tqdm

FIELD_LIST = [
    "document_id",
    "paciente_idade",
    "paciente_dataNascimento",
    "vacina_dataAplicacao",
    "vacina_descricao_dose",
    "vacina_codigo",
    "vacina_nome",
    "estabelecimento_municipio_nome"
]

RENAME_COLUMNS = [
    "document_id", "paciente_idade", "paciente_nascimento", "vacina_aplicacao", "vacina_dose",
    "vacina_codigo", "vacina_nome", "municipio_nome"
]

def filter_fields(obj, field_list=FIELD_LIST):
        
    filtered_obj = {}
    
    for field in field_list:
        try:
            filtered_obj[field] = obj[field]
        except KeyError:
            filtered_obj[field] = None
    
    return filtered_obj

def transform_data(json_data):
    
    source_data = json_data["hits"]["hits"]
    source_data = [sd["_source"] for sd in source_data]
    
    return [filter_fields(sd) for sd in source_data]

def json_to_dataframe(json_data):
        
    data = transform_data(json_data=json_data)
    data = pandas.DataFrame(data)
    data.columns = RENAME_COLUMNS
    data.vacina_aplicacao = data.vacina_aplicacao.apply(lambda d: d.split('T')[0])
    data.vacina_dose = data.vacina_dose.str.replace(u'\xa0', ' ').str.strip(' ')
    
    return data


if __name__ == "__main__":

    uf_name = "AL"
    source_dir = f"dataset/source_data/{uf_name}"
    dest_dir = f"dataset/processed_data/{uf_name}"

    source_filenames = os.listdir(source_dir)

    pbar = tqdm(source_filenames, desc="Processing json data to csv")

    dataframes = []

    for filename in pbar:
        
        pbar.set_description("Processing json data to csv - " + filename.split('.')[0])
        
        with open(os.path.join(source_dir, filename), 'r') as jfile:
            json_data = json.load(jfile)
        
        dataframes.append(json_to_dataframe(json_data))
        
        del json_data

    pandas.concat(dataframes, ignore_index=True).to_csv(
        os.path.join(dest_dir, f'{uf_name.lower()}-data.csv'), sep=';', index=False
    )
