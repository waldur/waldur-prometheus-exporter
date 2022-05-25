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
        ["abbreviation", "name", "uuid", "has_resources"],
    )

    resources_limits = Gauge(
        "resources_limits",
        "Resources limits",
        [
            "offering_uuid",
            "offering_country",
            "division_name",
            "division_uuid",
            "limit_name",
        ],
    )

    aggregated_usages = Gauge(
        "aggregated_usages",
        "Aggregated usages",
        ["offering_uuid", "offering_country", "division_name", "division_uuid", "type"],
    )

    count_users_of_service_provider = Gauge(
        "count_users_of_service_provider",
        "Count of users visible to service provider.",
        [
            "service_provider_uuid",
            "customer_uuid",
            "customer_name",
            "customer_division_uuid",
            "customer_division_name",
        ],
    )

    count_projects_of_service_provider = Gauge(
        "count_projects_of_service_provider",
        "Count of projects visible to service provider.",
        [
            "service_provider_uuid",
            "customer_uuid",
            "customer_name",
            "customer_division_uuid",
            "customer_division_name",
        ],
    )

    count_projects_of_service_provider_grouped_by_oecd = Gauge(
        "count_projects_of_service_provider_grouped_by_oecd",
        "Count of projects visible to service provider and grouped by oecd.",
        [
            "service_provider_uuid",
            "customer_uuid",
            "customer_name",
            "customer_division_uuid",
            "customer_division_name",
            "oecd_code",
        ],
    )

    total_cost_of_active_resources_per_offering = Gauge(
        "total_cost_of_active_resources_per_offering",
        "Total cost of active resources per offering.",
        [
            "offering_uuid",
        ],
    )

    count_projects_grouped_by_oecd = Gauge(
        "count_projects_grouped_by_oecd",
        "Count projects grouped by oecd.",
        [
            "oecd_code",
        ],
    )

    projects_usages_grouped_by_oecd = Gauge(
        "projects_usages_grouped_by_oecd",
        "Projects usages grouped by oecd.",
        [
            "oecd_code",
            "type",
        ],
    )

    projects_limits_grouped_by_oecd = Gauge(
        "projects_limits_grouped_by_oecd",
        "Projects limits grouped by oecd.",
        [
            "oecd_code",
            "name",
        ],
    )

    count_projects_grouped_by_industry_flag = Gauge(
        "count_projects_grouped_by_industry_flag",
        "Count projects grouped by industry flag.",
        [
            "is_industry",
        ],
    )

    projects_usages_grouped_by_industry_flag = Gauge(
        "projects_usages_grouped_by_industry_flag",
        "Projects usages grouped by industry flag.",
        [
            "is_industry",
            "type",
        ],
    )

    projects_limits_grouped_by_industry_flag = Gauge(
        "projects_limits_grouped_by_industry_flag",
        "Projects limits grouped by industry flag.",
        [
            "is_industry",
            "name",
        ],
    )

    count_unique_users_connected_with_active_resources = Gauge(
        "count_unique_users_connected_with_active_resources_of_service_provider",
        "Count unique users connected with active resources of service_provider .",
        [
            "customer_uuid",
            "customer_name",
        ],
    )

    count_active_resources_grouped_by_offering = Gauge(
        "count_active_resources_grouped_by_offering",
        "Count active resources grouped by offering.",
        [
            "uuid",
            "name",
        ],
    )

    count_active_resources_grouped_by_offering_country = Gauge(
        "count_active_resources_grouped_by_offering_country",
        "Count active resources grouped by country.",
        [
            "country",
        ],
    )

    count_active_resources_grouped_by_division = Gauge(
        "count_active_resources_grouped_by_division",
        "Count active resources grouped by division.",
        [
            "uuid",
            "name",
        ],
    )

    while True:
        try:
            users_total.set(client.count_users())
            customers_total.set(client.count_customers())
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

            for c in client.get_marketplace_stats("customer_member_count"):
                organization_members_count.labels(
                    c["abbreviation"],
                    c["name"],
                    c["uuid"],
                    c["has_resources"],
                ).set(c["count"])

            for c in client.get_marketplace_stats("resources_limits"):
                resources_limits.labels(
                    c["offering_uuid"],
                    c["offering_country"],
                    c["division_name"],
                    c["division_uuid"],
                    c["name"],
                ).set(c["value"])

            for c in client.get_marketplace_stats("component_usages"):
                aggregated_usages.labels(
                    c["offering_uuid"],
                    c["offering_country"],
                    c["division_name"],
                    c["division_uuid"],
                    c["component_type"],
                ).set(c["usage"])

            for c in client.get_marketplace_stats("count_users_of_service_providers"):
                count_users_of_service_provider.labels(
                    c["service_provider_uuid"],
                    c["customer_uuid"],
                    c["customer_name"],
                    c["customer_division_uuid"],
                    c["customer_division_name"],
                ).set(c["count"])

            for c in client.get_marketplace_stats(
                "count_projects_of_service_providers"
            ):
                count_projects_of_service_provider.labels(
                    c["service_provider_uuid"],
                    c["customer_uuid"],
                    c["customer_name"],
                    c["customer_division_uuid"],
                    c["customer_division_name"],
                ).set(c["count"])

            for c in client.get_marketplace_stats(
                "count_projects_of_service_providers_grouped_by_oecd"
            ):
                count_projects_of_service_provider_grouped_by_oecd.labels(
                    c["service_provider_uuid"],
                    c["customer_uuid"],
                    c["customer_name"],
                    c["customer_division_uuid"],
                    c["customer_division_name"],
                    c["oecd_fos_2007_name"],
                ).set(c["count"])

            for c in client.get_marketplace_stats(
                "total_cost_of_active_resources_per_offering"
            ):
                total_cost_of_active_resources_per_offering.labels(
                    c["offering_uuid"],
                ).set(c["cost"])

            for c in client.get_marketplace_stats("count_projects_grouped_by_oecd"):
                count_projects_grouped_by_oecd.labels(
                    c["oecd_fos_2007_name"],
                ).set(c["count"])

            for code, usages in client.get_marketplace_stats(
                "projects_usages_grouped_by_oecd"
            ).items():
                for usage_type, usage in usages.items():
                    projects_usages_grouped_by_oecd.labels(
                        code,
                        usage_type,
                    ).set(usage)

            for code, limits in client.get_marketplace_stats(
                "projects_limits_grouped_by_oecd"
            ).items():
                for limit_name, limit in limits.items():
                    projects_limits_grouped_by_oecd.labels(
                        code,
                        limit_name,
                    ).set(limit)

            for c in client.get_marketplace_stats(
                "count_projects_grouped_by_industry_flag"
            ):
                count_projects_grouped_by_industry_flag.labels(
                    c["is_industry"],
                ).set(c["count"])

            for is_industry, usages in client.get_marketplace_stats(
                "projects_usages_grouped_by_industry_flag"
            ).items():
                for usage_type, usage in usages.items():
                    projects_usages_grouped_by_industry_flag.labels(
                        is_industry,
                        usage_type,
                    ).set(usage)

            for is_industry, limits in client.get_marketplace_stats(
                "projects_limits_grouped_by_industry_flag"
            ).items():
                for limit_name, limit in limits.items():
                    projects_limits_grouped_by_industry_flag.labels(
                        is_industry,
                        limit_name,
                    ).set(limit)

            for c in client.get_marketplace_stats(
                "count_unique_users_connected_with_active_resources_of_service_provider"
            ):
                count_unique_users_connected_with_active_resources.labels(
                    c["customer_uuid"],
                    c["customer_name"],
                ).set(c["count_users"])

            for c in client.get_marketplace_stats(
                "count_active_resources_grouped_by_offering"
            ):
                count_active_resources_grouped_by_offering.labels(
                    c["uuid"],
                    c["name"],
                ).set(c["count"])

            for c in client.get_marketplace_stats(
                "count_active_resources_grouped_by_offering_country"
            ):
                count_active_resources_grouped_by_offering_country.labels(
                    c["country"],
                ).set(c["count"])

            for c in client.get_marketplace_stats(
                "count_active_resources_grouped_by_division"
            ):
                count_active_resources_grouped_by_division.labels(
                    c["uuid"],
                    c["name"],
                ).set(c["count"])

        except WaldurClientException as e:
            logger.error(f"Unable to collect metrics. Message: {e}")
        except Exception as e:
            logger.error(f"Unable to collect metrics. Exception: {e}")

        sleep(120)
