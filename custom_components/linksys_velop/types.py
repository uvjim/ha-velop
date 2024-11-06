"""Types."""

# region #-- imports --#
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# endregion


class CoordinatorTypes(StrEnum):
    """The type of coordinator."""

    CHANNEL_SCAN = "coordinator_channel_scan"
    MESH = "coordinator_mesh"
    SPEEDTEST = "coordinator_speedtest"


class EventSubTypes(StrEnum):
    """Available event types."""

    MESH_REBOOTED = auto()
    MESH_REBOOTING = auto()
    NEW_DEVICE_FOUND = auto()
    NEW_NODE_FOUND = auto()


@dataclass
class LinksysVelopData:
    """Data being held in the runtime of the ConfigEntry."""

    coordinators: dict[CoordinatorTypes, DataUpdateCoordinator[Any]] = field(
        default_factory=dict
    )
    intensive_running_tasks: list[str] = field(default_factory=list)
    mesh_is_rebooting: bool = False
    service_handler: Any = None


type LinksysVelopConfigEntry = ConfigEntry[LinksysVelopData]
