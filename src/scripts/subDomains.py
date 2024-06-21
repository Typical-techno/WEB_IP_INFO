# scripts/subDomains.py
import requests

def fetch_crt_data(domain: str):
    url = f"https://crt.sh/?q={domain}&output=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def get_unique_common_names(domain: str):
    data = fetch_crt_data(domain)
    common_names = [entry['common_name'] for entry in data if 'common_name' in entry]
    # Remove duplicates by converting the list to a set and back to a list
    unique_common_names = list(set(common_names))
    return unique_common_names
