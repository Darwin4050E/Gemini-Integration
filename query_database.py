import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

url = f"https://api.notion.com/v1/databases/{os.getenv('DATABASE_ID')}"

headers = {
    "Notion-Version": "2026-03-11",
    "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}"
}

response = requests.get(url, headers=headers)

print(json.dumps(response.json(), indent=4))
