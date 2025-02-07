"""Diagnostics support for Linksys Velop."""

# region #-- imports --#
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from homeassistant.components.diagnostics import REDACTED, async_redact_data
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from pyvelop.mesh import Mesh, Node

from .helpers import get_mesh_device_for_config_entry
from .types import LinksysVelopConfigEntry

# endregion


ATTR_REDACT: Iterable = {
    CONF_PASSWORD,
    "macAddress",
    "apBSSID",
    "stationBSSID",
    "serialNumber",
    "unique_id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: LinksysVelopConfigEntry
) -> dict[str, Any]:
    """Diagnostics for the config entry."""
    mesh: Mesh = config_entry.runtime_data.mesh
    mesh_attributes: dict = getattr(mesh, "_mesh_attributes")

    # region #-- unwanted attributes --#
    exclude_props: list[str] = ["devices"]
    # endregion

    # region #-- create generic details --#
    ret: dict[str, Any] = {
        "config_entry": config_entry.as_dict(),  # get the config entry details
        "mesh_details": {  # get mesh details
            key: mesh_attributes.get(key)
            for key in mesh_attributes
            if key not in exclude_props
        },
        "nodes": [node.__dict__ for node in mesh.nodes],
        "devices": [device.__dict__ for device in mesh.devices],
    }
    # endregion

    # region #-- redact additional buried data --#
    if (
        ret.get("mesh_details", {})
        .get("wan_info", {})
        .get("wanConnection", {})
        .get("ipAddress")
    ):
        ret["mesh_details"]["wan_info"]["wanConnection"]["ipAddress"] = REDACTED
    if (
        ret.get("mesh_details", {})
        .get("wan_info", {})
        .get("wanConnection", {})
        .get("gateway")
    ):
        ret["mesh_details"]["wan_info"]["wanConnection"]["gateway"] = REDACTED
    if ret.get("mesh_details", {}).get("guest_network", {}).get("radios", []):
        keys = ("guestWPAPassphrase", "guestSSID")
        for idx, _ in enumerate(
            ret.get("mesh_details", {}).get("guest_network", {}).get("radios", [])
        ):
            for k in keys:
                ret["mesh_details"]["guest_network"]["radios"][idx][k] = REDACTED
    # endregion

    return async_redact_data(
        ret,
        ATTR_REDACT,
    )


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: LinksysVelopConfigEntry, device: DeviceEntry
):
    """Diagnostics for a specific device.

    N.B. If the device is the Mesh then data for the ConfigEntry diagnostics is returned
    """
    if get_mesh_device_for_config_entry(hass, config_entry) == device:
        return await async_get_config_entry_diagnostics(hass, config_entry)

    mesh: Mesh = config_entry.runtime_data.mesh

    ret: dict[str, Any] = {
        "device_entry": {
            p: getattr(device, p, None)
            for p in [prop for prop in dir(DeviceEntry) if not prop.startswith("_")]
        }
    }

    node: list[Node] = [
        n
        for n in mesh.nodes
        if mesh.nodes and n.serial == next(iter(device.identifiers))[1]
    ]
    if node:
        ret["node"] = node[0].__dict__

    ret = async_redact_data(ret, ATTR_REDACT.union({"identifiers"}))

    return ret
