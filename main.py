import json
import requests

from requests.auth import HTTPBasicAuth


def save_data(response_json, filepath):
    
    print("Found %d" % (len(response_json["hits"]["hits"]),))

    with open(filepath, "w") as json_file:
        json_file.write(
            json.dumps(response_json, indent=1, ensure_ascii=False)
        )

if __name__ == "__main__":

    username = "imunizacao_public"
    password = "qlto5t&7r_@+#Tlstigi"

    json_request = {
        "size": 100,
        "query": {
            "match": {
                "paciente_endereco_uf": "AL",
            }
        },
        "query": {
            "match": {
                "paciente_endereco_nmMunicipio": "MACEIO"
            }
        }
    }

    response = requests.post(
        url="https://imunizacao-es.saude.gov.br/_search",
        json=json_request,
        auth=HTTPBasicAuth(username, password)
    )

    save_data(response.json(), filepath="data/al-maceio.json")