from functools import reduce
import os
from dotenv import load_dotenv
import requests
import json
from downloader import download_informe
from gemini import PreAuthAgent
from datetime import datetime
import time
import use_ia_response from page_edit

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
    download_informe(field.get("Informe Medico").get('files')[0].get('file').get('url'), item["id"])
    cleaned_response.append({
        "ID": item["id"],
        "Estado": field.get("Estado").get('select').get('name'),
        "Procedimiento Sugerido": field.get("Procedimiento Sugerido").get('rich_text')[0].get('text').get('content'),
        "informe_medico_link": f"informes_descargados/informe_{item['id']}.pdf",
        "Fecha de Afiliación": field.get("Fecha de Afiliacion").get('date').get('start'),
        "Poliza": seguros.get(field.get("Poliza del Seguro").get('relation')[0].get('id'), "No encontrado"),
    })

gemini_response = []

agent = PreAuthAgent(api_key=os.getenv("GEMINI_API_KEY"))

for item in cleaned_response:
    result = agent.process_authorization(
        item_id=item["ID"],
        current_date= datetime.now().strftime("%d de %B de %Y"),
        date_afiliation=item["Fecha de Afiliación"],
        suggested_procedure=item["Procedimiento Sugerido"],
        medical_report_path=item["informe_medico_link"],
        policy_data=item["Poliza"]
    )
    gemini_response.append(result)
    time.sleep(60)

for item in gemini_response:
    use_ia_response(item)