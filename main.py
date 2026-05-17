from functools import reduce
import os
from dotenv import load_dotenv
import requests
from downloader import download_informe
from gemini import PreAuthAgent
from datetime import datetime
import time
from page_edit import use_ia_response 

load_dotenv()

def main():
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

        if field.get("Estado").get('select').get('name') != 'Pendiente':
            continue

        download_informe(field.get("Informe Medico").get('files')[0].get('file').get('url'), item["id"])
        
        cleaned_response.append({
            "ID": item["id"],
            "Procedimiento Sugerido": field.get("Procedimiento Sugerido").get('rich_text')[0].get('text').get('content'),
            "Fecha de Afiliación": field.get("Fecha de Afiliacion").get('date').get('start'),
            "Póliza": seguros.get(field.get("Poliza del Seguro").get('relation')[0].get('id'), "No encontrado"),
            "informe_medico_path": f"informes_descargados/informe_{item['id']}.pdf"
        })

        print(f"DEBUG: Procesado el caso con ID {item['id']} - Procedimiento: {field.get('Procedimiento Sugerido').get('rich_text')[0].get('text').get('content')}")

    agent = PreAuthAgent(api_key=os.getenv("GEMINI_API_KEY"))

    for item in cleaned_response:
        result = agent.process_authorization(
            item_id=item["ID"],
            current_date= datetime.now().strftime("%d de %B de %Y"),
            date_afiliation=item["Fecha de Afiliación"],
            suggested_procedure=item["Procedimiento Sugerido"],
            medical_report_path=item["informe_medico_path"],
            policy_data=item["Póliza"]
        )
        print(f"DEBUG: Resultado de IA para el caso {item['ID']} -> {result}")
        result["page_id"] = item["ID"]
        use_ia_response(result)
        time.sleep(60)

    if os.path.isdir("informes_descargados"):
        for archivo in os.listdir("informes_descargados"):
            ruta_archivo = os.path.join("informes_descargados", archivo)
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)

if __name__ == "__main__":
    main()