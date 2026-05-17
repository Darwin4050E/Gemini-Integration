from functools import reduce
import os
from dotenv import load_dotenv
import requests
import json
from downloader import download_informes

load_dotenv()

### CARGANDO BASE DE DATOS SEGUROS

seguros_data_source_url = f"https://api.notion.com/v1/data_sources/{os.getenv('SEGUROSDS_ID')}/query"

payload = {
    "sorts": [],
    "filter": {
        "or": []
    },
}

headers = {
    "Notion-Version": "2026-03-11",
    "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
    "Content-Type": "application/json"
}

response = requests.post(seguros_data_source_url, json=payload, headers=headers)

seguros = {}

for item in response.json()['results']:
    field = item["properties"]

    seguros[item["id"]] = reduce(lambda acc, curr: acc + curr.get("plain_text"), field.get("Póliza").get('rich_text'), "").strip()

### CONSULTANDO BASE DE DATOS CASOS

url = f"https://api.notion.com/v1/data_sources/{os.getenv('DATASOURCE_ID')}/query"

payload = {
    "sorts": [],
    "filter": {
        "or": []
    },
}

headers = {
    "Notion-Version": "2026-03-11",
    "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

cleaned_response = []

for item in response.json()['results']:
    field = item["properties"]

    cleaned_response.append({
        "ID": item["id"],
        "Estado": field.get("Estado").get('select').get('name'),
        "Procedimiento Sugerido": field.get("Procedimiento Sugerido").get('rich_text')[0].get('text').get('content'),
        "informe_medico_link": field.get("Informe Medico").get('files')[0].get('file').get('url'),
        "Fecha de Afiliación": field.get("Fecha de Afiliacion").get('date').get('start'),
        "Poliza": seguros.get(field.get("Poliza del Seguro").get('relation')[0].get('id'), "No encontrado"),
    })

download_informes(cleaned_response)

with open('query_datasource.json', 'w') as f:
    json.dump(response.json(), f, indent=4)