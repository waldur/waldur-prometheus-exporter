import os
from time import sleep

from prometheus_client import Gauge, start_http_server
from waldur_client import WaldurClient

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
        users_total.set(client.count_users())
        customers_total.set(client.count_customers())
        resources_total.set(client.count_marketplace_resources())
        projects_total.set(client.count_projects())

        sleep(10.0)
