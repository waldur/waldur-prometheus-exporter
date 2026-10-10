"""Matrix chat health from the diagnostics endpoint, and rooms per state."""

from collections.abc import Iterator
from dataclasses import dataclass, field

import structlog
from prometheus_client.core import GaugeMetricFamily
from waldur_api_client.api.admin import admin_matrix_diagnostics_retrieve
from waldur_api_client.api.matrix import matrix_rooms_count
from waldur_api_client.client import AuthenticatedClient
from waldur_api_client.errors import UnexpectedStatus
from waldur_api_client.models.matrix_room_state_enum import MatrixRoomStateEnum

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class Snapshot:
    up: bool
    checks: dict[str, bool] = field(default_factory=dict)
    rooms: dict[str, int] = field(default_factory=dict)


def count_rooms(client: AuthenticatedClient) -> dict[str, int]:
    return {
        state.value: matrix_rooms_count.sync(client=client, state=state)
        for state in MatrixRoomStateEnum
    }


def describe_failure(error: Exception) -> str:
    if isinstance(error, UnexpectedStatus):
        if error.status_code == 403:
            return "HTTP 403: the API token's user is not staff or support"
        return f"HTTP {error.status_code}"
    return f"{type(error).__name__}: {error}"


class MatrixCollector:
    """Publishes the last result.

    Only what the last calls returned is published, so a check or room count
    that is gone, or a call that failed, leaves no value behind from an earlier
    one.
    """

    def __init__(self) -> None:
        # Replaced whole, never changed in place: the HTTP server thread reads
        # it while the main loop updates it.
        self._snapshot: Snapshot | None = None
        self._problems: dict[str, str] = {}

    def update(self, client: AuthenticatedClient) -> None:
        # Runs outside the loop's error handling, so nothing may escape it.
        try:
            diagnostics = admin_matrix_diagnostics_retrieve.sync(client=client)
            checks = {check.name: check.ok for check in diagnostics.checks}
        except Exception as e:
            self._snapshot = Snapshot(up=False)
            self._log_problems({"diagnostics": describe_failure(e)})
            return

        # Counted only once diagnostics succeeded: it answers staff and support
        # alone, the users the room list shows every room to. Any other token
        # would count only its own user's rooms.
        problems = {}
        try:
            rooms = count_rooms(client)
        except Exception as e:
            rooms = {}
            problems["rooms"] = describe_failure(e)

        self._snapshot = Snapshot(True, checks, rooms)
        self._log_problems(problems)

    # The exporter calls every 120 s; a lasting failure, such as a token that is
    # neither staff nor support, is logged when it starts or changes, not on
    # every call.
    def _log_problems(self, problems: dict[str, str]) -> None:
        for source, error in problems.items():
            if self._problems.get(source) != error:
                logger.warning(
                    "Unable to collect Matrix metrics", source=source, error=error
                )
        if self._problems and not problems:
            logger.info("Matrix metrics collected again")
        self._problems = problems

    def collect(self) -> Iterator[GaugeMetricFamily]:
        snapshot = self._snapshot
        if snapshot is None:
            return

        yield GaugeMetricFamily(
            "waldur_matrix_diagnostics_up",
            "1 if the last Matrix diagnostics call succeeded, 0 if it failed",
            value=int(snapshot.up),
        )

        checks = GaugeMetricFamily(
            "waldur_matrix_check_passed",
            "Matrix diagnostics check result: 1 passed, 0 failed",
            labels=["check"],
        )
        for name, ok in snapshot.checks.items():
            checks.add_metric([name], int(ok))
        yield checks

        rooms = GaugeMetricFamily(
            "waldur_matrix_rooms",
            "Matrix rooms per state",
            labels=["state"],
        )
        for state, count in snapshot.rooms.items():
            rooms.add_metric([state], count)
        yield rooms
