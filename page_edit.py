import os
from dotenv import load_dotenv
import requests

load_dotenv()

def use_ia_response(response):
    status_dict = {
        "RECHAZADO": "9183b58f-8208-4dd0-a8a2-d4ca80b5b884",
        "PREAPROBADO": "81a26fb4-7234-45b4-b169-d940cf2250b1",
        "PENDIENTE": "90c57792-09db-4576-b58e-70b8df146350"
    }

    status_id = status_dict.get(response.get("estado"), "81a26fb4-7234-45b4-b169-d940cf2250b1")

    if status_id == status_dict["PENDIENTE"]:
        return
    
    page_id = response.get("page_id")

    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {
        "parent": {
            "data_source_id": os.getenv('DATASOURCE_ID'),
        },
        "properties": {
            "Estado": {
                "select": {
                    "id": status_id
                }
            },
            "Respuesta IA": {
                "rich_text": [
                    {
                        "text": {
                            "content": response.get("justificacion", "")
                        }
                    }
                ]
            }
        }
    }

    headers = {
        "Notion-Version": "2026-03-11",
        "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
        "Content-Type": "application/json"
    }

    response = requests.patch(url, json=payload, headers=headers)