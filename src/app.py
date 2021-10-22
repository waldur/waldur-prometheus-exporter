import logging
import os
from time import sleep

from prometheus_client import Gauge, start_http_server
from waldur_client import WaldurClient, WaldurClientException

handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
formatter = logging.Formatter("[%(levelname)s] [%(asctime)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

WALDUR_API_URL = os.environ["WALDUR_API_URL"]
WALDUR_API_TOKEN = os.environ["WALDUR_API_TOKEN"]


if __name__ == "__main__":
    client = WaldurClient(WALDUR_API_URL, WALDUR_API_TOKEN)
    start_http_server(8080)

    users_total = Gauge("waldur_users_total", "Total count of users in Waldur instance")
    customers_total = Gauge(
        "waldur_customers_total", "Total count of organizations in Waldur instance"
    )
    resources_total = Gauge(
        "waldur_marketplace_resources_total",
        "Total count of marketplace resources in Waldur instance",
    )
    projects_total = Gauge(
        "waldur_projects_total", "Total count of projects in Waldur instance"
    )

    while True:
        try:
            users_count = client.count_users()
            customers_count = client.count_customers()
            marketplace_resources_count = client.count_marketplace_resources()
            projects_count = client.count_projects()

            users_total.set(users_count)
            customers_total.set(customers_count)
            resources_total.set(marketplace_resources_count)
            projects_total.set(projects_count)
            logger.info(f"Total count of users: {users_count}")
            logger.info(f"Total count of customers: {customers_count}")
            logger.info(
                f"Total count of marketplace_resources: {marketplace_resources_count}"
            )
            logger.info(f"Total count of projects: {projects_count}")
            print()
        except WaldurClientException as e:
            logger.error(f"Unable to collect metrics. Message: {e}")
        except Exception as e:
            logger.error(f"Unable to collect metrics. Exception: {e}")

        sleep(10.0)
