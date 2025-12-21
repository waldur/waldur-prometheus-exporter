import logging
import os
import sys
from time import sleep

from prometheus_client import Gauge, start_http_server
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
    marketplace_stats_resource_provisioning_stats_list,
    marketplace_stats_resources_limits_list,
    marketplace_stats_total_cost_of_active_resources_per_offering_list,
    marketplace_stats_user_affiliation_count_list,
    marketplace_stats_user_auth_method_count_list,
    marketplace_stats_user_identity_source_count_list,
    marketplace_stats_user_organization_count_list,
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
    waldur_marketplace_resources_total = Gauge(
        "waldur_marketplace_resources_total",
        "Total count of active resources",
    )

    waldur_user_auth_method_count = Gauge(
        "waldur_user_auth_method_count",
        "Total count of users by authentication method",
        ["method"],
    )

    waldur_user_identity_source_count = Gauge(
        "waldur_user_identity_source_count",
        "Total count of users by identity source",
        ["identity_source"],
    )

    waldur_user_organization_count = Gauge(
        "waldur_user_organization_count",
        "Total count of users by organization",
        ["organization"],
    )

    waldur_user_affiliation_count = Gauge(
        "waldur_user_affiliation_count",
        "Total count of users by affiliation",
        ["affiliation"],
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

    provisioning_count = Gauge(
        "provisioning_count",
        "Total finished provisioning attempts (DONE + ERRED)",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
        ],
    )
    provisioning_success_count = Gauge(
        "provisioning_success_count",
        "Total successful provisioning attempts (DONE)",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
        ],
    )
    provisioning_error_count = Gauge(
        "provisioning_error_count",
        "Total failed provisioning attempts (ERRED)",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
        ],
    )
    provisioning_in_progress_count = Gauge(
        "provisioning_in_progress_count",
        "Total currently in-progress provisioning attempts",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
        ],
    )
    provisioning_success_rate = Gauge(
        "provisioning_success_rate",
        "Rate of successful provisioning (0.0 to 1.0)",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
        ],
    )
    avg_provisioning_duration = Gauge(
        "avg_provisioning_duration",
        "Average duration in seconds from Executing to Terminal state",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
        ],
    )
    avg_pending_duration = Gauge(
        "avg_pending_duration",
        "Average duration in seconds from Creation to Executing state",
        [
            "offering_uuid",
            "offering_name",
            "service_provider_uuid",
            "service_provider_name",
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
            roles = roles_list.sync_all(client=client)
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

            logger.info("Collecting organization_project_count")
            for org_proj in (
                marketplace_stats_organization_project_count_list.sync(client=client)
                or []
            ):
                organization_project_count.labels(
                    org_proj.abbreviation, org_proj.name, org_proj.uuid
                ).set(org_proj.count)

            logger.info("Collecting organization_resource_count")
            for org_res in (
                marketplace_stats_organization_resource_count_list.sync(client=client)
                or []
            ):
                organization_resource_count.labels(
                    org_res.abbreviation,
                    org_res.name,
                    org_res.uuid,
                ).set(org_res.count)

            logger.info("Collecting organization_members_count")
            for member_count_stat in (
                marketplace_stats_customer_member_count_list.sync(client=client) or []
            ):
                member_count = member_count_stat.count or 0
                organization_members_count.labels(
                    member_count_stat.abbreviation,
                    member_count_stat.name,
                    member_count_stat.uuid,
                    member_count_stat.has_resources,
                ).set(member_count)

            logger.info("Collecting resources_limits")
            for limit in (
                marketplace_stats_resources_limits_list.sync(client=client) or []
            ):
                resources_limits.labels(
                    limit.offering_uuid,
                    limit.offering_country,
                    limit.organization_group_name,
                    limit.organization_group_uuid,
                    limit.name,
                ).set(limit.value)

            logger.info("Collecting aggregated_usages")
            for usage in (
                marketplace_stats_component_usages_list.sync(client=client) or []
            ):
                aggregated_usages.labels(
                    usage.offering_uuid,
                    usage.offering_country,
                    usage.organization_group_name,
                    usage.organization_group_uuid,
                    usage.component_type,
                ).set(usage.usage)

            logger.info("Collecting component_usages_per_project")
            for proj_usage in (
                marketplace_stats_component_usages_per_project_list.sync(client=client)
                or []
            ):
                component_usages_per_project.labels(
                    proj_usage.project_uuid,
                    proj_usage.component_type,
                ).set(proj_usage.usage)

            logger.info("Collecting aggregated_usages_per_month")
            for monthly_usage in (
                marketplace_stats_component_usages_per_month_list.sync_all(
                    client=client,
                )
                or []
            ):
                aggregated_usages_per_month.labels(
                    monthly_usage.offering_uuid,
                    monthly_usage.offering_country,
                    monthly_usage.organization_group_name,
                    monthly_usage.organization_group_uuid,
                    monthly_usage.component_type,
                    monthly_usage.month,
                    monthly_usage.year,
                ).set(monthly_usage.usage)

            logger.info("Collecting count_users_of_service_provider")
            for sp_user in (
                marketplace_stats_count_users_of_service_providers_list.sync(
                    client=client
                )
                or []
            ):
                count_users_of_service_provider.labels(
                    sp_user.service_provider_uuid,
                    sp_user.customer_uuid,
                    sp_user.customer_name,
                    sp_user.customer_organization_group_uuid,
                    sp_user.customer_organization_group_name,
                ).set(sp_user.count)

            logger.info("Collecting count_projects_of_service_provider")
            for sp_proj in (
                marketplace_stats_count_projects_of_service_providers_list.sync(
                    client=client
                )
                or []
            ):
                count_projects_of_service_provider.labels(
                    sp_proj.service_provider_uuid,
                    sp_proj.customer_uuid,
                    sp_proj.customer_name,
                    sp_proj.customer_organization_group_uuid,
                    sp_proj.customer_organization_group_name,
                ).set(sp_proj.count)

            logger.info("Collecting count_projects_of_service_provider_grouped_by_oecd")
            for sp_proj_oecd in (
                marketplace_stats_count_projects_of_service_providers_grouped_by_oecd_list.sync(
                    client=client
                )
                or []
            ):
                count_projects_of_service_provider_grouped_by_oecd.labels(
                    sp_proj_oecd.service_provider_uuid,
                    sp_proj_oecd.customer_uuid,
                    sp_proj_oecd.customer_name,
                    sp_proj_oecd.customer_organization_group_uuid,
                    sp_proj_oecd.customer_organization_group_name,
                    sp_proj_oecd.oecd_fos_2007_name,
                ).set(sp_proj_oecd.count)

            logger.info("Collecting total_cost_of_active_resources_per_offering")
            for cost_stat in (
                marketplace_stats_total_cost_of_active_resources_per_offering_list.sync(
                    client=client
                )
                or []
            ):
                total_cost_of_active_resources_per_offering.labels(
                    cost_stat.offering_uuid,
                ).set(cost_stat.cost)

            logger.info("Collecting offerings_counter_stats")
            for counter in (
                marketplace_stats_offerings_counter_stats_list.sync(client=client) or []
            ):
                offerings_counter_stats.labels(
                    counter.service_provider_uuid,
                    counter.service_provider_name,
                    counter.category_uuid,
                    counter.category_title,
                ).set(counter.count)

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
            for unique_user in (
                marketplace_stats_count_unique_users_connected_with_active_resources_of_service_provider_list.sync(
                    client=client
                )
                or []
            ):
                count_unique_users_connected_with_active_resources.labels(
                    unique_user.customer_uuid,
                    unique_user.customer_name,
                ).set(unique_user.count_users)

            total_active_resources = 0

            logger.info("Collecting count_active_resources_grouped_by_offering")
            for active_res in (
                marketplace_stats_count_active_resources_grouped_by_offering_list.sync(
                    client=client
                )
                or []
            ):
                count_active_resources_grouped_by_offering.labels(
                    active_res.uuid,
                    active_res.name,
                    active_res.country,
                ).set(active_res.count)

                total_active_resources += active_res.count

            logger.info("Collecting waldur_marketplace_resources_total")
            waldur_marketplace_resources_total.set(total_active_resources)

            logger.info("Collecting count_active_resources_grouped_by_offering_country")
            for country_res in (
                marketplace_stats_count_active_resources_grouped_by_offering_country_list.sync(
                    client=client
                )
                or []
            ):
                count_active_resources_grouped_by_offering_country.labels(
                    country_res.country,
                ).set(country_res.count)

            logger.info(
                "Collecting count_active_resources_grouped_by_organization_group"
            )
            for group_res in (
                marketplace_stats_count_active_resources_grouped_by_organization_group_list.sync(
                    client=client
                )
                or []
            ):
                count_active_resources_grouped_by_organization_group.labels(
                    group_res.uuid,
                    group_res.name,
                ).set(group_res.count)
            logger.info("Collecting count_projects_grouped_by_provider_and_oecd")
            for proj_oecd in (
                marketplace_stats_count_projects_grouped_by_provider_and_oecd_list.sync(
                    client=client
                )
            ) or []:
                count_projects_grouped_by_provider_and_oecd.labels(
                    proj_oecd.uuid,
                    proj_oecd.name,
                    proj_oecd.abbreviation,
                    proj_oecd.oecd,
                ).set(proj_oecd.count)
            logger.info(
                "Collecting count_projects_grouped_by_provider_and_industry_flag"
            )
            for proj_ind in (
                marketplace_stats_count_projects_grouped_by_provider_and_industry_flag_list.sync(
                    client=client
                )
                or []
            ):
                count_projects_grouped_by_provider_and_industry_flag.labels(
                    proj_ind.uuid,
                    proj_ind.name,
                    proj_ind.abbreviation,
                    proj_ind.is_industry,
                ).set(proj_ind.count)

            logger.info("Collecting resource_provisioning_stats")
            for stat in (
                marketplace_stats_resource_provisioning_stats_list.sync(client=client)
                or []
            ):
                labels = (
                    stat.offering_uuid,
                    stat.offering_name,
                    stat.service_provider_uuid,
                    stat.service_provider_name,
                )
                provisioning_count.labels(*labels).set(stat.provisioning_count)
                provisioning_success_count.labels(*labels).set(
                    stat.provisioning_success_count
                )
                provisioning_error_count.labels(*labels).set(
                    stat.provisioning_error_count
                )
                provisioning_in_progress_count.labels(*labels).set(
                    stat.provisioning_in_progress_count
                )
                provisioning_success_rate.labels(*labels).set(
                    stat.provisioning_success_rate
                )
                avg_provisioning_duration.labels(*labels).set(
                    stat.avg_provisioning_duration
                )
                avg_pending_duration.labels(*labels).set(stat.avg_pending_duration)

            logger.info("Collecting waldur_user_auth_method_count")
            for auth_stat in (
                marketplace_stats_user_auth_method_count_list.sync(client=client) or []
            ):
                waldur_user_auth_method_count.labels(auth_stat.method).set(
                    auth_stat.count
                )

            logger.info("Collecting waldur_user_identity_source_count")
            for identity_stat in (
                marketplace_stats_user_identity_source_count_list.sync(client=client)
                or []
            ):
                waldur_user_identity_source_count.labels(
                    identity_stat.identity_source
                ).set(identity_stat.count)

            logger.info("Collecting waldur_user_organization_count")
            for org_stat in (
                marketplace_stats_user_organization_count_list.sync(client=client) or []
            ):
                waldur_user_organization_count.labels(org_stat.organization).set(
                    org_stat.count
                )

            logger.info("Collecting waldur_user_affiliation_count")
            for aff_stat in (
                marketplace_stats_user_affiliation_count_list.sync(client=client) or []
            ):
                waldur_user_affiliation_count.labels(aff_stat.affiliation).set(
                    aff_stat.count
                )

        except UnexpectedStatus as e:
            logger.error(f"Unable to collect metrics. Message: {e}")
        except Exception as e:
            logger.error(f"Unable to collect metrics. Exception: {e}")

        sleep(120)
