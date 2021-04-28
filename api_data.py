import json
import requests

from requests.auth import HTTPBasicAuth


def save_data(response_json, filepath):
    
    if len(response_json["hits"]["hits"]):

        with open(filepath, "w") as json_file:
            json_file.write(
                json.dumps(response_json, indent=1, ensure_ascii=False)
            )

if __name__ == "__main__":

    username = "imunizacao_public"
    password = "qlto5t&7r_@+#Tlstigi"
    uf_name = "AL"

    json_request = {
        "size": 10000,
        "query": {
            "match": {
                "estabelecimento_uf": uf_name,
            }
        }
    }

    response = requests.post(
        url="https://imunizacao-es.saude.gov.br/_search?scroll=1m",
        json=json_request,
        auth=HTTPBasicAuth(username, password)
    )
    
    response_json = response.json()

    save_data(response_json, filepath=f"dataset/source_data/{uf_name}/{uf_name}-0.json")
    
    json_request = {}

    json_request["scroll"] = "1m"
    json_request["scroll_id"] = response_json["_scroll_id"]

    page_count = 0
    fetched_count = 10000

    print(f"Downloading data for UF-{uf_name} ... batch {page_count} ... fetched {fetched_count} results")

    while response_json["hits"]["hits"]:
        
        page_count += 1

        response = requests.post(
            url="https://imunizacao-es.saude.gov.br/_search/scroll",
            json=json_request,
            auth=HTTPBasicAuth(username, password)
        )
        
        response_json = response.json()
        
        save_data(response_json, filepath=f"dataset/source_data/{uf_name}/{uf_name}-{page_count}.json")

        fetched_count += len(response_json["hits"]["hits"])

        print(f"Downloading data for UF-{uf_name} ... batch {page_count} ... fetched {fetched_count} results")
        
        json_request["scroll_id"] = response_json["_scroll_id"]
    
    print(f"Done. Fetched {fetched_count} results in total.")
