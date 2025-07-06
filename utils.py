import requests
import json

def api_request (payload, API_KEY, API_URL):

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        # Send POST request
        response = requests.post(API_URL, json=payload, headers=headers)
        return json.dumps(response.json(), indent=2)
        
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except ValueError as e:
        return f"Failed to decode JSON response: {e}"