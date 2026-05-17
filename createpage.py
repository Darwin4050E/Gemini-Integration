import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

url = f"https://api.notion.com/v1/pages"

payload = {
    "parent": {
        "data_source_id": os.getenv('DATASOURCE_ID'),
    },
    "properties": {
        "Name": {
            "title": [{
                "text": {
                    "content": "ñañela"
                }
            }]
        },
        "Text": {
            "rich_text": [{
                "text": {
                    "content": "equisde"
                }
            }]
        },
        "Select": {
            "select": {
                "id": "9ccb1947-69de-4420-bbfa-41fedea614f8",
                "color": "purple"
            }
        },
        "Number": { "number": 55 }
    },
}

headers = {
    "Notion-Version": "2026-03-11",
    "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(json.dumps(response.json(), indent=4))