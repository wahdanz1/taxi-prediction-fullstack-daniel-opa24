import requests 
from urllib.parse import urljoin

def read_api_endpoint(endpoint="/", base_url="http://127.0.0.1:8000"):
    # Add leading slash if missing
    if not endpoint.startswith('/'):
        endpoint = f"/{endpoint}"
    
    url = urljoin(base_url, endpoint)
    response = requests.get(url)
    return response
