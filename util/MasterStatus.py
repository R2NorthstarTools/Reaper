import requests

NS_MASTER_SERVER_URL = "https://northstar.tf/client/servers"


def IsMasterDown():
    try:
        ms_response = requests.get(NS_MASTER_SERVER_URL)
        if ms_response.status_code == 200:
            return False
        else:
            return True
    except requests.exceptions.RequestException as err:
        print(f"Encountered exception while requesting MS: {err}")
        return None
