import requests
import json

WEBHOOK_URL = "https://discord.com/api/webhooks/1185281754316148867/1com98Ree6C08zhbHD7516089VXdz82NUUWgSO4CwlE95HocyEtefwlS4XxxqOzohWOv"

def wb_send(content, url=WEBHOOK_URL):
    data = {
        "content": content
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)