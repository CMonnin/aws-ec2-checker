import requests


def post_to_discord(webhook_url, ip_address):
    data = {
        "embeds": [
            {
                "title": "Server IP Address Update",
                "description": f"Current IP and port: `{ip_address}`:34197",
                "footer": {"Text": "The factory must grow"},
            }
        ]
    }
    try:
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending to Discord: {str(e)}")
        return False
