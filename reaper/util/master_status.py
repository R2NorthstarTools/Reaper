import logging

import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

import requests

NS_MASTER_SERVER_URL = "https://northstar.tf/client/servers"


def is_master_down():
    try:
        ms_response = requests.get(NS_MASTER_SERVER_URL)
        if ms_response.status_code == 200:
            return False
        else:
            return True
    except requests.exceptions.RequestException as err:
        logger.warning(f"Encountered exception while requesting MS: {err}")
        return None
