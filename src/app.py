import logging
import os
import sys
from time import sleep

from prometheus_client import Gauge, start_http_server
from waldur_api_client import models
from waldur_api_client.api.customers import customers_count
from waldur_api_client.api.marketplace_stats import (
    marketplace_stats_component_usages_list,
    marketplace_stats_component_usages_per_month_list,
    marketplace_stats_component_usages_per_project_list,
    marketplace_stats_count_active_resources_grouped_by_offering_country_list,
    marketplace_stats_count_active_resources_grouped_by_offering_list,
    marketplace_stats_count_active_resources_grouped_by_organization_group_list,
    marketplace_stats_count_projects_grouped_by_provider_and_industry_flag_list,
    marketplace_stats_count_projects_grouped_by_provider_and_oecd_list,
    marketplace_stats_count_projects_of_service_providers_grouped_by_oecd_list,
    marketplace_stats_count_projects_of_service_providers_list,
    marketplace_stats_count_unique_users_connected_with_active_resources_of_service_provider_list,
    marketplace_stats_count_users_of_service_providers_list,
    marketplace_stats_customer_member_count_list,
    marketplace_stats_offerings_counter_stats_list,
    marketplace_stats_organization_project_count_list,
    marketplace_stats_organization_resource_count_list,
    marketplace_stats_projects_limits_grouped_by_industry_flag_retrieve,
    marketplace_stats_projects_limits_grouped_by_oecd_retrieve,
    marketplace_stats_projects_usages_grouped_by_industry_flag_retrieve,
    marketplace_stats_projects_usages_grouped_by_oecd_retrieve,
    marketplace_stats_resources_limits_list,
    marketplace_stats_total_cost_of_active_resources_per_offering_list,
)
from waldur_api_client.api.projects import projects_count
from waldur_api_client.api.roles import roles_list
from waldur_api_client.api.users import users_count
from waldur_api_client.client import AuthenticatedClient
from waldur_api_client.errors import UnexpectedStatus

handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
formatter = logging.Formatter("[%(levelname)s] [%(asctime)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

WALDUR_API_URL = os.environ["WALDUR_API_URL"]
WALDUR_API_TOKEN = os.environ["WALDUR_API_TOKEN"]


if __name__ == "__main__":
    client = AuthenticatedClient(
        base_url=WALDUR_API_URL.rstrip("/api"),
        token=WALDUR_API_TOKEN,
    )
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
    waldur_marketplace_resources_total = Gauge(
        "waldur_marketplace_resources_total",
        "Total count of active resources",
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
            "organization_group_name",
            "organization_group_name_uuid",
            "limit_name",
        ],
    )

    aggregated_usages = Gauge(
        "aggregated_usages",
        "Aggregated usages",
        [
            "offering_uuid",
            "offering_country",
            "organization_group_name",
            "organization_group_uuid",
            "type",
        ],
    )

    component_usages_per_project = Gauge(
        "component_usages_per_project",
        "Component usages per project",
        ["project_uuid", "component_type"],
    )

    aggregated_usages_per_month = Gauge(
        "aggregated_usages_per_month",
        "Aggregated usages per month",
        [
            "offering_uuid",
            "offering_country",
            "organization_group_name",
            "organization_group_uuid",
            "type",
            "month",
            "year",
        ],
    )

    count_users_of_service_provider = Gauge(
        "count_users_of_service_provider",
        "Count of users visible to service provider.",
        [
            "service_provider_uuid",
            "customer_uuid",
            "customer_name",
            "customer_organization_group_uuid",
            "customer_organization_group_name",
        ],
    )

    count_projects_of_service_provider = Gauge(
        "count_projects_of_service_provider",
        "Count of projects visible to service provider.",
        [
            "service_provider_uuid",
            "customer_uuid",
            "customer_name",
            "customer_organization_group_uuid",
            "customer_organization_group_name",
        ],
    )

    count_projects_of_service_provider_grouped_by_oecd = Gauge(
        "count_projects_of_service_provider_grouped_by_oecd",
        "Count of projects visible to service provider and grouped by oecd.",
        [
            "service_provider_uuid",
            "customer_uuid",
            "customer_name",
            "customer_organization_group_uuid",
            "customer_organization_group_name",
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
            "country",
        ],
    )

    count_active_resources_grouped_by_offering_country = Gauge(
        "count_active_resources_grouped_by_offering_country",
        "Count active resources grouped by country.",
        [
            "country",
        ],
    )

    count_active_resources_grouped_by_organization_group = Gauge(
        "count_active_resources_grouped_by_organization_group",
        "Count active resources grouped by organization_group.",
        [
            "uuid",
            "name",
        ],
    )

    count_projects_grouped_by_provider_and_oecd = Gauge(
        "count_projects_grouped_by_provider_and_oecd",
        "Count projects with active resources grouped by provider and oecd",
        [
            "uuid",
            "name",
            "abbreviation",
            "oecd",
        ],
    )
    offerings_counter_stats = Gauge(
        "offerings_counter_stats",
        "Count of offerings grouped by service provider and category",
        [
            "service_provider_uuid",
            "service_provider_name",
            "category_uuid",
            "category_title",
        ],
    )
    count_projects_grouped_by_provider_and_industry_flag = Gauge(
        "count_projects_grouped_by_provider_and_industry_flag",
        "Count projects with active resources grouped by provider and industry flag",
        [
            "uuid",
            "name",
            "abbreviation",
            "is_industry",
        ],
    )

    while True:
        try:
            logger.info("Collecting metrics")

            logger.info("Collecting users_total")
            users_total.set(users_count.sync(client=client))

            logger.info("Collecting customers_total")
            customers_total.set(customers_count.sync(client=client))

            logger.info("Collecting projects_total")
            projects_total.set(projects_count.sync(client=client))

            logger.info("Collecting waldur_owners_users_total")
            roles: list[models.RoleDetails] | None = roles_list.sync(
                client=client, page_size=200
            )
            if roles:
                owners_count = [
                    role.users_count for role in roles if role.name == "CUSTOMER.OWNER"
                ]
                if owners_count:
                    waldur_owners_users_total.set(owners_count[0])

            logger.info("Collecting waldur_support_users_total")
            waldur_support_users_total.set(
                users_count.sync(client=client, is_support=True, is_active=True)
            )

            logger.info("Collecting waldur_local_users_total")
            waldur_local_users_total.set(
                users_count.sync(
                    client=client, registration_method="default", is_active=True
                )
            )

            logger.info("Collecting waldur_saml2_users_total")
            waldur_saml2_users_total.set(
                users_count.sync(
                    client=client, registration_method="saml2", is_active=True
                )
            )

            logger.info("Collecting waldur_tara_users_total")
            waldur_tara_users_total.set(
                users_count.sync(
                    client=client, registration_method="tara", is_active=True
                )
            )

            logger.info("Collecting waldur_eduteams_users_total")
            waldur_eduteams_users_total.set(
                users_count.sync(
                    client=client, registration_method="eduteams", is_active=True
                )
            )

            logger.info("Collecting organization_project_count")
            for c in (
                marketplace_stats_organization_project_count_list.sync(client=client)
                or []
            ):
                organization_project_count.labels(c.abbreviation, c.name, c.uuid).set(
                    c.count
                )

            logger.info("Collecting organization_resource_count")
            for c in (
                marketplace_stats_organization_resource_count_list.sync(client=client)
                or []
            ):
                organization_resource_count.labels(
                    c.abbreviation,
                    c.name,
                    c.uuid,
                ).set(c.count)

            logger.info("Collecting organization_members_count")
            for c in (
                marketplace_stats_customer_member_count_list.sync(client=client) or []
            ):
                member_count = c.count or 0
                organization_members_count.labels(
                    c.abbreviation,
                    c.name,
                    c.uuid,
                    c.has_resources,
                ).set(member_count)

            logger.info("Collecting resources_limits")
            for c in marketplace_stats_resources_limits_list.sync(client=client) or []:
                resources_limits.labels(
                    c.offering_uuid,
                    c.offering_country,
                    c.organization_group_name,
                    c.organization_group_uuid,
                    c.name,
                ).set(c.value)

            logger.info("Collecting aggregated_usages")
            for c in marketplace_stats_component_usages_list.sync(client=client) or []:
                aggregated_usages.labels(
                    c.offering_uuid,
                    c.offering_country,
                    c.organization_group_name,
                    c.organization_group_uuid,
                    c.component_type,
                ).set(c.usage)

            logger.info("Collecting component_usages_per_project")
            for c in (
                marketplace_stats_component_usages_per_project_list.sync(client=client)
                or []
            ):
                component_usages_per_project.labels(
                    c.project_uuid,
                    c.component_type,
                ).set(c.usage)

            logger.info("Collecting aggregated_usages_per_month")
            for c in (
                marketplace_stats_component_usages_per_month_list.sync(
                    client=client,
                    page_size=1000,
                )
                or []
            ):
                aggregated_usages_per_month.labels(
                    c.offering_uuid,
                    c.offering_country,
                    c.organization_group_name,
                    c.organization_group_uuid,
                    c.component_type,
                    c.month,
                    c.year,
                ).set(c.usage)

            logger.info("Collecting count_users_of_service_provider")
            for c in (
                marketplace_stats_count_users_of_service_providers_list.sync(
                    client=client
                )
                or []
            ):
                count_users_of_service_provider.labels(
                    c.service_provider_uuid,
                    c.customer_uuid,
                    c.customer_name,
                    c.customer_organization_group_uuid,
                    c.customer_organization_group_name,
                ).set(c.count)

            logger.info("Collecting count_projects_of_service_provider")
            for c in (
                marketplace_stats_count_projects_of_service_providers_list.sync(
                    client=client
                )
                or []
            ):
                count_projects_of_service_provider.labels(
                    c.service_provider_uuid,
                    c.customer_uuid,
                    c.customer_name,
                    c.customer_organization_group_uuid,
                    c.customer_organization_group_name,
                ).set(c.count)

            logger.info("Collecting count_projects_of_service_provider_grouped_by_oecd")
            for c in (
                marketplace_stats_count_projects_of_service_providers_grouped_by_oecd_list.sync(
                    client=client
                )
                or []
            ):
                count_projects_of_service_provider_grouped_by_oecd.labels(
                    c.service_provider_uuid,
                    c.customer_uuid,
                    c.customer_name,
                    c.customer_organization_group_uuid,
                    c.customer_organization_group_name,
                    c.oecd_fos_2007_name,
                ).set(c.count)

            logger.info("Collecting total_cost_of_active_resources_per_offering")
            for c in (
                marketplace_stats_total_cost_of_active_resources_per_offering_list.sync(
                    client=client
                )
                or []
            ):
                total_cost_of_active_resources_per_offering.labels(
                    c.offering_uuid,
                ).set(c.cost)

            logger.info("Collecting offerings_counter_stats")
            for c in (
                marketplace_stats_offerings_counter_stats_list.sync(client=client) or []
            ):
                offerings_counter_stats.labels(
                    c.service_provider_uuid,
                    c.service_provider_name,
                    c.category_uuid,
                    c.category_title,
                ).set(c.count)

            logger.info("Collecting projects_usages_grouped_by_oecd")
            result = marketplace_stats_projects_usages_grouped_by_oecd_retrieve.sync(
                client=client
            )
            usages = result.usages.to_dict() if result else {}

            for code, usage_data in usages.items():
                for usage_type, usage in usage_data.items():
                    projects_usages_grouped_by_oecd.labels(
                        code,
                        usage_type,
                    ).set(usage)

            logger.info("Collecting projects_limits_grouped_by_oecd")
            usage_data = (
                marketplace_stats_projects_limits_grouped_by_oecd_retrieve.sync(
                    client=client
                )
            )
            limit_oecd_usages = usage_data.limits.to_dict() if usage_data else {}
            for code, limits in limit_oecd_usages.items():
                for limit_name, limit in limits.items():
                    projects_limits_grouped_by_oecd.labels(
                        code,
                        limit_name,
                    ).set(limit)
            logger.info("Collecting projects_usages_grouped_by_industry_flag")

            usage_data_proj_by_flag = marketplace_stats_projects_usages_grouped_by_industry_flag_retrieve.sync(
                client=client
            )
            project_flag_usages = (
                usage_data_proj_by_flag.usages.to_dict()
                if usage_data_proj_by_flag
                else {}
            )
            for is_industry, usages in project_flag_usages.items():
                for usage_type, usage in usages.items():
                    projects_usages_grouped_by_industry_flag.labels(
                        is_industry,
                        usage_type,
                    ).set(usage)

            logger.info("Collecting projects_limits_grouped_by_industry_flag")
            usage_data = marketplace_stats_projects_limits_grouped_by_industry_flag_retrieve.sync(
                client=client
            )
            limit_flag_usages = usage_data.limits.to_dict() if usage_data else {}
            for is_industry, limits in limit_flag_usages.items():
                for limit_name, limit in limits.items():
                    projects_limits_grouped_by_industry_flag.labels(
                        is_industry,
                        limit_name,
                    ).set(limit)

            logger.info("Collecting count_unique_users_connected_with_active_resources")
            for c in (
                marketplace_stats_count_unique_users_connected_with_active_resources_of_service_provider_list.sync(
                    client=client
                )
                or []
            ):
                count_unique_users_connected_with_active_resources.labels(
                    c.customer_uuid,
                    c.customer_name,
                ).set(c.count_users)

            total_active_resources = 0

            logger.info("Collecting count_active_resources_grouped_by_offering")
            for c in (
                marketplace_stats_count_active_resources_grouped_by_offering_list.sync(
                    client=client
                )
                or []
            ):
                count_active_resources_grouped_by_offering.labels(
                    c.uuid,
                    c.name,
                    c.country,
                ).set(c.count)

                total_active_resources += c.count

            logger.info("Collecting waldur_marketplace_resources_total")
            waldur_marketplace_resources_total.set(total_active_resources)

            logger.info("Collecting count_active_resources_grouped_by_offering_country")
            for c in (
                marketplace_stats_count_active_resources_grouped_by_offering_country_list.sync(
                    client=client
                )
                or []
            ):
                count_active_resources_grouped_by_offering_country.labels(
                    c.country,
                ).set(c.count)

            logger.info(
                "Collecting count_active_resources_grouped_by_organization_group"
            )
            for c in (
                marketplace_stats_count_active_resources_grouped_by_organization_group_list.sync(
                    client=client
                )
                or []
            ):
                count_active_resources_grouped_by_organization_group.labels(
                    c.uuid,
                    c.name,
                ).set(c.count)
            logger.info("Collecting count_projects_grouped_by_provider_and_oecd")
            for c in (
                marketplace_stats_count_projects_grouped_by_provider_and_oecd_list.sync(
                    client=client
                )
            ) or []:
                count_projects_grouped_by_provider_and_oecd.labels(
                    c.uuid,
                    c.name,
                    c.abbreviation,
                    c.oecd,
                ).set(c.count)
            logger.info(
                "Collecting count_projects_grouped_by_provider_and_industry_flag"
            )
            for c in (
                marketplace_stats_count_projects_grouped_by_provider_and_industry_flag_list.sync(
                    client=client
                )
                or []
            ):
                count_projects_grouped_by_provider_and_industry_flag.labels(
                    c.uuid,
                    c.name,
                    c.abbreviation,
                    c.is_industry,
                ).set(c.count)

        except UnexpectedStatus as e:
            logger.error(f"Unable to collect metrics. Message: {e}")
        except Exception as e:
            logger.error(f"Unable to collect metrics. Exception: {e}")

        sleep(120)
