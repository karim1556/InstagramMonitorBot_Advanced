import requests

def is_account_banned(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return True  # Banned/deactivated
    elif response.status_code == 200:
        return False  # Active
    return None  # Unknown