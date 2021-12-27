import logging
import os
import sys
from time import sleep

from prometheus_client import Gauge, start_http_server
from waldur_client import WaldurClient, WaldurClientException

handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
formatter = logging.Formatter("[%(levelname)s] [%(asctime)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

WALDUR_API_URL = os.environ["WALDUR_API_URL"]
WALDUR_API_TOKEN = os.environ["WALDUR_API_TOKEN"]


if __name__ == "__main__":
    client = WaldurClient(WALDUR_API_URL, WALDUR_API_TOKEN)
    start_http_server(8080)

    users_total = Gauge("waldur_users_total", "Total count of users")
    customers_total = Gauge("waldur_customers_total", "Total count of organizations")
    resources_total = Gauge(
        "waldur_marketplace_resources_total",
        "Total count of marketplace resources",
    )
    projects_total = Gauge("waldur_projects_total", "Total count of projects")
    waldur_owners_users_total = Gauge(
        "waldur_owners_users_total", "Total count of users with owner permissions"
    )
    waldur_support_users_total = Gauge(
        "waldur_support_users_total", "Total count of support users"
    )
    waldur_local_users_total = Gauge(
        "waldur_local_users_total",
        "Total count of users with local registration method",
    )
    waldur_saml2_users_total = Gauge(
        "waldur_saml2_users_total",
        "Total count of users with saml2 registration method",
    )
    waldur_tara_users_total = Gauge(
        "waldur_tara_users_total", "Total count of users with tara registration method"
    )
    waldur_eduteams_users_total = Gauge(
        "waldur_eduteams_users_total",
        "Total count of users with eduteams registration method",
    )

    organization_project_count = Gauge(
        "organization_project_count",
        "Count of projects for each organization.",
        ["abbreviation", "name", "uuid"],
    )

    organization_resource_count = Gauge(
        "organization_resource_count",
        "Count of resources for every organization.",
        ["abbreviation", "name", "uuid"],
    )

    organization_members_count = Gauge(
        "organization_members_count",
        "Count of members for every organization.",
        ["abbreviation", "name", "uuid"],
    )

    resources_limits = Gauge(
        "resources_limits",
        "Resources limits",
        ["offering_uuid", "name"],
    )

    aggregated_usages = Gauge(
        "aggregated_usages",
        "Aggregated usages",
        ["offering_uuid", "type"],
    )

    while True:
        try:
            users_total.set(client.count_users())
            customers_total.set(client.count_customers())
            resources_total.set(
                client.count_marketplace_resources(params={"state": "OK"})
            )
            projects_total.set(client.count_projects())
            waldur_owners_users_total.set(
                client.count_customer_permissions(params={"role": "owner"})
            )
            waldur_support_users_total.set(
                client.count_users(params={"is_support": "true", "is_active": "true"})
            )
            waldur_local_users_total.set(
                client.count_users(
                    params={"registration_method": "default", "is_active": "true"}
                )
            )
            waldur_saml2_users_total.set(
                client.count_users(
                    params={"registration_method": "saml2", "is_active": "true"}
                )
            )
            waldur_tara_users_total.set(
                client.count_users(
                    params={"registration_method": "tara", "is_active": "true"}
                )
            )
            waldur_eduteams_users_total.set(
                client.count_users(
                    params={"registration_method": "eduteams", "is_active": "true"}
                )
            )

            for c in client.get_marketplace_stats("organization_project_count"):
                organization_project_count.labels(
                    c["abbreviation"],
                    c["name"],
                    c["uuid"],
                ).set(c["count"])

            for c in client.get_marketplace_stats("organization_resource_count"):
                organization_resource_count.labels(
                    c["abbreviation"],
                    c["name"],
                    c["uuid"],
                ).set(c["count"])

            organization_members_count.clear()

            for c in client.get_marketplace_stats("customer_member_count"):
                organization_members_count.labels(
                    c["abbreviation"],
                    c["name"],
                    c["uuid"],
                ).inc(c["count"])

            for c in client.get_marketplace_stats("project_member_count"):
                organization_members_count.labels(
                    c["abbreviation"],
                    c["name"],
                    c["uuid"],
                ).inc(c["count"])

            for c in client.get_marketplace_stats("resources_limits"):
                resources_limits.labels(
                    c["offering_uuid"],
                    c["name"],
                ).set(c["value"])

            for c in client.get_marketplace_stats("component_usages"):
                aggregated_usages.labels(
                    c["offering_uuid"],
                    c["component_type"],
                ).set(c["usage"])

        except WaldurClientException as e:
            logger.error(f"Unable to collect metrics. Message: {e}")
        except Exception as e:
            logger.error(f"Unable to collect metrics. Exception: {e}")

        sleep(10)
