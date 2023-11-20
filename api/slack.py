import requests
import json
from api.config import settings


# Define the webhook URL
webhook_url = settings.slack_webhook_url




# Convert the message into JSON


def send_notification(data):
    message = {
        "text": data,
        "usename": "FreshBooks"
    }
    
    message_json = json.dumps(message)


    # Send the POST request
    response = requests.post(webhook_url, data=message_json, headers={"Content-Type": "application/json"})
    print(webhook_url)
    print('slack response')
    print(response.status_code, response.content)
