import json
import requests

from requests.auth import HTTPBasicAuth


def save_data(response_json, filepath):
    
    with open(filepath, "w") as json_file:
        json_file.write(
            json.dumps(response_json, indent=1, ensure_ascii=False)
        )

if __name__ == "__main__":

    username = "imunizacao_public"
    password = "qlto5t&7r_@+#Tlstigi"

    json_request = {
        "size": 10000,
        "query": {
            "match": {
                "estabelecimento_uf": "AL",
            }
        }
    }

    response = requests.post(
        url="https://imunizacao-es.saude.gov.br/_search?scroll=1m",
        json=json_request,
        auth=HTTPBasicAuth(username, password)
    )
    
    response_json = response.json()

    save_data(response_json, filepath="data/AL/al-0.json")
    
    json_request = {}

    json_request["scroll"] = "1m"
    json_request["scroll_id"] = response_json["_scroll_id"]

    page_count = 0
    fetched_count = 10000

    print(f"Fetched {fetched_count} registers - batch 0")

    while response_json["hits"]["hits"]:
        
        page_count += 1

        response = requests.post(
            url="https://imunizacao-es.saude.gov.br/_search/scroll",
            json=json_request,
            auth=HTTPBasicAuth(username, password)
        )
        
        response_json = response.json()
        save_data(response_json, filepath=f"data/AL/al-{page_count}.json")

        fetched_count += len(response_json["hits"]["hits"])

        print(f"Fetched {fetched_count} registers - batch {page_count}")
        json_request["scroll_id"] = response_json["_scroll_id"]
