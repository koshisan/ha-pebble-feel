from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    async_discovered_service_info,
    BluetoothServiceInfoBleak,
)

from .const import DOMAIN, PF_SERVICE_UUID, CONF_POLL_INTERVAL


class PebbleFeelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        address = discovery_info.address
        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_user({"address": address, "name": discovery_info.name})

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get("name") or "Pebble Feel",
                data={"address": user_input["address"]},
                options={CONF_POLL_INTERVAL: user_input.get(CONF_POLL_INTERVAL, 30)},
            )

        discovered = [
            info
            for info in async_discovered_service_info(self.hass)
            if PF_SERVICE_UUID in info.service_uuids
        ]

        schema = vol.Schema(
            {
                vol.Required("address", default=discovered[0].address if discovered else ""): str,
                vol.Optional("name"): str,
                vol.Optional(CONF_POLL_INTERVAL, default=30): vol.Coerce(int),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
